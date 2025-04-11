from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.utils import timezone
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth import get_user_model
import requests
import os
import uuid
from datetime import timedelta

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate verification token
        verification_token = str(uuid.uuid4())
        user = serializer.save(
            verification_token=verification_token,
            token_created_at=timezone.now()
        )

        # Send email verification link using Brevo
        email_data = {
            "sender": {"name": os.getenv('BREVO_EMAIL_NAME'), "email": os.getenv('BREVO_EMAIL_FROM')},
            "to": [{"email": user.email, "name": user.username}],
            "subject": "Verify Your Email",
            "htmlContent": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #333; text-align: center;">Welcome to Our Platform!</h1>
                <p style="color: #666;">Dear {user.username},</p>
                <p style="color: #666;">Thank you for registering with us. To complete your registration, please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                <a href='{os.getenv('BACKEND_URL')}/api/verify-email/?id={user.id}&token={verification_token}'
                   style="background-color: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 4px;">
                   Verify Email Address
                </a>
                </div>
                <p style="color: #666;">If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="color: #666; word-break: break-all;">{os.getenv('BACKEND_URL')}/api/verify-email/?id={user.id}&token={verification_token}</p>
                <p style="color: #999; font-size: 12px;">This link will expire in 24 hours.</p>
            </div>
            """
        }
        response = requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={'api-key': os.getenv('BREVO_API_KEY')},
            json=email_data
        )

        if response.status_code == 201:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": "Failed to send verification email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            if not user.is_email_verified:
                return Response(
                    {"error": "Please verify your email first"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate tokens
            tokens = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmailView(APIView):
    def get(self, request):
        # Fetch query parameters
        user_id = request.query_params.get('id')
        token = request.query_params.get('token')

        # If query parameters are missing, check the request body
        if not user_id or not token:
            try:
                user_id = request.data.get('id')
                token = request.data.get('token')
            except AttributeError:
                # Handle case where request.data is not available (e.g., GET request without body)
                pass

        # Check if both 'id' and 'token' are provided
        if not user_id or not token:
            return Response(
                {"error": "Both 'id' and 'token' are required as query parameters or in the request body"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id, verification_token=token)
            
            # Check if token is expired (24 hours)
            if user.token_created_at < timezone.now() - timedelta(hours=24):
                return Response(
                    {"error": "Verification link has expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.is_email_verified = True
            user.verification_token = None
            user.token_created_at = None
            user.save()

            return Response(
                {"message": "Email verified successfully"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST
            )
    @permission_classes([IsAuthenticated])
    def post(self, request):
        user = request.user
        return Response({
            "is_verified": user.is_email_verified,
            "email": user.email
        })
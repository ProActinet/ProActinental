from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
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
            "htmlContent": f"<p>Click <a href='{os.getenv('FRONTEND_URL')}/verify-email/{user.id}/{verification_token}'>here</a> to verify your email.</p>"
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
            # Handle login success (you might want to return a token here)
            return Response({"message": "Login successful"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    def get(self, request):
        # Fetch query parameters
        user_id = request.query_params.get('id')
        token = request.query_params.get('token')

        if not user_id or not token:
            return Response(
                {"error": "Both 'id' and 'token' query parameters are required"},
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
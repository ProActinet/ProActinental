from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import LicenseKey
from .utils import generate_license_key
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class GenerateLicenseKeyView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access this endpoint
    throttle_scope = 'licenses' # Rate limiting scope to prevent abuse

    def post(self, request):
        try:
            user = request.user
            key = generate_license_key()

            # Create and save the license key
            license_key = LicenseKey.objects.create(user=user, key=key)
            return Response(
                {"license_key": license_key.key},
                status=status.HTTP_201_CREATED
            )

        except IntegrityError as e:
            return Response(
                {"error": "License key generation failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetLicenseKeysView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            license_keys = LicenseKey.objects.filter(user=user).values('key', 'created_at', 'is_active')
            return Response(
                {"license_keys": list(license_keys)},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Failed to retrieve license keys."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR # Server error
            )
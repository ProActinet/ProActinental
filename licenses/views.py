from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import LicenseKey
from .serializers import GenerateLicenseKeySerializer, LicenseKeySerializer
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class GenerateLicenseKeyView(APIView):
    """
    This view generates (or reuses) a unified license key for the authenticated user.
    Before associating MAC IDs with the license key, it validates that none of them
    are already registered with another user.
    """
    permission_classes = [IsAuthenticated]
    throttle_scope = 'licenses'

    def post(self, request, *args, **kwargs):
        serializer = GenerateLicenseKeySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                license_key = serializer.save()
                return Response(
                    {"license_key": license_key.key},
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {"error": "License key generation failed. Please try again."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception:
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetLicenseKeysView(APIView):
    """
    This view returns a list of license keys for the authenticated user,
    including their associated MAC IDs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        license_keys = LicenseKey.objects.filter(user=request.user)
        serializer = LicenseKeySerializer(license_keys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
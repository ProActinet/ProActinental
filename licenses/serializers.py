# serializers.py

from rest_framework import serializers
from .models import LicenseKey, LicenseMac
from .utils import generate_license_key

class LicenseMacSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseMac
        fields = ('mac_id', 'os')


class GenerateLicenseKeySerializer(serializers.Serializer):
    # Now expect a list of objects for mac_ids.
    mac_ids = LicenseMacSerializer(many=True, required=True, allow_empty=False)

    def validate_mac_ids(self, value):
        """
        Validate each MAC object: if a MAC ID is already registered to a license key
        owned by a different user, raise a validation error.
        """
        user = self.context['request'].user
        errors = {}
        for item in value:
            mac = item.get('mac_id')
            # Check if the mac already exists in any LicenseMac record.
            qs = LicenseMac.objects.filter(mac_id=mac)
            if qs.exists():
                existing_license_mac = qs.first()
                # If the MAC is registered with a license key that belongs to another user, record an error.
                if existing_license_mac.license_key.user != user:
                    errors[mac] = f"MAC ID {mac} is already registered with another user."
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        macs = validated_data.get('mac_ids')

        # Create or reuse the unified license key for this user.
        license_key, created = LicenseKey.objects.get_or_create(
            user=user,
            defaults={'key': generate_license_key(user.username)}
        )

        # Associate each provided MAC (with OS) with the license key.
        for item in macs:
            mac = item.get('mac_id')
            # If 'os' is not provided, default to 'unknown'
            os_value = item.get('os', 'unknown')
            LicenseMac.objects.get_or_create(
                license_key=license_key,
                mac_id=mac,
                defaults={'os': os_value}
            )
        return license_key

class LicenseKeySerializer(serializers.ModelSerializer):
    mac_ids = LicenseMacSerializer(many=True, read_only=True)
    
    class Meta:
        model = LicenseKey
        fields = ('key', 'created_at', 'is_active', 'mac_ids')
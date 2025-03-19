from django.db import models
from django.conf import settings

class LicenseKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='license_keys'
    )
    key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.key} (User: {self.user.email})"


class LicenseMac(models.Model):
    license_key = models.ForeignKey(
        LicenseKey, 
        on_delete=models.CASCADE, 
        related_name="mac_ids"
    )
    mac_id = models.CharField(max_length=50, unique=True)
    os = models.CharField(max_length=100, default='unknown')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MAC: {self.mac_id} (License: {self.license_key.key}) (OS: {self.os})"  
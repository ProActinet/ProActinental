# models.py
from django.db import models

class SuricataAlert(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    logs = models.JSONField()  # Assuming logs are stored in JSON format
    created_at = models.DateTimeField(auto_now_add=True)  # Optional timestamp
    updated_at = models.DateTimeField(auto_now=True)       # Optional timestamp

    class Meta:
        db_table = 'suricata_alerts'

    def __str__(self):
        return f"{self.username} - {self.email}"

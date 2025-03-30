from rest_framework import serializers
from .models import SuricataAlert
from datetime import datetime, timedelta
import pytz

class SuricataAlertSerializer(serializers.ModelSerializer):
    timestamps = serializers.SerializerMethodField()

    class Meta:
        model = SuricataAlert
        fields = ['id', 'username', 'email', 'timestamps']

    def get_timestamps(self, obj):
        logs = obj.logs if isinstance(obj.logs, list) else []

        # Get current time in UTC
        now = datetime.now(pytz.UTC)
        last_24_hours = now - timedelta(hours=24)

        # Filter timestamps within the last 24 hours
        recent_timestamps = []
        for log in logs:
            timestamp_str = log.get('timestamp')
            if timestamp_str:
                try:
                    log_time = datetime.fromisoformat(timestamp_str)
                    if log_time >= last_24_hours:
                        recent_timestamps.append(timestamp_str)
                except ValueError:
                    # Skip invalid timestamp formats
                    continue

        return recent_timestamps

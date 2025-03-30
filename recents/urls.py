from django.urls import path
from .views import recent_timestamps

urlpatterns = [
    path('api/timestamps/', recent_timestamps, name='recent-timestamps'),
]

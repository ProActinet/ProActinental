from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^wss/daemon-watcher/$', consumers.DaemonWatcherConsumer.as_asgi()),
    re_path(r'^wss/frontend-logs/$', consumers.FrontendLogConsumer.as_asgi()),
]

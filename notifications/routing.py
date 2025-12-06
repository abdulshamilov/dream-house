from django.urls import re_path
from . import consumers  # consumers.py нужно создать

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

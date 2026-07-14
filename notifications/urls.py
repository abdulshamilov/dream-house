from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationDeleteView,
    NotificationClearAllView,
    NotificationSettingsView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification_mark_all_read'),
    path('clear/', NotificationClearAllView.as_view(), name='notification_clear_all'),
    path('settings/', NotificationSettingsView.as_view(), name='notification_settings'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification_read'),
    path('<int:pk>/', NotificationDeleteView.as_view(), name='notification_delete'),
]

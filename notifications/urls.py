from django.urls import path
from .views import NotificationListView, NotificationMarkReadView, NotificationSettingsView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification_read'),
    path('settings/', NotificationSettingsView.as_view(), name='notification_settings'),
]

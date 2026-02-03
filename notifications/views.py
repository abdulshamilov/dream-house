from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Notification, NotificationSettings
from .serializers import NotificationSerializer, NotificationSettingsSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return (
            Notification.objects.filter(user=self.request.user)
            .select_related("card")
            .prefetch_related("card__images")
        )


class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)


class NotificationSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSettingsSerializer

    @extend_schema(responses=NotificationSettingsSerializer)
    def get(self, request):
        settings_obj, _ = NotificationSettings.objects.get_or_create(
            user=request.user, defaults={"enabled": True}
        )
        return Response(NotificationSettingsSerializer(settings_obj).data)

    @extend_schema(request=NotificationSettingsSerializer, responses=NotificationSettingsSerializer)
    def post(self, request):
        settings_obj, _ = NotificationSettings.objects.get_or_create(
            user=request.user, defaults={"enabled": True}
        )
        serializer = NotificationSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

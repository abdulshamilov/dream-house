from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Q

from .models import Notification, NotificationSettings
from .serializers import NotificationSerializer, NotificationSettingsSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        # Возвращаем как персональные уведомления пользователя, так и глобальные
        return (
            Notification.objects.filter(
                Q(user=self.request.user) | Q(is_global=True)
            )
            .select_related("card", "promotion")
            .prefetch_related("card__images")
            .distinct()
        )


class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        # Позволяем отмечать как прочитанные только персональные уведомления
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)


class NotificationMarkAllReadView(APIView):
    """Пометить все персональные уведомления пользователя прочитанными."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({"updated": updated})


class NotificationDeleteView(generics.DestroyAPIView):
    """Удалить одно уведомление (только своё персональное)."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)


class NotificationClearAllView(APIView):
    """Удалить все персональные уведомления пользователя разом."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def delete(self, request):
        deleted, _ = Notification.objects.filter(user=request.user).delete()
        return Response({"deleted": deleted})


class NotificationSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSettingsSerializer

    @extend_schema(responses=NotificationSettingsSerializer)
    def get(self, request):
        settings_obj, _ = NotificationSettings.objects.get_or_create(
            user=request.user
        )
        return Response(NotificationSettingsSerializer(settings_obj).data)

    @extend_schema(request=NotificationSettingsSerializer, responses=NotificationSettingsSerializer)
    def post(self, request):
        settings_obj, _ = NotificationSettings.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

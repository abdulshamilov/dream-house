from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Q, Exists, OuterRef
from django.shortcuts import get_object_or_404

from .models import Notification, NotificationSettings, NotificationUserState
from .serializers import NotificationSerializer, NotificationSettingsSerializer


def _visible_notifications(user):
    """Персональные уведомления пользователя + глобальные, которые он не скрыл."""
    return (
        Notification.objects.filter(Q(user=user) | Q(is_global=True))
        .exclude(user_states__user=user, user_states__is_hidden=True)
        .select_related("card", "promotion")
        .prefetch_related("card__images")
        .distinct()
    )


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        user = self.request.user
        # read_by_user — прочитанность глобального уведомления ЭТИМ
        # пользователем; сериализатор берёт её вместо общего is_read.
        return _visible_notifications(user).annotate(
            read_by_user=Exists(
                NotificationUserState.objects.filter(
                    notification=OuterRef("pk"), user=user, is_read=True
                )
            )
        )


class NotificationMarkReadView(APIView):
    """Пометить уведомление прочитанным (персональное или глобальное)."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=NotificationSerializer)
    def patch(self, request, pk):
        notification = get_object_or_404(_visible_notifications(request.user), pk=pk)
        if notification.user_id == request.user.id:
            if not notification.is_read:
                notification.is_read = True
                notification.save(update_fields=["is_read"])
        else:
            # Глобальное: прочитанность храним отдельно для каждого пользователя
            NotificationUserState.objects.update_or_create(
                user=request.user,
                notification=notification,
                defaults={"is_read": True},
            )
        serializer = NotificationSerializer(notification, context={"request": request})
        return Response(serializer.data)

    # Совместимость с клиентами, шлющими PUT
    def put(self, request, pk):
        return self.patch(request, pk)


class NotificationMarkAllReadView(APIView):
    """Пометить все уведомления пользователя прочитанными (включая глобальные)."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)

        unread_globals = Notification.objects.filter(is_global=True).exclude(
            user_states__user=request.user, user_states__is_read=True
        )
        for notification in unread_globals:
            _, created = NotificationUserState.objects.update_or_create(
                user=request.user,
                notification=notification,
                defaults={"is_read": True},
            )
            updated += 1
        return Response({"updated": updated})


class NotificationDeleteView(APIView):
    """Удалить уведомление: персональное — физически, глобальное — скрыть у себя."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, pk):
        notification = get_object_or_404(_visible_notifications(request.user), pk=pk)
        if notification.user_id == request.user.id:
            notification.delete()
        else:
            NotificationUserState.objects.update_or_create(
                user=request.user,
                notification=notification,
                defaults={"is_hidden": True},
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationClearAllView(APIView):
    """Очистить список: персональные удалить, глобальные скрыть у себя."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={200: None})
    def delete(self, request):
        deleted, _ = Notification.objects.filter(user=request.user).delete()

        visible_globals = Notification.objects.filter(is_global=True).exclude(
            user_states__user=request.user, user_states__is_hidden=True
        )
        for notification in visible_globals:
            NotificationUserState.objects.update_or_create(
                user=request.user,
                notification=notification,
                defaults={"is_hidden": True},
            )
            deleted += 1
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

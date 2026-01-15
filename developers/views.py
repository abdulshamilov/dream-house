from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Developer, Subscription
from .serializers import DeveloperSerializer, SubscriptionSerializer, SubscriptionListSerializer
from cards.models import Card
from cards.serializers import CardSerializer

# 🔹 Подписка / отписка через один endpoint
class SubscribeAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer  # for schema generation

    @extend_schema(
        summary="Подписка на застройщика",
        description="POST — подписка, DELETE — отписка. Возвращает сообщение и код состояния.",
        responses={
            201: {"application/json": {"example": {"detail": "Подписка оформлена"}}},
            200: {"application/json": {"example": {"detail": "Подписка отменена"}}},
            400: {"application/json": {"example": {"detail": "Уже подписан"}}},
        }
    )
    def post(self, request, developer_id):
        developer = get_object_or_404(Developer, id=developer_id)
        subscription, created = Subscription.objects.get_or_create(user=request.user, developer=developer)
        if not created:
            return Response({'detail': 'Уже подписан'}, status=400)
        return Response({'detail': 'Подписка оформлена'}, status=201)

    @extend_schema(
        summary="Отписка от застройщика",
        description="POST — подписка, DELETE — отписка. Возвращает сообщение и код состояния."
    )
    def delete(self, request, developer_id):
        developer = get_object_or_404(Developer, id=developer_id)
        deleted, _ = Subscription.objects.filter(user=request.user, developer=developer).delete()
        if deleted:
            return Response({'detail': 'Подписка отменена'}, status=200)
        return Response({'detail': 'Вы не были подписаны'}, status=400)

# 🔹 Список своих подписок
class MySubscriptionsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionListSerializer

    @extend_schema(
        summary="Список моих подписок",
        description="Возвращает всех застройщиков, на которых подписан текущий пользователь."
    )
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Subscription.objects.none()
        return Subscription.objects.filter(user=self.request.user).select_related('developer').order_by('-created_at')

# 🔹 Остальные стандартные view
class DeveloperListAPIView(generics.ListAPIView):
    serializer_class = DeveloperSerializer

    def get_queryset(self):
        qs = Developer.objects.all()
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            from django.db.models import Exists, OuterRef
            qs = qs.annotate(
                is_subscribed=Exists(
                    Subscription.objects.filter(user=user, developer_id=OuterRef('pk'))
                )
            )
        return qs

class DeveloperCardsAPIView(generics.ListAPIView):
    serializer_class = CardSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Card.objects.none()
        developer_id = self.kwargs['developer_id']
        return Card.objects.filter(developer_id=developer_id).select_related('owner').prefetch_related('images')

class DeveloperDetailView(generics.RetrieveAPIView):
    serializer_class = DeveloperSerializer
    queryset = Developer.objects.all()

    def retrieve(self, request, *args, **kwargs):
        developer = self.get_object()

        # Аннотация is_subscribed для точного флага
        if request.user.is_authenticated:
            developer.is_subscribed = Subscription.objects.filter(user=request.user, developer=developer).exists()
        else:
            developer.is_subscribed = False

        data = DeveloperSerializer(developer, context={'request': request}).data

        cards = Card.objects.filter(developer=developer).select_related('owner').prefetch_related('images')
        data['cards'] = CardSerializer(cards, many=True, context={'request': request}).data

        return Response(data)

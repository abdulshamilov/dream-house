from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Developer, Subscription
from .serializers import DeveloperSerializer, SubscriptionSerializer
from cards.models import Card
from cards.serializers import CardSerializer


# ✅ Получить всех застройщиков
class DeveloperListAPIView(generics.ListAPIView):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer


# ✅ Получить все ЖК (квартиры) застройщика с полными данными
class DeveloperCardsAPIView(generics.ListAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        developer_id = self.kwargs['developer_id']
        return Card.objects.filter(developer_id=developer_id).select_related('owner', 'city').prefetch_related('images')


# ✅ Подписаться или отписаться от застройщика
class SubscribeAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, developer_id):
        developer = get_object_or_404(Developer, id=developer_id)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            developer=developer
        )
        if not created:
            return Response({'detail': 'Уже подписан'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Подписка оформлена'}, status=status.HTTP_201_CREATED)

    def delete(self, request, developer_id):
        developer = get_object_or_404(Developer, id=developer_id)
        Subscription.objects.filter(user=request.user, developer=developer).delete()
        return Response({'detail': 'Подписка отменена'}, status=status.HTTP_204_NO_CONTENT)


# ✅ Получить все свои подписки
class MySubscriptionsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

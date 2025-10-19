from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Card
from .serializers import CardSerializer
from .filters import CardFilter

@extend_schema(
    tags=["Cards"],
    summary="Список всех карточек домов",
    description="Возвращает список всех карточек домов. Можно фильтровать по цене, комнатам, городу и типу дома."
)
class CardListView(generics.ListAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter

@extend_schema(
    tags=["Cards"],
    summary="Просмотр конкретной карточки",
    description="Возвращает данные одной карточки по ID."
)
class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

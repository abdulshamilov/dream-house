from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Card
from .serializers import CardSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=["Cards"],
    summary="Список всех карточек домов",
    description="Возвращает список всех карточек домов. JWT-токен не обязателен.",
)
class CardListView(generics.ListAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    tags=["Cards"],
    summary="Просмотр конкретной карточки",
    description="Возвращает данные одной карточки по ID."
)
class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

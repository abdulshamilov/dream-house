from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Card
from .serializers import CardSerializer
from .filters import CardFilter
from .serializers import CallRequestSerializer

# Сериализатор для оценки карточки
class RateCardSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

# Сериализатор для ответа после оценки
class RateCardResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    new_average = serializers.FloatField()
    total_votes = serializers.IntegerField()


@extend_schema(
    tags=["Cards"],
    summary="Список всех карточек домов",
    description="Возвращает список всех карточек домов. Можно фильтровать по цене, комнатам, городу и типу дома.",
    responses=CardSerializer(many=True)
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
    description="Возвращает данные одной карточки по ID.",
    responses=CardSerializer
)
class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=["Cards"],
    summary="Поставить оценку карточке",
    description="Позволяет пользователю поставить оценку от 1 до 5. Средний рейтинг пересчитывается автоматически.",
    request=RateCardSerializer,
    responses=RateCardResponseSerializer
)
class RateCardView(generics.GenericAPIView):
    queryset = Card.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            card = Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            return Response({"error": "Карточка не найдена"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RateCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.validated_data['rating']

        # Пересчёт среднего рейтинга
        total_rating = card.rating * card.rating_count
        card.rating_count += 1
        card.rating = (total_rating + rating) / card.rating_count
        card.save()

        response_data = {
            "message": "Оценка добавлена",
            "new_average": round(card.rating, 2),
            "total_votes": card.rating_count
        }

        return Response(response_data, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Cards"],
    summary="Оставить заявку на звонок",
    description=(
        "Создаёт заявку на звонок по конкретной карточке.\n\n"
        "Поля:\n"
        "- `card` — ID карточки\n"
        "- `name` — имя клиента\n"
        "- `phone_number` — номер телефона\n"
        "- `preferred_time` — удобное время для звонка (необязательно)"
    ),
    request=CallRequestSerializer,
    responses={
        201: {
            "application/json": {
                "example": {
                    "ok": True,
                    "code": "OK",
                    "reason": ""
                }
            }
        },
        400: {
            "application/json": {
                "example": {
                    "ok": False,
                    "code": "FAILED",
                    "reason": "INVALID_DATA"
                }
            }
        },
    }
)
class CallRequestCreateView(generics.CreateAPIView):
    serializer_class = CallRequestSerializer
    permission_classes = [permissions.AllowAny]

class CallRequestCreateView(generics.CreateAPIView):
    serializer_class = CallRequestSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        card_id = kwargs.get('pk')
        try:
            card = Card.objects.get(pk=card_id)
        except Card.DoesNotExist:
            return Response({"ok": False, "code": "FAILED", "reason": "CARD_NOT_FOUND"}, status=404)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(card=card)  # 🔹 привязываем карточку здесь
        return Response({"ok": True, "code": "OK", "reason": ""}, status=201)
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.db.models import Q

from .models import (
    Card, CardReview, CardQuestion, CardVideo, SearchHistory
)
from .serializers import (
    CardSerializer, CardReviewSerializer, CardQuestionSerializer,
    CardVideoSerializer, CallRequestSerializer
)
from .filters import CardFilter


# -------------------------------
# Сериализаторы рейтинга
# -------------------------------
class RateCardSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)


class RateCardResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    new_average = serializers.FloatField()
    total_votes = serializers.IntegerField()


# -------------------------------
# Список карточек
# -------------------------------
@extend_schema(
    summary="Получить список карточек",
    description="Возвращает список всех карточек недвижимости с поддержкой фильтров.",
    responses=CardSerializer
)
class CardListView(generics.ListAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter


# -------------------------------
# Детальная карточка
# -------------------------------
@extend_schema(
    summary="Получить подробную информацию о карточке",
    responses=CardSerializer
)
class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]


# -------------------------------
# Оценка карточки
# -------------------------------
@extend_schema(
    summary="Поставить оценку карточке",
    request=RateCardSerializer,
    responses={200: RateCardResponseSerializer}
)
class RateCardView(generics.GenericAPIView):
    queryset = Card.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            card = Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            return Response({"error": "Карточка не найдена"}, status=404)

        serializer = RateCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.validated_data['rating']

        total_rating = card.rating * card.rating_count
        card.rating_count += 1
        card.rating = (total_rating + rating) / card.rating_count
        card.save()

        return Response({
            "message": "Оценка добавлена",
            "new_average": round(card.rating, 2),
            "total_votes": card.rating_count
        })


# -------------------------------
# Создание заявки на звонок
# -------------------------------
@extend_schema(
    summary="Оставить заявку на звонок",
    request=CallRequestSerializer,
    responses={201: OpenApiResponse(description="Создано"), 404: OpenApiResponse(description="Карточка не найдена")}
)
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
        serializer.save(card=card)
        return Response({"ok": True, "code": "OK"}, status=201)


# -------------------------------
# Добавление видео
# -------------------------------
@extend_schema(
    summary="Добавить видео к карточке",
    request=CardVideoSerializer,
    responses=CardVideoSerializer
)
class CardVideoCreateView(generics.CreateAPIView):
    serializer_class = CardVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card)


# -------------------------------
# Добавление отзыва
# -------------------------------
@extend_schema(
    summary="Добавить отзыв",
    request=CardReviewSerializer,
    responses=CardReviewSerializer
)
class CardReviewCreateView(generics.CreateAPIView):
    serializer_class = CardReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card, user=self.request.user)


# -------------------------------
# Добавление вопроса
# -------------------------------
@extend_schema(
    summary="Добавить вопрос",
    request=CardQuestionSerializer,
    responses=CardQuestionSerializer
)
class CardQuestionCreateView(generics.CreateAPIView):
    serializer_class = CardQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card, user=self.request.user)


# -------------------------------
# Получение отзыва по id
# -------------------------------
@extend_schema(
    summary="Получить отзыв по ID",
    responses=CardReviewSerializer
)
class CardReviewDetailView(generics.RetrieveAPIView):
    queryset = CardReview.objects.all()
    serializer_class = CardReviewSerializer
    lookup_field = "id"


# -------------------------------
# Получение вопроса по id
# -------------------------------
@extend_schema(
    summary="Получить вопрос по ID",
    responses=CardQuestionSerializer
)
class CardQuestionDetailView(generics.RetrieveAPIView):
    queryset = CardQuestion.objects.all()
    serializer_class = CardQuestionSerializer
    lookup_field = "id"


# -------------------------------
# Поиск карточек + история поиска
# -------------------------------
@extend_schema(
    summary="Поиск карточек",
    description="Ищет по названию и описанию. История сохраняется для авторизованных пользователей.",
    parameters=[
        OpenApiParameter(name="q", description="Поисковый запрос", required=False, type=str)
    ],
    responses=CardSerializer(many=True)
)
class CardSearchView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get("q", "")

        if query and self.request.user.is_authenticated:
            SearchHistory.objects.create(user=self.request.user, query=query)

        return Card.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

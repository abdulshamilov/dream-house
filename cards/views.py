from rest_framework import generics, permissions, status, serializers, views
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import get_object_or_404 

from .models import (
    Card, CardReview, CardQuestion, CardVideo, SearchHistory,
    Favorite 
)
from .serializers import (
    CardSerializer,
    CardReviewSerializer,
    CardQuestionSerializer,
    CardVideoSerializer,
    CallRequestSerializer,
    FavoriteSerializer, 
)
from .filters import CardFilter


# -------------------------------
# Сериализаторы рейтинга (Оставлены для полноты)
# -------------------------------
class RateCardSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

class RateCardResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    new_average = serializers.FloatField()
    total_votes = serializers.IntegerField()


# -------------------------------
# 1. Список карточек (GET /api/cards/)
# -------------------------------
@extend_schema(
    summary="Получить список карточек",
    description="Возвращает список всех карточек недвижимости с поддержкой фильтров.",
    responses=CardSerializer(many=True)
)
class CardListView(generics.ListAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter
    
    # 🔑 ВАЖНО: Передаем объект запроса в контекст сериализатора, 
    # чтобы работал is_favorite
    def get_serializer_context(self):
        return {'request': self.request}


# -------------------------------
# 2. ФИЛЬТРАЦИЯ КАРТОЧЕК (POST /api/cards/filter/)
# -------------------------------
@extend_schema(
    summary="Получить список карточек с фильтрами (POST JSON)",
    description="Принимает параметры фильтрации в теле JSON. Возвращает список карточек.",
    responses=CardSerializer(many=True)
)
class CardFilterPostView(generics.GenericAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_data = request.data

        # Применяем фильтр CardFilter к QuerySet, используя JSON-данные
        filtered_queryset = CardFilter(data=filter_data, queryset=queryset).qs

        # 🔑 Передаем объект запроса в контекст сериализатора
        serializer = self.get_serializer(
            filtered_queryset, 
            many=True, 
            context={'request': request} 
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------------
# 3. Детальная карточка
# -------------------------------
@extend_schema(
    summary="Получить подробную информацию о карточке",
    responses=CardSerializer
)
class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    # 🔑 ВАЖНО: Передаем объект запроса в контекст сериализатора
    def get_serializer_context(self):
        return {'request': self.request}


# -------------------------------
# 4. ДОБАВЛЕНИЕ/УДАЛЕНИЕ ИЗ ИЗБРАННОГО
# -------------------------------
@extend_schema(
    summary="Добавление/удаление карточки из избранного",
    description="POST - добавить в избранное. DELETE - удалить из избранного.",
    responses={
        201: {"application/json": {"example": {"message": "Карточка добавлена в избранное"}}},
        204: {"description": "Успешно удалено"},
        400: {"application/json": {"example": {"message": "Карточка уже в избранном/отсутствует"}}},
    }
)
class FavoriteAPIView(generics.GenericAPIView):
    queryset = Card.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
        
        # Проверяем, существует ли уже запись
        if Favorite.objects.filter(user=request.user, card=card).exists():
            return Response({'message': 'Карточка уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
            
        Favorite.objects.create(user=request.user, card=card)
        return Response({'message': 'Карточка добавлена в избранное'}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
        deleted_count, _ = Favorite.objects.filter(user=request.user, card=card).delete()

        if deleted_count == 0:
            return Response({'message': 'Карточка не была в избранном'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------
# 5. СПИСОК МОИХ ИЗБРАННЫХ КАРТОЧЕК
# -------------------------------
@extend_schema(
    summary="Список избранных карточек текущего пользователя",
    responses=FavoriteSerializer(many=True)
)
class MyFavoritesListAPIView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Возвращает объекты Favorite, которые включают связанные Card
        return Favorite.objects.filter(user=self.request.user).select_related('card')

    # 🔑 ВАЖНО: Передаем объект запроса в контекст сериализатора
    def get_serializer_context(self):
        return {'request': self.request}


# -------------------------------
# 6. Оценка карточки
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
        card = get_object_or_404(Card, pk=pk)

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
# 7. Создание заявки на звонок
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
        card = get_object_or_404(Card, pk=card_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(card=card)
        return Response({"ok": True, "code": "OK"}, status=201)


# -------------------------------
# 8. Добавление видео, отзыва, вопроса
# -------------------------------
class CardVideoCreateView(generics.CreateAPIView):
    serializer_class = CardVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card)

class CardReviewCreateView(generics.CreateAPIView):
    serializer_class = CardReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card, user=self.request.user)

class CardQuestionCreateView(generics.CreateAPIView):
    serializer_class = CardQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card, user=self.request.user)


# -------------------------------
# 9. Получение отзыва/вопроса по id
# -------------------------------
@extend_schema(summary="Получить отзыв по ID", responses=CardReviewSerializer)
class CardReviewDetailView(generics.RetrieveAPIView):
    queryset = CardReview.objects.all()
    serializer_class = CardReviewSerializer
    lookup_field = "id"

@extend_schema(summary="Получить вопрос по ID", responses=CardQuestionSerializer)
class CardQuestionDetailView(generics.RetrieveAPIView):
    queryset = CardQuestion.objects.all()
    serializer_class = CardQuestionSerializer
    lookup_field = "id"


# -------------------------------
# 10. Поиск карточек + история поиска
# -------------------------------
@extend_schema(
    summary="Поиск карточек",
    parameters=[OpenApiParameter(name="q", description="Поисковый запрос", required=False, type=str)],
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
    
    # 🔑 ВАЖНО: Передаем объект запроса в контекст сериализатора
    def get_serializer_context(self):
        return {'request': self.request}

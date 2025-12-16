from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import generics, permissions, status, serializers, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Card, CardReview, CardQuestion, CardVideo, SearchHistory, Favorite, Review
from .serializers import (
    CardSerializer,
    CardReviewSerializer,
    CardQuestionSerializer,
    CardVideoSerializer,
    CallRequestSerializer,
    FavoriteSerializer,
)
from .filters import CardFilter
from .permissions import IsAdminOrReadOnly

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
# 1. Список карточек
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

    def get_serializer_context(self):
        return {'request': self.request}

# -------------------------------
# 2. ФИЛЬТРАЦИЯ КАРТОЧЕК (POST)
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
        filtered_queryset = CardFilter(data=filter_data, queryset=queryset).qs
        serializer = self.get_serializer(filtered_queryset, many=True, context={'request': request})
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

    def get_serializer_context(self):
        return {'request': self.request}
    
    def retrieve(self, request, *args, **kwargs):
        """Переопределить retrieve для автоматического сохранения просмотра"""
        response = super().retrieve(request, *args, **kwargs)
        
        # 🔑 НОВОЕ: Автоматически сохранить просмотр если пользователь аутентифицирован
        if request.user.is_authenticated:
            from .models import ViewHistory
            card = self.get_object()
            ViewHistory.objects.create(
                user=request.user,
                card=card,
                duration_seconds=0  # Будет обновлено на фронте
            )
        
        return response

# -------------------------------
# 4. Избранное
# -------------------------------
@extend_schema(
    summary="Добавление/удаление карточки из избранного"
)
class FavoriteAPIView(generics.GenericAPIView):
    queryset = Card.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
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

class MyFavoritesListAPIView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('card')

    def get_serializer_context(self):
        return {'request': self.request}

# -------------------------------
# 5. Оценка карточки
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
# 6. Заявка на звонок
# -------------------------------
@extend_schema(
    summary="Оставить заявку на звонок",
    request=CallRequestSerializer,
    responses={201: OpenApiResponse(description="Создано")}
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
# 7. Видео, отзыв, вопрос
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

# -------------------------------
class CardQuestionListView(generics.ListAPIView):
    serializer_class = CardQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Список вопросов",
        description="Возвращает список всех вопросов, можно фильтровать по карточке через query param card_id",
        responses=CardQuestionSerializer(many=True)
    )
    def get_queryset(self):
        card_id = self.request.query_params.get('card_id')
        if card_id:
            return CardQuestion.objects.filter(card_id=card_id)
        return CardQuestion.objects.all()

# Создание вопроса к конкретной карточке
class CardQuestionCreateView(generics.CreateAPIView):
    serializer_class = CardQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Создать вопрос к карточке",
        request=CardQuestionSerializer,
        responses={201: CardQuestionSerializer}
    )
    def post(self, request, pk, *args, **kwargs):
        card = get_object_or_404(Card, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(card=card, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Ответ на вопрос (только админ/девелопер)
class CardQuestionAnswerView(generics.UpdateAPIView):
    queryset = CardQuestion.objects.all()
    serializer_class = CardQuestionSerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        summary="Ответить на вопрос",
        request=CardQuestionSerializer,
        responses={200: CardQuestionSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(answer=self.request.data.get('answer'))
# -------------------------------
# 9. Детали отзывов/вопросов
# -------------------------------
class CardReviewDetailView(generics.RetrieveAPIView):
    queryset = CardReview.objects.all()
    serializer_class = CardReviewSerializer
    lookup_field = "id"

class CardQuestionDetailView(generics.RetrieveAPIView):
    queryset = CardQuestion.objects.all()
    serializer_class = CardQuestionSerializer
    lookup_field = "id"

# -------------------------------
# 10. Поиск карточек
# -------------------------------
class CardSearchView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        if query and self.request.user.is_authenticated:
            SearchHistory.objects.create(user=self.request.user, query=query)
        
        if not query:
            return Card.objects.none()
        
        return Card.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )

    def get_serializer_context(self):
        return {'request': self.request}


# 🔑 НОВЫЕ: Views для истории просмотров и подборок документов

@extend_schema(
    summary="Сохранить просмотр карточки"
)
class CardViewHistoryView(generics.CreateAPIView):
    """Сохранить просмотр карточки пользователем"""
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        from .models import ViewHistory
        
        card_id = self.kwargs.get('card_pk')
        duration = request.data.get('duration_seconds', 0)
        
        try:
            card = Card.objects.get(id=card_id)
            view = ViewHistory.objects.create(
                user=request.user,
                card=card,
                duration_seconds=int(duration) if duration else 0
            )
            return Response(
                {'message': 'View saved', 'id': view.id},
                status=status.HTTP_201_CREATED
            )
        except Card.DoesNotExist:
            return Response(
                {'error': 'Card not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="История просмотров пользователя"
)
class UserViewHistoryListView(generics.ListAPIView):
    """Получить историю просмотров текущего пользователя"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from .models import ViewHistory
        return ViewHistory.objects.filter(user=self.request.user).order_by('-viewed_at')
    
    def get_serializer_class(self):
        from .serializers import ViewHistorySerializer
        return ViewHistorySerializer


@extend_schema(
    summary="Подборки документов для карточки"
)
class CardDocumentListsView(generics.ListAPIView):
    """Получить подборки документов для карточки"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        from .models import CardDocumentList
        card_id = self.kwargs.get('card_pk')
        return CardDocumentList.objects.filter(card_id=card_id)
    
    def get_serializer_class(self):
        from .serializers import CardDocumentListSerializer
        return CardDocumentListSerializer


@extend_schema(
    summary="Создать подборку документов"
)
class CardDocumentListCreateView(generics.CreateAPIView):
    """Создать новую подборку документов для карточки"""
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        from .serializers import CardDocumentListSerializer
        return CardDocumentListSerializer
    
    def perform_create(self, serializer):
        from .models import CardDocumentList
        card_id = self.kwargs.get('card_pk')
        card = get_object_or_404(Card, id=card_id)
        serializer.save(card=card)


# 🔑 НОВОЕ: Отзывы на карточки
class ReviewListCreateView(generics.ListCreateAPIView):
    """Список отзывов и создание нового отзыва"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        card_id = self.kwargs.get('card_pk')
        return Review.objects.filter(card_id=card_id)
    
    def get_serializer_class(self):
        from .serializers import ReviewSerializer, ReviewCreateUpdateSerializer
        if self.request.method == 'POST':
            return ReviewCreateUpdateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        from .models import Review
        card_id = self.kwargs.get('card_pk')
        card = get_object_or_404(Card, id=card_id)
        review = serializer.save(user=self.request.user, card=card)
        # Обновляем рейтинг карточки
        card.update_rating()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получить, обновить или удалить отзыв"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.all()
    
    def get_serializer_class(self):
        from .serializers import ReviewSerializer, ReviewCreateUpdateSerializer
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return ReviewCreateUpdateSerializer
        return ReviewSerializer
    
    def check_object_permissions(self, request, obj):
        # Только автор может редактировать/удалять
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != request.user:
                self.permission_denied(request, message="You can only edit your own reviews")
        super().check_object_permissions(request, obj)
    
    def perform_update(self, serializer):
        review = serializer.save()
        # Обновляем рейтинг карточки
        review.card.update_rating()
    
    def perform_destroy(self, instance):
        card = instance.card
        instance.delete()
        # Обновляем рейтинг карточки
        card.update_rating()


# 🔑 НОВОЕ: Подборка для карточки
@extend_schema(
    summary="Получить подборку похожих карточек",
    responses=CardSerializer(many=True)
)
class CardCurationsView(generics.RetrieveAPIView):
    """Получить подборку похожих карточек"""
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    
    def retrieve(self, request, *args, **kwargs):
        """Переопределить для возврата кураций"""
        card = self.get_object()
        
        # Генерируем кураци если нужны
        if not card.list_curations or card.list_curations == '[]':
            card.generate_curations(user=request.user if request.user.is_authenticated else None)
        
        # Возвращаем курации
        import json
        try:
            curations_data = json.loads(card.list_curations)
        except:
            curations_data = []
        
        return Response({
            'card_id': card.id,
            'curations': curations_data
        }, status=status.HTTP_200_OK)

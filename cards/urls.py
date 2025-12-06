from django.urls import path
from .views import (
    CardListView,
    CardDetailView,
    RateCardView,
    CallRequestCreateView,
    CardVideoCreateView,
    CardReviewCreateView,
    CardQuestionCreateView,
    CardReviewDetailView,
    CardQuestionDetailView,
    CardSearchView,
    CardFilterPostView,
    FavoriteAPIView,
    MyFavoritesListAPIView,
    CardQuestionListView,
    CardQuestionAnswerView,
)

urlpatterns = [
    # --- Список карточек и фильтры ---
    path("", CardListView.as_view(), name="cards_list"),  # GET /api/cards/
    path("filter/", CardFilterPostView.as_view(), name="cards_filter_post"),  # POST /api/cards/filter/
    path("<int:pk>/", CardDetailView.as_view(), name="card_detail"),

    # --- Избранное ---
    path("<int:pk>/favorite/", FavoriteAPIView.as_view(), name="card_favorite"),  # POST/DELETE
    path("favorites/me/", MyFavoritesListAPIView.as_view(), name="my_favorites"),  # GET

    # --- Рейтинг ---
    path("<int:pk>/rate/", RateCardView.as_view(), name="card_rate"),  # POST

    # --- Заявка на звонок ---
    path("<int:pk>/call_request/", CallRequestCreateView.as_view(), name="call_request"),  # POST

    # --- Видео ---
    path("<int:pk>/videos/add/", CardVideoCreateView.as_view(), name="card_video_add"),  # POST

    # --- Отзывы ---
    path("<int:pk>/reviews/add/", CardReviewCreateView.as_view(), name="card_review_add"),  # POST
    path("reviews/<int:id>/", CardReviewDetailView.as_view(), name="card_review_detail"),  # GET

   # --- Вопросы и ответы ---
# Создать вопрос для конкретной карточки
path("<int:pk>/questions/add/", CardQuestionCreateView.as_view(), name="card_question_add"),  # POST

# Получить все вопросы (можно фильтровать по карточке через query param ?card=ID)
path("questions/", CardQuestionListView.as_view(), name="card_question_list"),  # GET

# Получить вопрос по ID
path("questions/<int:id>/", CardQuestionDetailView.as_view(), name="card_question_detail"),  # GET

# Ответить на вопрос (только разработчик/админ)
path("questions/<int:pk>/answer/", CardQuestionAnswerView.as_view(), name="card_question_answer"),  # PATCH/PUT

    # --- Поиск ---
    path("search/", CardSearchView.as_view(), name="card_search"),  # GET /api/cards/search/?q=
]

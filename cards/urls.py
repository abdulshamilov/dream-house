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
)

urlpatterns = [
    # --- Список карточек и Фильтр ---
    path("", CardListView.as_view(), name="cards_list"),                # GET /api/cards/
    path("filter/", CardFilterPostView.as_view(), name="cards_filter_post"), # POST /api/cards/filter/
    path("<int:pk>/", CardDetailView.as_view(), name="card_detail"),

    # --- Избранное ---
    path("<int:pk>/favorite/", FavoriteAPIView.as_view(), name="card_favorite"), # POST/DELETE /api/cards/{pk}/favorite/
    path("favorites/me/", MyFavoritesListAPIView.as_view(), name="my_favorites"), # GET /api/cards/favorites/me/

    # --- Рейтинг ---
    path("<int:pk>/rate/", RateCardView.as_view(), name="card_rate"),

    # --- Заявка на звонок ---
    path("<int:pk>/call_request/", CallRequestCreateView.as_view(), name="call_request"),

    # --- Видео ---
    path("<int:pk>/videos/add/", CardVideoCreateView.as_view(), name="card_video_add"),

    # --- Отзывы ---
    path("<int:pk>/reviews/add/", CardReviewCreateView.as_view(), name="card_review_add"),
    path("reviews/<int:id>/", CardReviewDetailView.as_view(), name="card_review_detail"),

    # --- Вопросы ---
    path("<int:pk>/questions/add/", CardQuestionCreateView.as_view(), name="card_question_add"),
    path("questions/<int:id>/", CardQuestionDetailView.as_view(), name="card_question_detail"),

    # --- Поиск ---
    path("search/", CardSearchView.as_view(), name="card_search"),

    
]

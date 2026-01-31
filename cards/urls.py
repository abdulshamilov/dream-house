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
    CardViewHistoryView,  # 🔑 НОВОЕ
    UserViewHistoryListView,  # 🔑 НОВОЕ
    CardDocumentListsView,  # 🔑 НОВОЕ
    CardDocumentListCreateView,  # 🔑 НОВОЕ
    ReviewListCreateView,  # 🔑 НОВОЕ
    ReviewDetailView,  # 🔑 НОВОЕ
    CardCurationsView,  # 🔑 НОВОЕ
    SearchHistoryView,  # 🔑 ИСТОРИЯ ПОИСКА
    PersonalRecommendationsView,  # 🔑 ПОДБОРКА ДЛЯ МЕНЯ
    RecentlyViewedView,  # 🔑 НЕДАВНО ПРОСМОТРЕННЫЕ
    ReviewLikeView,  # 🔑 ЛАЙКИ НА ОТЗЫВЫ
    PromotionListView,  # 🔑 АКЦИИ
)
from .views_ai import (
    DiscountRequestCreateView,
    UserDiscountRequestsView,
    GetRecommendationsView,
    AIChatView,
    ChatHistoryView,
    RateAIResponseView,
)

urlpatterns = [
    path("", CardListView.as_view(), name="cards_list"),
    path("filter/", CardFilterPostView.as_view(), name="cards_filter_post"),
    path("promotions/", PromotionListView.as_view(), name="promotions_list"),
    path("recommendations/for-me/", PersonalRecommendationsView.as_view(), name="personal_recommendations"),  # 🔑 ПОДБОРКА ДЛЯ МЕНЯ
    path("recent-views/", RecentlyViewedView.as_view(), name="recently_viewed"),  # 🔑 НЕДАВНО ПРОСМОТРЕННЫЕ
    path("<int:pk>/", CardDetailView.as_view(), name="card_detail"),
    path("<int:pk>/favorite/", FavoriteAPIView.as_view(), name="card_favorite"),
    path("favorites/me/", MyFavoritesListAPIView.as_view(), name="my_favorites"),
    path("<int:pk>/rate/", RateCardView.as_view(), name="card_rate"),
    path("<int:pk>/call_request/", CallRequestCreateView.as_view(), name="call_request"),
    path("<int:pk>/videos/add/", CardVideoCreateView.as_view(), name="card_video_add"),
    path("<int:pk>/reviews/add/", CardReviewCreateView.as_view(), name="card_review_add"),
    path("reviews/<int:id>/", CardReviewDetailView.as_view(), name="card_review_detail"),
    path("reviews/<int:review_id>/like/", ReviewLikeView.as_view(), name="review_like"),  # 🔑 НОВОЕ: Лайк на отзыв
    path("<int:card_pk>/user-reviews/", ReviewListCreateView.as_view(), name="card_user_reviews"),
    path("user-reviews/<int:pk>/", ReviewDetailView.as_view(), name="user_review_detail"),
    path("<int:pk>/curations/", CardCurationsView.as_view(), name="card_curations"),
    path("<int:pk>/questions/add/", CardQuestionCreateView.as_view(), name="card_question_add"),
    path("questions/", CardQuestionListView.as_view(), name="card_question_list"),
    path("questions/<int:id>/", CardQuestionDetailView.as_view(), name="card_question_detail"),
    path("questions/<int:pk>/answer/", CardQuestionAnswerView.as_view(), name="card_question_answer"),
    path("search/", CardSearchView.as_view(), name="card_search"),
    path("search-history/", SearchHistoryView.as_view(), name="search_history"),
    # 🔑 НОВЫЕ: История просмотров
    path("<int:card_pk>/view-history/", CardViewHistoryView.as_view(), name="card_view_history"),
    path("view-history/me/", UserViewHistoryListView.as_view(), name="my_view_history"),
    # 🔑 НОВЫЕ: Подборки документов
    path("<int:card_pk>/document-lists/", CardDocumentListsView.as_view(), name="card_document_lists"),
    path("<int:card_pk>/document-lists/create/", CardDocumentListCreateView.as_view(), name="card_document_list_create"),
    # AI
    path("<int:pk>/discount/", DiscountRequestCreateView.as_view(), name="discount_request"),
    path("discounts/me/", UserDiscountRequestsView.as_view(), name="my_discounts"),
    path("recommendations/", GetRecommendationsView.as_view(), name="recommendations"),
    path("ai/chat/", AIChatView.as_view(), name="ai_chat"),
    path("ai/history/", ChatHistoryView.as_view(), name="chat_history"),
    path("ai/chat/<int:pk>/rate/", RateAIResponseView.as_view(), name="rate_ai_response"),
]

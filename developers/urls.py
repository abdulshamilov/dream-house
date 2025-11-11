from django.urls import path
from .views import (
    DeveloperListAPIView,
    DeveloperDetailView,
    DeveloperCardsAPIView,
    SubscribeAPIView,
    MySubscriptionsAPIView,
)

urlpatterns = [
    path('', DeveloperListAPIView.as_view(), name='developer_list'),
    path('<int:developer_id>/cards/', DeveloperCardsAPIView.as_view(), name='developer_cards'),

    # 🔹 Один endpoint для подписки/отписки
    path('<int:developer_id>/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),

    path('me/subscriptions/', MySubscriptionsAPIView.as_view(), name='my_subscriptions'),
    path('<int:pk>/', DeveloperDetailView.as_view(), name='developer-detail'),
]

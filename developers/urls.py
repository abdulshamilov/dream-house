from django.urls import path
from .views import (
    DeveloperListAPIView,
    DeveloperDetailView,
    DeveloperCardsAPIView,
    SubscribeAPIView,
    MySubscriptionsAPIView,
)

urlpatterns = [
    # ✅ Все застройщики
    path('', DeveloperListAPIView.as_view(), name='developer_list'),

    # ✅ ЖК определённого застройщика
    path('<int:developer_id>/cards/', DeveloperCardsAPIView.as_view(), name='developer_cards'),

    # ✅ Подписка и отписка
    path('<int:developer_id>/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    path('<int:developer_id>/unsubscribe/', SubscribeAPIView.as_view(), name='unsubscribe'),

    # ✅ Мои подписки
    path('me/subscriptions/', MySubscriptionsAPIView.as_view(), name='my_subscriptions'),

    # ✅ Детали застройщика (ставим последним!)
    path('<int:pk>/', DeveloperDetailView.as_view(), name='developer-detail'),
]

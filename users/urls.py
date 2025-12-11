from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    MeView, 
    ReferralListView, 
    get_referral_link,
    PasswordResetRequestView,
    PasswordResetConfirmView
)


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path('referrals/', ReferralListView.as_view(), name='referral-list'),
    path('referral-link/', get_referral_link, name='referral-link'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

from django.urls import path
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    MeView, 
    ReferralListView, 
    get_referral_link,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    UpdateProfileView,
    DeleteAccountView,
    SMSRequestView,
    SMSVerifyView,
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
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),  # PUT для смены фото и имени, DELETE для удаления фото
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),   # DELETE для удаления аккаунта
    path('sms/request/', SMSRequestView.as_view(), name='sms-request'),  # Запрос OTP по SMS
    path('sms/verify/', SMSVerifyView.as_view(), name='sms-verify'),    # Проверка OTP и вход
]

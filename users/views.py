from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    ReferralSerializer, 
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    TokenSerializer
)
from rest_framework import generics, permissions
from .models import Referral, PasswordResetOTP

from rest_framework.decorators import api_view, permission_classes
import uuid

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: TokenSerializer},
        tags=["Auth"],
        summary="Регистрация нового пользователя и получение JWT токенов"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for newly registered user
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=CustomTokenObtainPairSerializer,
        responses={200: TokenSerializer},
        tags=["Auth"],
        summary="Вход по номеру телефона и паролю"
    )
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: {"detail": "OTP sent to phone"}},
        tags=["Auth"],
        summary="Запрос сброса пароля (отправка OTP)"
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        user = User.objects.get(phone_number=phone_number)
        
        # Generate OTP
        otp = PasswordResetOTP.generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)
        
        # TODO: Send OTP via SMS (integrate with SMS provider)
        # For now, we'll return it in development mode
        # In production, remove this line
        print(f"OTP for {phone_number}: {otp}")
        
        return Response({
            "detail": "OTP sent to your phone",
            "otp": otp  # Remove in production!
        }, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200: TokenSerializer},
        tags=["Auth"],
        summary="Подтверждение сброса пароля и получение JWT токенов"
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        
        # Get the latest valid OTP for this user
        try:
            otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)
        
        if not otp_obj.is_valid():
            return Response({"detail": "OTP expired"}, status=400)
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=200)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: {"detail": "Logged out"}},
        tags=["Auth"],
        summary="Выход из аккаунта (разорвать JWT сессию)"
    )
    def post(self, request):
        # With JWT, logout is handled on client side by removing tokens
        # This endpoint exists for symmetry and to allow blacklist token if needed
        return Response({"detail": "Logged out successfully"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        tags=["User"],
        summary="Получить информацию о текущем пользователе"
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ReferralListView(generics.ListAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Referral.objects.filter(referrer=self.request.user)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_link(request):
    user = request.user
    code = str(uuid.uuid4())
    link = f"https://dreamhouse05.com/register/?ref={code}"
    return Response({"referral_link": link})
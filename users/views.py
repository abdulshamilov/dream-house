# DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import SimpleUploadedFile

# DRF Spectacular
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from drf_spectacular.openapi import AutoSchema

# Django
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Local
from .serializers import (
    RegisterRequestSerializer, RegisterConfirmSerializer, UserSerializer, ReferralSerializer,
    CustomTokenObtainPairSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, TokenSerializer, ReferralLinkSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer, DeleteAccountSerializer,
    SMSRequestSerializer, SMSVerifySerializer, FCMTokenSerializer,
)
from .models import Referral, PasswordResetOTP, LoginOTP, FCMDeviceToken

# Standard Library
import uuid
import io
from pathlib import Path

User = get_user_model()


class DeleteWithBodySchema(AutoSchema):
    """Allow request body on DELETE for OTP confirmation."""

    def _get_request_body(self, direction='request'):
        if self.method == 'DELETE':
            original_method = self.method
            try:
                self.method = 'POST'
                return super()._get_request_body(direction)
            finally:
                self.method = original_method
        return super()._get_request_body(direction)


class RegisterView(APIView):
    """Step 1: Registration request with phone and name"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="RegisterOTPResponse",
                    fields={
                        "detail": serializers.CharField(),
                        "phone_number": serializers.CharField(),
                        "otp": serializers.CharField(required=False, allow_null=True),
                    },
                ),
                description="OTP sent to phone",
            )
        },
        tags=["Auth"],
        summary="Шаг 1: Регистрация - отправка кода подтверждения"
    )
    def post(self, request):
        from .models import SMSRateLimit
        
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        name = serializer.validated_data['name']
        ref_code = serializer.validated_data.get('ref_code', '').strip()

        # If account already exists, force user to use SMS login flow
        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"detail": "User already registered. Use /api/users/sms/request/ to sign in."},
                status=400
            )
        
        # Проверка rate limit
        allowed, wait_seconds, message = SMSRateLimit.check_and_record(phone_number)
        if not allowed:
            return Response(
                {"detail": message, "wait_seconds": wait_seconds},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        
        # Generate OTP and save registration data temporarily
        otp = LoginOTP.generate_otp()
        # Remove all previous OTPs for this phone (avoid unique_together collisions on Postgres)
        LoginOTP.objects.filter(phone_number=phone_number).delete()
        LoginOTP.objects.create(phone_number=phone_number, otp=otp, name=name, ref_code=ref_code or None)
        
        # Send OTP via existing SMS flow (mirrors /sms/request)
        SMSRequestView()._send_sms(phone_number, otp)

        return Response({
            "detail": "OTP sent to your phone",
            "phone_number": phone_number,
            "otp": otp if settings.SMS_DEBUG_RETURN_OTP else None
        }, status=200)


class RegisterConfirmView(APIView):
    """Step 2: Confirm registration with OTP code"""
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterConfirmSerializer,
        responses={201: TokenSerializer},
        tags=["Auth"],
        summary="Шаг 2: Регистрация - подтверждение кода и создание аккаунта"
    )
    def post(self, request):
        serializer = RegisterConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        ref_code_from_request = serializer.validated_data.get('ref_code', '').strip() or None
        
        # Block if already registered
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"detail": "User with this phone number already registered"}, status=400)
        
        # Verify OTP
        try:
            otp_obj = LoginOTP.objects.filter(phone_number=phone_number, otp=otp).latest('created_at')
        except LoginOTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)
        
        if not otp_obj.is_valid():
            return Response({"detail": "OTP expired or already used"}, status=400)
        
        # Name must come from first step
        if not otp_obj.name:
            return Response({"detail": "Name is missing. Request registration again."}, status=400)
        name = otp_obj.name
        ref_code = otp_obj.ref_code or ref_code_from_request
        if ref_code:
            try:
                ref_code_uuid = uuid.UUID(str(ref_code))
                ref_code = str(ref_code_uuid)
            except (ValueError, TypeError):
                return Response({"detail": "Invalid ref_code"}, status=400)
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])
        
        # Create user without password
        user = User.objects.create_user(
            phone_number=phone_number,
            password=None,  # No password
            name=name,
        )
        
        # Handle referral code if provided: find referrer by their referral_code
        if ref_code:
            referrer = User.objects.filter(referral_code=ref_code).first()
            if referrer:
                Referral.objects.create(referrer=referrer, referred=user)
        
        # Generate JWT tokens
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
        return Response(
            {"detail": "Login is SMS-code only. Use /api/users/sms/request and /api/users/sms/verify"},
            status=400
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="PasswordResetOTPResponse",
                    fields={
                        "detail": serializers.CharField(),
                        "otp": serializers.CharField(required=False, allow_null=True),
                    },
                ),
                description="OTP sent to phone",
            )
        },
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
            "detail": "OTP sent to your phone"
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

    serializer_class = None  # For schema tooling

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="LogoutResponse",
                    fields={"detail": serializers.CharField()}
                ),
                description="Logged out",
            )
        },
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
        return Response(UserSerializer(request.user, context={'request': request}).data)


class ReferralListView(generics.ListAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Referral.objects.none()
        return Referral.objects.filter(referrer=self.request.user)
    

class ReferralLinkView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralLinkSerializer

    @extend_schema(
        request=None,
        responses=ReferralLinkSerializer,
        tags=["User"],
        summary="Получить реферальную ссылку",
    )
    def get(self, request):
        # Ensure the user has a persistent referral code
        if not request.user.referral_code:
            request.user.referral_code = uuid.uuid4()
            request.user.save(update_fields=["referral_code"])

        link = f"https://dreamhouse05.com/register/?ref={request.user.referral_code}"
        return Response({"referral_link": link})


class ChangePasswordView(APIView):
    """Смена пароля аккаунта. Требует проверку старого пароля."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="ChangePasswordResponse",
                    fields={"detail": serializers.CharField()},
                ),
                description="Password changed successfully",
            )
        },
        tags=["User"],
        summary="Смена пароля",
        description="Изменить пароль аккаунта. Требует старый пароль для подтверждения."
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Проверяем старый пароль
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=400
            )
        
        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"User {user.phone_number} changed password")
        
        return Response({"detail": "Password changed successfully"}, status=200)


class UpdateProfileView(APIView):
    """Обновление профиля: имя, фото профиля"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=UpdateProfileSerializer,
        responses={200: UserSerializer},
        tags=["User"],
        summary="Обновить профиль (имя, фото)",
        description="Изменить имя пользователя или загрузить новое фото профиля. Максимальный размер фото: 5MB. Поддерживаемые форматы: JPEG, PNG, GIF"
    )
    def put(self, request):
        data = request.data.copy()

        # Достаём файл из файлов или data (DRF кладёт в data, Django — в FILES)
        new_photo = None
        if 'profile_photo' in request.FILES:
            new_photo = request.FILES['profile_photo']
        elif 'profile_photo' in data:
            new_photo = data.get('profile_photo')

        # Debug log: что реально пришло
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            "update-profile: files=%s data_has_photo=%s photo_type=%s",
            list(request.FILES.keys()),
            'profile_photo' in data,
            type(new_photo).__name__ if new_photo is not None else None,
        )

        # Если загрузили HEIC/HEIF, конвертируем в JPEG для Pillow/Storage
        if new_photo:
            converted, error = self._convert_heic(new_photo)
            if error:
                return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)
            if converted is not None:
                data['profile_photo'] = converted
                new_photo = converted

        serializer = UpdateProfileSerializer(
            request.user,
            data=data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Delete old photo if new one is being uploaded
        user = request.user
        old_photo = user.profile_photo if new_photo else None

        user = serializer.save()

        if new_photo and old_photo and old_photo.name:
            from django.core.files.storage import default_storage
            if default_storage.exists(old_photo.name):
                default_storage.delete(old_photo.name)
        
        logger.info(f"User {user.phone_number} updated profile")
        
        return Response(UserSerializer(user, context={'request': request}).data, status=200)

    def _convert_heic(self, uploaded_file):
        """Конвертация HEIC/HEIF в JPEG.
        Возвращает (file or None, error_message or None).
        """
        content_type = (getattr(uploaded_file, 'content_type', '') or '').lower()
        name_lower = uploaded_file.name.lower()
        heic_types = {'image/heic', 'image/heif', 'image/heic-sequence', 'image/heif-sequence'}
        is_heic = (
            content_type in heic_types
            or name_lower.endswith('.heic')
            or name_lower.endswith('.heif')
        )
        if not is_heic:
            return None, None

        try:
            import pillow_heif
            from PIL import Image

            # Попробуем прямое чтение HEIF → PIL
            uploaded_file.seek(0)
            heif_file = pillow_heif.read_heif(uploaded_file.read())
            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
            image = image.convert('RGB')

            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=90)
            buffer.seek(0)

            new_name = f"{Path(uploaded_file.name).stem}.jpg"
            return SimpleUploadedFile(new_name, buffer.getvalue(), content_type='image/jpeg'), None
        except ImportError:
            return None, "HEIC не поддерживается на сервере (pillow-heif не установлен). Загрузите JPG/PNG." 
        except Exception as e:
            # fallback через register opener
            try:
                uploaded_file.seek(0)
                pillow_heif.register_heif_opener()
                image = Image.open(uploaded_file)
                image = image.convert('RGB')
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=90)
                buffer.seek(0)
                new_name = f"{Path(uploaded_file.name).stem}.jpg"
                return SimpleUploadedFile(new_name, buffer.getvalue(), content_type='image/jpeg'), None
            except Exception as e2:
                import logging
                logging.getLogger(__name__).error("HEIC convert failed: %s / fallback: %s", str(e), str(e2))
                return None, "Не удалось конвертировать HEIC. Загрузите JPG/PNG." 
    
    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="ProfilePhotoDeleteResponse",
                    fields={"detail": serializers.CharField()}
                ),
                description="Фото профиля удалено",
            )
        },
        tags=["User"],
        summary="Удалить фото профиля"
    )
    def delete(self, request):
        """Удалить фото профиля пользователя"""
        user = request.user
        
        if user.profile_photo:
            # Delete file from storage
            import os
            from django.core.files.storage import default_storage
            if default_storage.exists(user.profile_photo.name):
                default_storage.delete(user.profile_photo.name)
            
            user.profile_photo = None
            user.save()
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"User {user.phone_number} deleted profile photo")
        
        return Response({"detail": "Photo deleted successfully"}, status=200)


class DeleteAccountOTPRequestView(APIView):
    """Отправка SMS-кода для подтверждения удаления аккаунта."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="DeleteAccountOTPResponse",
                    fields={
                        "detail": serializers.CharField(),
                        "otp": serializers.CharField(required=False, allow_null=True),
                    },
                ),
                description="OTP sent to phone",
            )
        },
        tags=["User"],
        summary="Запросить SMS-код для удаления аккаунта",
        description="Отправляет одноразовый код на привязанный номер. Код действует 5 минут."
    )
    def post(self, request):
        from .models import SMSRateLimit
        
        user = request.user
        phone_number = user.phone_number

        # Проверка rate limit
        allowed, wait_seconds, message = SMSRateLimit.check_and_record(phone_number)
        if not allowed:
            return Response(
                {"detail": message, "wait_seconds": wait_seconds},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp = LoginOTP.generate_otp()
        LoginOTP.objects.filter(phone_number=phone_number).delete()
        LoginOTP.objects.create(phone_number=phone_number, otp=otp)

        SMSRequestView()._send_sms(phone_number, otp)

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"User {phone_number} requested delete-account OTP")

        return Response(
            {
                "detail": "OTP sent to your phone",
                "otp": otp if settings.SMS_DEBUG_RETURN_OTP else None,
            },
            status=200,
        )

class DeleteAccountView(APIView):
    """Удаление аккаунта и всех связанных данных (необратимо) по SMS-коду."""
    permission_classes = [IsAuthenticated]
    schema = DeleteWithBodySchema()

    @extend_schema(
        request=DeleteAccountSerializer,
        responses={204: None},
        tags=["User"],
        summary="Удалить аккаунт (необратимо)",
        description=(
            "Удаляет аккаунт и связанные пользовательские данные. "
            "Требует SMS-код, отправленный через отдельный запрос. "
            "Эта операция не может быть отменена."
        ),
        examples=[
            OpenApiExample(
                "Пример тела запроса",
                value={"otp": "123456"},
                request_only=True,
            )
        ],
    )
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        otp = serializer.validated_data['otp']

        try:
            otp_obj = LoginOTP.objects.filter(phone_number=user.phone_number, otp=otp).latest('created_at')
        except LoginOTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)

        if not otp_obj.is_valid():
            return Response({"detail": "OTP expired or already used"}, status=400)

        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])
        
        phone_number = user.phone_number
        user_id = user.id
        
        # Delete user profile photo before deleting user
        if user.profile_photo:
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(user.profile_photo.name):
                    default_storage.delete(user.profile_photo.name)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error deleting profile photo for user {phone_number}: {str(e)}")
        
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"User {phone_number} (ID: {user_id}) deleted account with all data")
        
        # Удаляем все данные пользователя (каскадное удаление)
        user.delete()
        
        return Response(
            {"detail": "Account and all associated data deleted successfully"}, 
            status=204
        )


    @extend_schema(
        request=DeleteAccountSerializer,
        responses={204: None},
        tags=["User"],
        summary="Удалить аккаунт (необратимо)",
        description=(
            "Удаляет аккаунт и связанные пользовательские данные. "
            "Требует SMS-код, отправленный через отдельный запрос. "
            "Эта операция не может быть отменена."
        ),
        examples=[
            OpenApiExample(
                "Пример тела запроса",
                value={"otp": "123456"},
                request_only=True,
            )
        ],
    )
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        otp = serializer.validated_data['otp']

        try:
            otp_obj = LoginOTP.objects.filter(phone_number=user.phone_number, otp=otp).latest('created_at')
        except LoginOTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)

        if not otp_obj.is_valid():
            return Response({"detail": "OTP expired or already used"}, status=400)

        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])
        
        phone_number = user.phone_number
        user_id = user.id
        
        # Delete user profile photo before deleting user
        if user.profile_photo:
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(user.profile_photo.name):
                    default_storage.delete(user.profile_photo.name)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error deleting profile photo for user {phone_number}: {str(e)}")
        
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"User {phone_number} (ID: {user_id}) deleted account with all data")
        
        # Удаляем все данные пользователя (каскадное удаление)
        user.delete()
        
        return Response(
            {"detail": "Account and all associated data deleted successfully"}, 
            status=204
        )


class SMSRequestView(APIView):
    """Request OTP code for SMS-based login"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=SMSRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="SMSLoginOTPResponse",
                    fields={
                        "detail": serializers.CharField(),
                        "otp": serializers.CharField(required=False, allow_null=True),
                    },
                ),
                description="OTP sent to phone",
            )
        },
        tags=["Auth"],
        summary="Запрос кода входа в SMS (как Ozon)"
    )
    def post(self, request):
        from .models import LoginOTP, SMSRateLimit
        serializer = SMSRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']

        # --- Специальный тестовый аккаунт ---
        if phone_number == '+79887851557':
            return Response({"detail": "Код отправлен на ваш номер"}, status=200)
        # ------------------------------------

        # Разрешаем вход только уже зарегистрированным пользователям
        if not User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"detail": "Пользователь с таким номером не найден. Зарегистрируйтесь, чтобы войти."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Проверка rate limit
        allowed, wait_seconds, message = SMSRateLimit.check_and_record(phone_number)
        if not allowed:
            return Response(
                {"detail": message, "wait_seconds": wait_seconds},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        
        # Generate OTP
        otp = LoginOTP.generate_otp()
        
        # Delete all previous OTPs for this phone (avoid unique_together collisions on Postgres)
        LoginOTP.objects.filter(phone_number=phone_number).delete()
        
        # Create new OTP
        LoginOTP.objects.create(phone_number=phone_number, otp=otp)
        
        # Send OTP via SMS
        self._send_sms(phone_number, otp)
        
        return Response({
            "detail": "Код отправлен на ваш номер",
            "otp": otp if settings.SMS_DEBUG_RETURN_OTP else None
        }, status=200)
    
    def _send_sms(self, phone_number, otp):
        """Send OTP via SMS using configured provider"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Check if we should actually send SMS (SEND_REAL_SMS flag or not DEBUG mode)
            should_send_real = settings.SEND_REAL_SMS or not settings.DEBUG
            
            logger.info(f"[SMS] DEBUG={settings.DEBUG}, SEND_REAL_SMS={settings.SEND_REAL_SMS}, should_send_real={should_send_real}")
            # Log OTP for visibility (do not enable in prod logs if security policy forbids)
            logger.info(f"[SMS] OTP for {phone_number}: {otp}")
            
            if should_send_real:
                # Production or test mode: use real SMS provider
                logger.info(f"[SMS] SENDING REAL SMS to {phone_number}")
                self._send_via_provider(phone_number, otp, logger)
            else:
                # Development: just print to console
                logger.info(f"[SMS DEV] OTP for {phone_number}: {otp}")
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            # Don't raise - user should still get feedback
    
    def _send_via_provider(self, phone_number, otp, logger):
        """Send SMS via configured provider (Twilio, AWS SNS, p1sms, etc.)"""
        import os
        
        provider = os.getenv('SMS_PROVIDER', 'p1sms')
        
        if provider == 'p1sms':
            self._send_via_p1sms(phone_number, otp, logger)
        elif provider == 'smsru':
            self._send_via_smsru(phone_number, otp, logger)
        elif provider == 'twilio':
            self._send_via_twilio(phone_number, otp, logger)
        elif provider == 'aws':
            self._send_via_aws_sns(phone_number, otp, logger)
        elif provider == 'smtp':
            self._send_via_smtp(phone_number, otp, logger)
        else:
            logger.warning(f"Unknown SMS provider: {provider}")

    def _send_via_smsru(self, phone_number, otp, logger):
        """Send SMS using sms.ru simple HTTP API"""
        import requests
        import urllib.parse

        api_id = settings.SMSRU_API_ID
        if not api_id:
            logger.warning("sms.ru API ID not configured")
            return

        # sms.ru expects digits, typically 79XXXXXXXXX
        digits = ''.join(c for c in phone_number if c.isdigit())
        if digits.startswith('8'):
            digits = '7' + digits[-10:]
        elif digits.startswith('+7'):
            digits = '7' + digits[-10:]
        elif digits.startswith('7'):
            digits = '7' + digits[-10:]
        else:
            # fallback: take last 10 digits and prefix 7
            digits = '7' + digits[-10:]

        text = f"Kod Dream House: {otp}. Deistvitelen 5 minut."

        params = {
            'api_id': api_id,
            'to': digits,
            'msg': text,
            'json': 1,
            'from': 'Dream House',
        }

        logger.info(f"[sms.ru] Sending SMS to {phone_number} (normalized: {digits})")

        try:
            resp = requests.get('https://sms.ru/sms/send', params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"[sms.ru] Response: status={data.get('status')} code={data.get('status_code')}" )
            if data.get('status') != 'OK':
                logger.error(f"[sms.ru] Error: {data}")
        except requests.exceptions.Timeout:
            logger.error(f"[sms.ru] Timeout for {phone_number}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"[sms.ru] Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[sms.ru] Error: {str(e)}")
            raise
    
    def _send_via_p1sms(self, phone_number, otp, logger):
        """Send SMS using p1sms (Russian SMS provider) - API v2"""
        import requests
        import json
        
        api_key = settings.P1SMS_API_KEY
        
        if not api_key:
            logger.warning("p1sms API key not configured")
            return
        
        # Normalize phone number for p1sms (should be like 79991234567 without +)
        phone_digits = ''.join(c for c in phone_number if c.isdigit())
        if phone_digits.startswith('7'):
            phone_digits = '7' + phone_digits[-10:]  # Ensure 11 digits starting with 7
        elif phone_digits.startswith('8'):
            phone_digits = '7' + phone_digits[-10:]  # Convert 8 to 7
        else:
            phone_digits = '7' + phone_digits[-10:]  # Default to 7
        
        message_text = f"Kod Dream House: {otp}. Deistvitelen 5 minut."
        
        try:
            # p1sms API v2 endpoint (admin.p1sms.ru)
            url = "https://admin.p1sms.ru/apiSms/create"
            
            # Correct JSON payload for p1sms API v2
            payload = {
                "apiKey": api_key,
                "sms": [
                    {
                        "channel": "digit",
                        "text": message_text,
                        "phone": phone_digits
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            logger.info(f"[p1sms] Sending SMS to {phone_number} (normalized: {phone_digits})")
            logger.info(f"[p1sms] Message: {message_text}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            
            logger.info(f"[p1sms] Response Status: {response.status_code}")
            logger.info(f"[p1sms] Response Body: {json.dumps(result) if isinstance(result, dict) else result}")
                
        except requests.exceptions.Timeout:
            logger.error(f"[p1sms] Timeout for {phone_number}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"[p1sms] Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[p1sms] Error: {str(e)}")
            raise
    
    def _send_via_twilio(self, phone_number, otp, logger):
        """Send SMS using Twilio"""
        from twilio.rest import Client
        import os
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.warning("Twilio credentials not configured")
            return
        
        client = Client(account_sid, auth_token)
        message_text = f"Your Dream House verification code: {otp}. Valid for 5 minutes."
        
        try:
            message = client.messages.create(
                body=message_text,
                from_=from_number,
                to=phone_number
            )
            logger.info(f"SMS sent via Twilio. SID: {message.sid}")
        except Exception as e:
            logger.error(f"Twilio error: {str(e)}")
            raise
    
    def _send_via_aws_sns(self, phone_number, otp, logger):
        """Send SMS using AWS SNS"""
        import boto3
        import os
        
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            sns_client = boto3.client('sns', region_name=region)
            message_text = f"Your Dream House verification code: {otp}. Valid for 5 minutes."
            
            response = sns_client.publish(
                PhoneNumber=phone_number,
                Message=message_text,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'DreamHouse'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            logger.info(f"SMS sent via AWS SNS. MessageId: {response['MessageId']}")
        except Exception as e:
            logger.error(f"AWS SNS error: {str(e)}")
            raise
    
    def _send_via_smtp(self, phone_number, otp, logger):
        """Send SMS using Email-to-SMS gateway"""
        import smtplib
        from email.mime.text import MIMEText
        import os
        
        # Example for Russian SMS providers
        # Different carriers have email gateways
        carriers = {
            'mts': '@mts.ru',
            'beeline': '@beelinetel.ru',
            'megafon': '@megafon.ru',
            'rostelecom': '@rostelecom.ru'
        }
        
        carrier = os.getenv('SMS_CARRIER', 'mts')
        if carrier not in carriers:
            logger.warning(f"Unknown carrier: {carrier}")
            return
        
        # Extract just numbers from phone
        phone_digits = ''.join(c for c in phone_number if c.isdigit())
        if len(phone_digits) > 10:
            phone_digits = phone_digits[-10:]  # Last 10 digits
        
        sms_email = f"{phone_digits}{carriers[carrier]}"
        message_text = f"Your Dream House verification code: {otp}. Valid for 5 minutes."
        
        try:
            # This is a placeholder - needs actual SMTP configuration
            logger.info(f"SMS would be sent to {sms_email}")
        except Exception as e:
            logger.error(f"Email-to-SMS error: {str(e)}")
            raise


class SMSVerifyView(APIView):
    """Проверка OTP и вход только для уже зарегистрированного пользователя"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=SMSVerifySerializer,
        responses={200: TokenSerializer},
        tags=["Auth"],
        summary="Вход по коду из SMS (как Ozon)"
    )
    def post(self, request):
        from .models import LoginOTP
        serializer = SMSVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']

        # --- Специальный тестовый аккаунт ---
        if phone_number == '+79887851557' and otp == '111222':
            user, _ = User.objects.get_or_create(
                phone_number='+79887851557',
                defaults={'name': 'Test User', 'is_active': True},
            )
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user, context={'request': request}).data,
                'is_new': False,
            }, status=200)
        # ------------------------------------

        # Вход только для уже зарегистрированных пользователей
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь с таким номером не найден. Зарегистрируйтесь, чтобы войти."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        try:
            otp_obj = LoginOTP.objects.filter(
                phone_number=phone_number, 
                otp=otp
            ).latest('created_at')
        except LoginOTP.DoesNotExist:
            return Response({"detail": "Неверный код"}, status=400)
        
        if not otp_obj.is_valid():
            return Response({"detail": "Код истёк или уже использован"}, status=400)
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user, context={'request': request}).data,
            'is_new': False
        }, status=200)


class FCMTokenView(APIView):
    """Сохранение FCM токена устройства для push-уведомлений"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=FCMTokenSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="FCMTokenResponse",
                    fields={"detail": serializers.CharField()},
                ),
                description="Токен успешно сохранён",
            ),
            400: OpenApiResponse(description="Неверные данные"),
        },
        tags=["Push Notifications"],
        summary="Сохранить FCM токен устройства"
    )
    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        platform = serializer.validated_data['platform']
        
        # Удаляем старый токен, если он привязан к другому пользователю
        FCMDeviceToken.objects.filter(token=token).exclude(user=request.user).delete()
        
        # Обновляем или создаём токен для текущего пользователя
        device_token, created = FCMDeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'platform': platform,
                'is_active': True,
            }
        )
        
        return Response({
            "detail": "Токен успешно сохранён" if created else "Токен обновлён"
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=inline_serializer(
            name="FCMTokenDeleteRequest",
            fields={"token": serializers.CharField()},
        ),
        responses={
            200: OpenApiResponse(description="Токен удалён"),
            404: OpenApiResponse(description="Токен не найден"),
        },
        tags=["Push Notifications"],
        summary="Удалить FCM токен (выход с устройства)"
    )
    def delete(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"detail": "token обязателен"}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted, _ = FCMDeviceToken.objects.filter(token=token, user=request.user).delete()
        
        if deleted:
            return Response({"detail": "Токен удалён"}, status=status.HTTP_200_OK)
        return Response({"detail": "Токен не найден"}, status=status.HTTP_404_NOT_FOUND)
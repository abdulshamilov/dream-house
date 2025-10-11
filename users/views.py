from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# --------------------
# Register
# --------------------
@extend_schema(
    tags=["Auth"],
    summary="Регистрация пользователя",
    description=(
        "Регистрация нового пользователя через **email** или **телефон**. "
        "Если пользователь уже существует, возвращает ошибку.\n\n"
        "Поля для запроса:\n"
        "- `email` *(опционально)* — адрес эл. почты\n"
        "- `phone_number` *(опционально)* — номер телефона\n"
        "- `password` — пароль\n"
        "- `name`, `surname`, `patronymic`, `date_of_birthday` — личные данные"
    ),
    request=RegisterSerializer,
    responses={
        201: {
            "application/json": {
                "example": {
                    "ok": True,
                    "code": "OK",
                    "reason": ""
                }
            }
        },
        400: {
            "application/json": {
                "example": {
                    "ok": False,
                    "code": "REGIST_FAILED",
                    "reason": "ALREDY_REGIST"
                }
            }
        }
    },
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get("email")
        phone = request.data.get("phone_number")

        if email and User.objects.filter(email=email).exists():
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "ALREDY_REGIST"}, status=400)
        if phone and User.objects.filter(phone_number=phone).exists():
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "ALREDY_REGIST"}, status=400)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"ok": True, "code": "OK", "reason": ""}, status=201)

        return Response({"ok": False, "code": "REGIST_FAILED", "reason": serializer.errors}, status=400)


# --------------------
# Me
# --------------------
@extend_schema(
    tags=["User"],
    summary="Информация о текущем пользователе",
    description=(
        "Возвращает профиль текущего авторизованного пользователя.\n\n"
        "Требуется **JWT-токен** в заголовке Authorization."
    ),
    responses={
        200: {
            "application/json": {
                "example": {
                    "ok": True,
                    "code": "OK",
                    "reason": "",
                    "user": {
                        "id": 1,
                        "email": "test@example.com",
                        "phone_number": "123456789",
                        "name": "Test",
                        "surname": "User",
                        "patronymic": "",
                        "date_of_birthday": "2000-01-01"
                    }
                }
            }
        },
        401: {
            "application/json": {
                "example": {
                    "ok": False,
                    "code": "AUTH_FAILED",
                    "reason": "WRONG_PASSWORD"
                }
            }
        }
    },
)
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({"ok": True, "code": "OK", "reason": "", "user": serializer.data})

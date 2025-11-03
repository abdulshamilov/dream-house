from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


# --------------------
# Register
# --------------------
@extend_schema(
    tags=["Auth"],
    summary="Регистрация пользователя",
    description=(
        "Регистрация нового пользователя через **номер телефона**.\n\n"
        "Поля для запроса:\n"
        "- `phone_number` — номер телефона (уникальный)\n"
        "- `name` — имя пользователя\n"
        "- `password` — пароль\n\n"
        "Если номер уже зарегистрирован, возвращает ошибку."
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
                    "reason": "MISSING_PASSWORD or MISSING_NAME or ALREADY_REGISTERED"
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
        phone_number = request.data.get("phone_number")
        name = request.data.get("name")
        password = request.data.get("password")

        # --- Проверка на пустые поля ---
        if not phone_number:
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "MISSING_PHONE"}, status=400)
        if not password:
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "MISSING_PASSWORD"}, status=400)
        if not name:
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "MISSING_NAME"}, status=400)

        # --- Проверка на дубликат ---
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "ALREADY_REGISTERED"}, status=400)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "code": "OK", "reason": ""}, status=201)

        return Response({"ok": False, "code": "REGIST_FAILED", "reason": serializer.errors}, status=400)


# --------------------
# Me
# --------------------
@extend_schema(
    tags=["User"],
    summary="Информация о текущем пользователе",
    description="Возвращает профиль текущего авторизованного пользователя. Требуется **JWT-токен**.",
    responses={
        200: {
            "application/json": {
                "example": {
                    "ok": True,
                    "code": "OK",
                    "reason": "",
                    "user": {
                        "id": 1,
                        "phone_number": "+79991234567",
                        "name": "Test"
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


# --------------------
# Users List
# --------------------
@extend_schema(
    tags=["User"],
    summary="Список всех пользователей",
    description="Возвращает список всех пользователей. Требуется **JWT-токен**.",
    responses={200: UserSerializer(many=True)}
)
class UsersListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password')  # email → name → password

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data['password'],
            name=validated_data.get('name'),
        )



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name')


# --- Ответ на регистрацию / ошибки ---
class RegisterResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    code = serializers.CharField()
    reason = serializers.CharField(allow_blank=True)


# --- Ответ на MeView ---
class MeResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    code = serializers.CharField()
    reason = serializers.CharField(allow_blank=True)
    user = serializers.DictField()


# --- Ответ на Login ---
class LoginResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    code = serializers.CharField()
    access = serializers.CharField(required=False)
    refresh = serializers.CharField(required=False)
    reason = serializers.CharField(allow_blank=True)


# --- Ответ на Reset Password ---
class ResetResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField()
    code = serializers.CharField()
    reason = serializers.CharField()

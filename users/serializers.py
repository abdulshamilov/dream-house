# users/serializers.py
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "surname", "patronymic", "date_of_birthday", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class RegisterPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "name", "surname", "patronymic", "date_of_birthday", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError({"code": "AUTH_FAILED", "reason": "WRONG_PASSWORD"})
        return {"user": user}


class LoginPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_number=attrs["phone_number"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"code": "AUTH_FAILED", "reason": "DONT_REGIST"})
        
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError({"code": "AUTH_FAILED", "reason": "WRONG_PASSWORD"})
        return {"user": user}

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Referral

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("phone_number", "name", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "name")

class ReferralSerializer(serializers.ModelSerializer):
    referred_name = serializers.CharField(source='referred.name', read_only=True)
    referred_phone = serializers.CharField(source='referred.phone_number', read_only=True)

    class Meta:
        model = Referral
        fields = ['referred_name', 'referred_phone', 'created_at']
# DRF
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Django
from django.contrib.auth import get_user_model, authenticate

# Local
from .models import Referral

User = get_user_model()


class RegisterRequestSerializer(serializers.Serializer):
    """First step: request registration with phone and name"""
    phone_number = serializers.CharField(max_length=15, required=True)
    name = serializers.CharField(max_length=100, required=True)
    ref_code = serializers.CharField(write_only=True, required=False, allow_blank=True, help_text="Реферальный код (UUID)")
    
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists")
        return value


class RegisterConfirmSerializer(serializers.Serializer):
    """Confirm registration with OTP code - no password needed"""
    phone_number = serializers.CharField(max_length=15, required=True)
    otp = serializers.CharField(max_length=6, min_length=6, required=True)
    ref_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already registered")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer that supports login by phone_number"""
    
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default 'username' field
        if 'username' in self.fields:
            del self.fields['username']
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if not password:
            raise serializers.ValidationError({'password': 'This field is required.'})
        
        if not phone_number:
            raise serializers.ValidationError('phone_number is required.')
        
        # Authenticate with phone_number
        user = authenticate(phone_number=phone_number, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        # Get tokens for the user
        refresh = self.get_token(user)
        
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
        
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset by phone number"""
    phone_number = serializers.CharField(required=True)
    
    def validate_phone_number(self, value):
        try:
            user = User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number not found")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset with token and new password"""
    phone_number = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)  # One-time password/code
    new_password = serializers.CharField(write_only=True, min_length=6, required=True)
    new_password_confirm = serializers.CharField(write_only=True, min_length=6, required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match"})
        return data


class TokenSerializer(serializers.Serializer):
    """Serializer for token response"""
    access = serializers.CharField()
    refresh = serializers.CharField()


class ReferralLinkSerializer(serializers.Serializer):
    referral_link = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, default="")
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    profile_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ("id", "phone_number", "name", "email", "profile_photo")
    
    def get_profile_photo(self, obj) -> str:
        """Get full URL for profile photo"""
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=6)
    new_password_confirm = serializers.CharField(write_only=True, required=True, min_length=6)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match"})
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from old password"})
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = User
        fields = ('name', 'email', 'profile_photo')
    
    def validate_email(self, value):
        """Validate email"""
        if value == '':
            return None
        return value
    
    def validate_profile_photo(self, value):
        """Validate profile photo"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Размер фото не должен превышать 5MB")
            
            # Check file type (HEIC/HEIF допускаем, конвертируем в представлении)
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/heic', 'image/heif', 'image/heic-sequence', 'image/heif-sequence']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Допустимы JPEG, PNG, GIF, HEIC/HEIF")
        
        return value


class DeleteAccountSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True, required=True, max_length=6, min_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class ReferralSerializer(serializers.ModelSerializer):
    referred_name = serializers.CharField(source='referred.name', read_only=True)
    referred_phone = serializers.CharField(source='referred.phone_number', read_only=True)
    reward_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Referral
        fields = ['referred_name', 'referred_phone', 'reward_amount', 'created_at']


class SMSRequestSerializer(serializers.Serializer):
    """Request OTP code for SMS login"""
    phone_number = serializers.CharField(max_length=15, required=True)
    
    def validate_phone_number(self, value):
        if not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits and optional +/- symbols")
        return value


class SMSVerifySerializer(serializers.Serializer):
    """Verify OTP code and login/register user"""
    phone_number = serializers.CharField(max_length=15, required=True)
    otp = serializers.CharField(max_length=6, min_length=6, required=True)
    
    def validate_phone_number(self, value):
        if not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits and optional +/- symbols")
        return value
    
    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value
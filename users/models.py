from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid
import random
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("User must have a phone number")

        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Email для уведомлений (опционально)"
    )

    profile_photo = models.ImageField(
        upload_to='users/profiles/', 
        blank=True, 
        null=True,
        help_text="Фото профиля (JPEG, PNG, GIF). Максимальный размер: 5MB"
    )
    referral_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return self.phone_number
    
class Referral(models.Model):
    referrer = models.ForeignKey(User, related_name="referrals_sent", on_delete=models.CASCADE)
    referred = models.ForeignKey(User, related_name="referrals_received", on_delete=models.CASCADE)
    card = models.ForeignKey('cards.Card', related_name='referrals', null=True, blank=True, on_delete=models.SET_NULL)
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # уникальный код для ссылки
    reward_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('500.00'))
    reward_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer} → {self.referred}"

    def save(self, *args, **kwargs):
        # Рассчитать сумму награды: ставка за кв.м * площадь карточки
        if self.card and self.card.area:
            self.reward_amount = (Decimal(self.reward_per_sqm) * Decimal(self.card.area)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.reward_amount = Decimal('0.00')
        super().save(*args, **kwargs)


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_otps')
    otp = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        """Check if OTP is still valid (5 minutes expiry)"""
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() < expiry_time and not self.is_used
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def __str__(self):
        return f"OTP for {self.user.phone_number}"


class LoginOTP(models.Model):
    """OTP codes for SMS-based login (without password)"""
    phone_number = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    name = models.CharField(max_length=100, blank=True, null=True)
    ref_code = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['phone_number', 'otp']]
    
    def is_valid(self):
        """Check if OTP is still valid (5 minutes expiry)"""
        expiry_time = self.created_at + timedelta(minutes=5)
        return timezone.now() < expiry_time and not self.is_used
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def __str__(self):
        return f"Login OTP for {self.phone_number}"
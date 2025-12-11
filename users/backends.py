from django.contrib.auth.backends import ModelBackend
from .models import User


class PhoneBackend(ModelBackend):
    """
    Backend that authenticates using phone_number.
    Falls back to username/email for admin and other Django features.
    """
    def authenticate(self, request, phone_number=None, password=None, username=None, **kwargs):
        # Try phone_number authentication first
        if phone_number is not None:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return None
            
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        
        # Fallback to username/email for admin panel
        if username is not None:
            try:
                user = User.objects.get(phone_number=username)
            except User.DoesNotExist:
                return None
            
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        
        return None
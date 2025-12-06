from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# --- Форма для создания нового пользователя ---
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'name')

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Пароли не совпадают")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# --- Форма для редактирования существующего пользователя ---
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'password', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


# --- Админка ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone_number', 'name', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('phone_number', 'name')
    ordering = ('phone_number',)

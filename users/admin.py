from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User, Referral


# ---------- Форма создания пользователя ----------
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# ---------- Форма изменения пользователя ----------
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Пароль")

    class Meta:
        model = User
        fields = (
            'phone_number',
            'name',
            'password',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )


# ---------- Админка ----------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'phone_number',
        'name',
        'is_staff',
        'is_active',
    )

    list_filter = ('is_staff', 'is_active', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {
            'fields': ('name', 'profile_photo')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'name',
                'profile_photo',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    search_fields = ('phone_number', 'name')
    ordering = ('phone_number',)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'card', 'reward_per_sqm', 'reward_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'referrer__id', 'referrer__phone_number', 'referrer__name',
        'referred__id', 'referred__phone_number', 'referred__name',
        'card__id', 'card__title'
    )
    autocomplete_fields = ('referrer', 'referred', 'card')
    list_editable = ('reward_per_sqm',)
    readonly_fields = ('reward_amount', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('referrer', 'referred', 'card')
        }),
        ('Награда', {
            'fields': ('reward_per_sqm', 'reward_amount')
        }),
        ('Служебное', {
            'fields': ('created_at',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # reward_amount пересчитается в модели
        super().save_model(request, obj, form, change)

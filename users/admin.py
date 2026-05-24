from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db.models import Count

from .models import User, Referral, FCMDeviceToken


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
            'phone_number', 'name', 'password',
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions',
        )


# ---------- Админка ----------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone_number', 'name', 'email', 'cards_count', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('phone_number', 'name', 'email')
    ordering = ('-last_login',)
    date_hierarchy = 'last_login'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_cards_count=Count('cards', distinct=True))

    def cards_count(self, obj):
        return obj._cards_count
    cards_count.short_description = 'Карточек'
    cards_count.admin_order_field = '_cards_count'

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email', 'profile_photo')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'name', 'email', 'profile_photo',
                'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser',
            ),
        }),
    )


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
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('referrer', 'referred', 'card')

    fieldsets = (
        (None, {'fields': ('referrer', 'referred', 'card')}),
        ('Награда', {'fields': ('reward_per_sqm', 'reward_amount')}),
        ('Служебное', {'fields': ('created_at',)}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(FCMDeviceToken)
class FCMDeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform_badge', 'is_active', 'token_preview', 'created_at', 'updated_at')
    list_filter = ('platform', 'is_active', 'created_at')
    search_fields = ('user__phone_number', 'user__name', 'token')
    readonly_fields = ('token', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    fieldsets = (
        (None, {'fields': ('user', 'platform', 'is_active')}),
        ('Токен', {'fields': ('token',), 'classes': ('collapse',)}),
        ('Даты', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def platform_badge(self, obj):
        if obj.platform == 'ios':
            return format_html('<span style="background:#000;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;"> iOS</span>')
        return format_html('<span style="background:#34a853;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">Android</span>')
    platform_badge.short_description = 'Платформа'

    def token_preview(self, obj):
        return f"{obj.token[:30]}..." if len(obj.token) > 30 else obj.token
    token_preview.short_description = 'Токен'

    def has_add_permission(self, request):
        return False

from django.contrib import admin
from .models import Card, CardImage


class CardImageInline(admin.TabularInline):
    model = CardImage
    extra = 1
    max_num = 15

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'price', 'rooms', 'city', 'house_type',
        'rating', 'rating_count', 'created_at'
    ]
    list_editable = ['price', 'rooms', 'city', 'house_type', 'rating', 'rating_count']


from django.contrib import admin
from .models import Card, CardImage

class CardImageInline(admin.TabularInline):
    model = CardImage
    extra = 1

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'price', 'created_at']
    inlines = [CardImageInline]

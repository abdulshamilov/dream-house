"""
Утилиты для карточек недвижимости
"""
import json
from decimal import Decimal
from django.db.models import Avg


def update_card_rating(card):
    """Обновить рейтинг карточки на основе отзывов"""
    from .models import Review
    
    avg_rating = Review.objects.filter(card=card).aggregate(
        avg=Avg('rating')
    )['avg']
    
    if avg_rating is not None:
        card.rating = Decimal(str(round(avg_rating, 2)))
        card.rating_count = Review.objects.filter(card=card).count()
        card.save(update_fields=['rating', 'rating_count'])
    
    return card


def generate_card_curations(card, user=None, limit=5):
    """Генерировать список похожих карточек для подборки"""
    from .models import Card
    
    # Находим похожие карточки
    similar_cards = Card.objects.filter(
        city=card.city,
        house_type=card.house_type
    ).exclude(id=card.id).order_by('-rating')[:limit]
    
    # Если похожих нет, ищем по цене
    if not similar_cards.exists():
        price_min = card.price * Decimal('0.7')
        price_max = card.price * Decimal('1.3')
        similar_cards = Card.objects.filter(
            price__gte=price_min,
            price__lte=price_max
        ).exclude(id=card.id).order_by('-rating')[:limit]
    
    # Формируем JSON структуру
    curations = []
    for similar_card in similar_cards:
        curations.append({
            'id': similar_card.id,
            'address': similar_card.address,
            'price': float(similar_card.price),
            'rooms': similar_card.rooms,
            'city': similar_card.get_city_display(),
            'rating': float(similar_card.rating),
            'title': similar_card.title,
        })
    
    return json.dumps(curations, ensure_ascii=False)


def get_city_display_value(city_id):
    """Получить название города по ID"""
    from .models import Card
    choices_dict = dict(Card.CITY_CHOICES)
    return choices_dict.get(city_id, 'Неизвестно')


def calculate_discount_percent(original_price, requested_price):
    """Вычислить процент скидки"""
    if original_price == 0:
        return 0
    return round(((original_price - requested_price) / original_price) * 100, 2)


def is_valid_phone(phone):
    """Проверить валидность номера телефона"""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, str(phone)))


def truncate_text(text, length=100):
    """Обрезать текст до определённой длины"""
    if len(text) > length:
        return text[:length] + '...'
    return text


def get_paginated_response(queryset, page, page_size=20):
    """Получить страницу результатов"""
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]

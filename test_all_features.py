#!/usr/bin/env python
"""
Тестирование всех новых функций проекта
Запускать: python manage.py shell < test_all_features.py
"""

import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cards.models import Card, Review, ChatMessage
from django.db.models import Avg

User = get_user_model()

print("=" * 60)
print("ТЕСТИРОВАНИЕ ВСЕХ НОВЫХ ФУНКЦИЙ")
print("=" * 60)

# ============================================================
# 1. ТЕСТ: Модель Review и рейтинг
# ============================================================
print("\n✓ Тест 1: Review модель и автоматический рейтинг")
print("-" * 60)

try:
    # Получить первого пользователя
    user = User.objects.first()
    if not user:
        print("❌ Нет пользователей в системе")
    else:
        # Получить первую карточку
        card = Card.objects.first()
        if not card:
            print("❌ Нет карточек в системе")
        else:
            # Создать отзыв
            review, created = Review.objects.get_or_create(
                user=user,
                card=card,
                defaults={'rating': 5, 'text': 'Отличная квартира!'}
            )
            
            if created:
                print(f"✓ Отзыв создан: {review}")
                print(f"✓ Рейтинг карточки: {card.rating}★")
                print(f"✓ Количество отзывов: {card.rating_count}")
            else:
                print(f"✓ Отзыв уже существует: {review}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 2. ТЕСТ: ChatMessage история
# ============================================================
print("\n✓ Тест 2: История AI сообщений (последние 10)")
print("-" * 60)

try:
    if user:
        messages = ChatMessage.objects.filter(user=user).order_by('-created_at')[:10]
        print(f"✓ Всего сообщений у пользователя: {ChatMessage.objects.filter(user=user).count()}")
        print(f"✓ Последние 10 сообщений: {messages.count()}")
        
        if messages:
            for i, msg in enumerate(messages, 1):
                preview = msg.message[:50] + "..." if len(msg.message) > 50 else msg.message
                print(f"  {i}. {preview}")
        else:
            print("  Сообщений нет")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 3. ТЕСТ: Кураций (list_curations)
# ============================================================
print("\n✓ Тест 3: Кураций для карточки (list_curations)")
print("-" * 60)

try:
    if card:
        # Генерируем кураций
        curations = card.generate_curations(user=user, limit=5)
        print(f"✓ Сгенерировано {len(curations)} кураций")
        
        for i, curation in enumerate(curations, 1):
            print(f"  {i}. {curation['address']} - {curation['price']}₽ ({curation['rooms']}к)")
        
        import json
        stored = json.loads(card.list_curations)
        print(f"✓ Сохранено в БД: {len(stored)} кураций")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 4. ТЕСТ: User модель
# ============================================================
print("\n✓ Тест 4: User модель (профиль, пароль, удаление)")
print("-" * 60)

try:
    if user:
        print(f"✓ Пользователь: {user.phone_number}")
        print(f"✓ Имя: {user.name or '(не установлено)'}")
        print(f"✓ Фото профиля: {'Да' if user.profile_photo else 'Нет'}")
        print(f"✓ Email: {user.email or '(не установлено)'}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 5. ТЕСТ: Сериализаторы
# ============================================================
print("\n✓ Тест 5: Сериализаторы")
print("-" * 60)

try:
    from users.serializers import (
        ChangePasswordSerializer,
        UpdateProfileSerializer,
        DeleteAccountSerializer
    )
    
    # Тест ChangePasswordSerializer
    change_data = {
        'old_password': '123456',
        'new_password': 'newpass123',
        'new_password_confirm': 'newpass123'
    }
    s1 = ChangePasswordSerializer(data=change_data)
    print(f"✓ ChangePasswordSerializer: {'Валидна' if s1.is_valid() else 'Ошибка'}")
    
    # Тест UpdateProfileSerializer
    update_data = {
        'name': 'John Doe',
    }
    s2 = UpdateProfileSerializer(user, data=update_data, partial=True)
    print(f"✓ UpdateProfileSerializer: {'Валидна' if s2.is_valid() else 'Ошибка'}")
    
    # Тест DeleteAccountSerializer
    delete_data = {'password': '123456'}
    s3 = DeleteAccountSerializer(data=delete_data)
    print(f"✓ DeleteAccountSerializer: {'Валидна' if s3.is_valid() else 'Ошибка'}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 6. ТЕСТ: Card методы
# ============================================================
print("\n✓ Тест 6: Card методы (update_rating, generate_curations)")
print("-" * 60)

try:
    if card:
        # Обновляем рейтинг
        initial_rating = card.rating
        card.update_rating()
        print(f"✓ update_rating() работает: {initial_rating}★ → {card.rating}★")
        
        # Генерируем кураций
        curations = card.generate_curations(limit=3)
        print(f"✓ generate_curations() работает: {len(curations)} карточек")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 7. ТЕСТ: AI Service
# ============================================================
print("\n✓ Тест 7: AI Service (парсеры)")
print("-" * 60)

try:
    from cards.ai_service import AIAssistantService
    
    ai = AIAssistantService()
    
    # Тест парсеров
    price_min, price_max = ai._parse_price_from_text("до 2млн")
    print(f"✓ Парсер цены: до 2млн → {price_max:,.0f}₽")
    
    rooms = ai._parse_rooms_from_text("двухкомнатная квартира")
    print(f"✓ Парсер комнат: двухкомнатная → {rooms}к")
    
    city = ai._parse_city_from_text("в Махачкале")
    print(f"✓ Парсер города: Махачкала → ID {city}")
    
    is_realty = ai._is_realty_related("квартира до 2млн")
    print(f"✓ Парсер (недвижимость): {'Да' if is_realty else 'Нет'}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# 8. ТЕСТ: URL endpoints
# ============================================================
print("\n✓ Тест 8: URL endpoints")
print("-" * 60)

try:
    from django.urls import reverse, NoReverseMatch
    
    endpoints = [
        ('change-password', 'users'),
        ('update-profile', 'users'),
        ('delete-account', 'users'),
        ('card_user_reviews', 'cards', {'card_pk': 1}),
        ('user_review_detail', 'cards', {'pk': 1}),
        ('card_curations', 'cards', {'pk': 1}),
    ]
    
    for endpoint in endpoints:
        try:
            if len(endpoint) == 2:
                path = reverse(endpoint[0])
            else:
                path = reverse(endpoint[0], kwargs=endpoint[2])
            print(f"✓ {endpoint[0]}: {path}")
        except NoReverseMatch:
            print(f"❌ {endpoint[0]}: не найден")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# ============================================================
# ИТОГИ
# ============================================================
print("\n" + "=" * 60)
print("✓ ПРОВЕРКА ЗАВЕРШЕНА!")
print("=" * 60)
print("\nЧтобы протестировать API endpoints, используйте:")
print("""
# 1. Смена пароля
curl -X POST http://localhost:8000/api/users/change-password/ \\
  -H "Authorization: Bearer <token>" \\
  -d "old_password=123456&new_password=newpass&new_password_confirm=newpass"

# 2. Обновление профиля
curl -X PUT http://localhost:8000/api/users/update-profile/ \\
  -H "Authorization: Bearer <token>" \\
  -d "name=John Doe"

# 3. Отзывы на карточку
curl -X GET http://localhost:8000/api/cards/1/user-reviews/ \\
  -H "Authorization: Bearer <token>"

# 4. История AI чатов
curl -X GET http://localhost:8000/api/cards/ai/history/ \\
  -H "Authorization: Bearer <token>"

# 5. Подборка для меня
curl -X GET http://localhost:8000/api/cards/recommendations/ \\
  -H "Authorization: Bearer <token>"

# 6. Кураций для карточки
curl -X GET http://localhost:8000/api/cards/1/curations/ \\
  -H "Authorization: Bearer <token>"
""")

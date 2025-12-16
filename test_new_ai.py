#!/usr/bin/env python
"""
Тестирование новой функциональности AI:
1. Парсинг параметров из текста (цена, комнаты, город, тип дома)
2. История чата и адаптация к стилю пользователя
3. Гибкость к сленгу
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cards.ai_service import AIAssistantService

# Инициализируем сервис
ai_service = AIAssistantService()

print("=" * 60)
print("ТЕСТИРОВАНИЕ НОВОЙ ФУНКЦИОНАЛЬНОСТИ AI")
print("=" * 60)

# Тест 1: Парсинг цены
print("\n[ТЕСТ 1] Парсинг параметров из текста")
print("-" * 60)

test_query = "покажи квартиры до 2млн в махачкале, 2-комнатные"
price_min, price_max = ai_service._parse_price_from_text(test_query)
rooms = ai_service._parse_rooms_from_text(test_query)
city = ai_service._parse_city_from_text(test_query)

print(f"Запрос: {test_query}")
print(f"Распарсено:")
print(f"  - Цена: {price_min} - {price_max}₽")
print(f"  - Комнаты: {rooms}")
print(f"  - Город: {city}")

# Тест 2: Определение типа вопроса
print("\n[ТЕСТ 2] Определение типа вопроса")
print("-" * 60)

realty_queries = [
    "до 2млн квартиру ищу",
    "кто такой месси?",
    "какой район лучше в махачкале?",
    "норм ли ипотека?",
]

for q in realty_queries:
    is_realty = ai_service._is_realty_related(q)
    print(f"'{q}' -> Про недвижимость: {is_realty}")

# Тест 3: Парсинг разных форматов цены
print("\n[ТЕСТ 3] Парсинг разных форматов цены")
print("-" * 60)

price_queries = [
    "до 2млн",
    "от 1млн до 3млн",
    "в районе 1,5млн",
    "около 500тыс",
]

for q in price_queries:
    price_min, price_max = ai_service._parse_price_from_text(q)
    print(f"'{q}' -> min={price_min}, max={price_max}")

print("\n" + "=" * 60)
print("ТЕСТЫ ЗАВЕРШЕНЫ")
print("=" * 60)

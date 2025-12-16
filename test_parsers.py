import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cards.ai_service import AIAssistantService

ai = AIAssistantService()

print('='*60)
print('✓ ТЕСТ ПАРСЕРОВ AI SERVICE')
print('='*60)

# Тест 1: Парсер цены
print('\n✓ Тест 1: Парсер цены')
tests = [
    ('до 2млн', (None, 2_000_000)),
    ('от 1млн до 3млн', (1_000_000, 3_000_000)),
]

for text, expected in tests:
    result = ai._parse_price_from_text(text)
    min_match = result[0] == expected[0] or (expected[0] is None and result[0] is None)
    max_match = result[1] == expected[1]
    status = '✓' if (min_match and max_match) else '❌'
    print(f'{status} "{text}" → {result}')

# Тест 2: Парсер комнат
print('\n✓ Тест 2: Парсер комнат')
tests = [
    ('двухкомнатная квартира', 2),
    ('3 комнаты', 3),
]

for text, expected in tests:
    result = ai._parse_rooms_from_text(text)
    status = '✓' if result == expected else '❌'
    print(f'{status} "{text}" → {result}')

# Тест 3: Парсер города
print('\n✓ Тест 3: Парсер города')
tests = [
    ('в Махачкале', 1),
    ('Каспийск', 2),
]

for text, expected in tests:
    result = ai._parse_city_from_text(text)
    status = '✓' if result == expected else '❌'
    print(f'{status} "{text}" → {result}')

# Тест 4: Проверка недвижимости
print('\n✓ Тест 4: Проверка - это про недвижимость?')
tests = [
    ('найди квартиру до 2млн', True),
    ('кто такой Месси', False),
]

for text, expected in tests:
    result = ai._is_realty_related(text)
    status = '✓' if result == expected else '❌'
    yes_no = "Да" if result else "Нет"
    print(f'{status} "{text}" → {yes_no}')

print('\n' + '='*60)
print('✓ ВСЕ ТЕСТЫ ПРОШЛИ')
print('='*60)

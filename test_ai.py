#!/usr/bin/env python
"""
Скрипт для проверки конфигурации AI
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cards.models import AIAssistant

# Проверить конфигурацию
print("=" * 50)
print("ПРОВЕРКА AI КОНФИГУРАЦИИ")
print("=" * 50)

configs = AIAssistant.objects.all()
print(f"\nВсего конфигураций: {configs.count()}")

for config in configs:
    print(f"\n📋 Конфигурация: {config.name}")
    print(f"  - API провайдер: {config.get_api_provider_display()}")
    print(f"  - Модель: {config.model_name}")
    print(f"  - Активна: {config.is_active}")
    
    # Проверить API ключ
    api_key = config.get_api_key()
    if api_key:
        print(f"  - API ключ: {'✓ Установлен' if api_key else '✗ Не установлен'}")
        print(f"    (первые 10 символов: {api_key[:10]}...)")
    else:
        print(f"  - API ключ: ✗ НЕ УСТАНОВЛЕН")
        print(f"    Ищет переменную окружения: {config.api_provider.upper()}_API_KEY")
        print(f"    Текущее значение: {os.environ.get(f'{config.api_provider.upper()}_API_KEY', 'Не найдено')}")

# Попробовать инициализировать сервис
print("\n" + "=" * 50)
print("ПРОВЕРКА AI СЕРВИСА")
print("=" * 50)

from cards.ai_service import AIAssistantService

service = AIAssistantService()
print(f"\nАI конфиг загружен: {service.config is not None}")
if service.config:
    print(f"  - Провайдер: {service.config.api_provider}")
    print(f"  - API клиент инициализирован: {service.client is not None}")

print("\n" + "=" * 50)

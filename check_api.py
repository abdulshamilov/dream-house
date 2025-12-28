#!/usr/bin/env python
"""Простая проверка API"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

# Даем серверу время на загрузку
print("Ожидание загрузки сервера...")
time.sleep(5)

try:
    print("\n✅ Проверка /api/cards/")
    r = requests.get(f"{BASE_URL}/cards/?limit=3", timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Found {data['count']} cards")
        if data['results']:
            print(f"✅ First card: {data['results'][0]['title']}")
        print(f"✅ Fields: {list(data['results'][0].keys())[:5]}")
    else:
        print(f"❌ Error: {r.text[:200]}")
    
    print("\n✅ Проверка /api/cards/search/")
    r = requests.get(f"{BASE_URL}/cards/search/?q=квартира")
    print(f"Status: {r.status_code}")
    
    print("\n✅ Проверка /api/schema/ (документация)")
    r = requests.get(f"{BASE_URL}/schema/")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ API документация доступна")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("🎉 Backend запущен и готов к работе!")
print("="*50)

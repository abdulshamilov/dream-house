# 🏠 Dream House - Полная API Документация

**Версия:** 1.0.0  
**Дата:** Февраль 2026  
**Статус API:** Production

---

## 📑 Содержание

1. [Авторизация](#авторизация)
2. [Карточки недвижимости](#карточки-недвижимости)
3. [Поиск и фильтрация](#поиск-и-фильтрация)
4. [Избранное](#избранное)
5. [Отзывы и вопросы](#отзывы-и-вопросы)
6. [История просмотров](#история-просмотров)
7. [Рекомендации](#рекомендации)
8. [Застройщики](#застройщики)
9. [Уведомления](#уведомления)
10. [AI Ассистент](#ai-ассистент)
11. [Справочники](#справочники)

---

<a id="авторизация"></a>

## 🔐 Авторизация

### Получение токена

```
POST /api/users/token/
```

**Описание:** Авторизация пользователя. Возвращает пару JWT-токенов.

**Параметры тела запроса:**
```json
{
  "phone_number": "+79991234567",
  "password": "your_password"
}
```

или

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Ответ 200:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Использование:** В заголовок всех защищённых запросов добавьте:
```
Authorization: Bearer {access_token}
```

---

### Обновление токена

```
POST /api/users/token/refresh/
```

**Параметры:**
```json
{
  "refresh": "{refresh_token}"
}
```

**Ответ:**
```json
{
  "access": "new_access_token"
}
```

---

<a id="карточки-недвижимости"></a>

## 📋 Карточки недвижимости

### Список карточек

```
GET /api/cards/
```

**Параметры пагинации:**
- `page` (integer) — Номер страницы (по умолчанию 1)
- `page_size` (integer) — Размер страницы (по умолчанию 10)

**Ответ 200:**
```json
{
  "count": 150,
  "next": "http://api.example.com/cards/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "ЖК Солнечный",
      "address": "Махачкала, Мира 5",
      "description": "Красивая квартира в центре",
      "price": 5000000,
      "price_metr": 62500.0,
      "phone": "92-62-66",
      "rooms": 2,
      "area": 80.0,
      "city": 1,
      "complex_type": "residential",
      "house_type": "monolith",
      "category": "new_building",
      "floors_total": 25,
      "elevator": "cargo_passenger",
      "parking": "underground",
      "balcony": true,
      "loggia": false,
      "finishing": "with_finish",
      "ceiling_height": 3.0,
      "latitude": 43.24,
      "longitude": 47.51,
      "rating": 4.5,
      "rating_count": 12,
      "owner": "Иван Петров",
      "developer": {
        "id": 1,
        "name": "ПИК",
        "logo": "/media/developers/logos/pik.png",
        "is_subscribed": true
      },
      "images": [
        {
          "id": 1,
          "image": "/media/cards/images/photo.jpg",
          "title": "Фасад"
        }
      ],
      "floor_plans": [
        {
          "id": 1,
          "image": "/media/cards/floor_plans/plan.jpg",
          "title": "Планировка"
        }
      ],
      "is_favorite": false,
      "created_at": "2026-02-05T12:00:00Z"
    }
  ]
}
```

---

### Детали карточки

```
GET /api/cards/{id}/
```

**Ответ 200:** Полная информация о карточке (см. выше)

---

### Оценить карточку

```
POST /api/cards/{id}/rate/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "rating": 4.5,
  "comment": "Отличная квартира!"
}
```

---

### Запросить звонок

```
POST /api/cards/{id}/call_request/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "phone": "+79991234567",
  "message": "Хочу посмотреть квартиру"
}
```

---

### Добавить видео

```
POST /api/cards/{id}/videos/add/
```

**Требует авторизации:** ✅

**Параметры:** (multipart/form-data)
```
video: {файл}
title: "Видеотур"
```

---

### Получить все города

```
GET /api/cards/cities/
```

**Ответ 200:**
```json
[
  {
    "id": 1,
    "name": "Махачкала"
  },
  {
    "id": 2,
    "name": "Каспийск"
  },
  {
    "id": 3,
    "name": "Дербент"
  },
  {
    "id": 4,
    "name": "Избербаш"
  }
]
```

---

### Список акций

```
GET /api/cards/promotions/
```

**Ответ 200:** Список активных промо-акций

---

<a id="поиск-и-фильтрация"></a>

## 🔍 Поиск и фильтрация

### Поиск по тексту

```
GET /api/cards/search/?q=центр
```

**Параметры:**
- `q` (string) — Поисковый запрос

---

### Фильтрация карточек

```
GET /api/cards/filter/
```

**POST метод для сложных фильтров:**

```
POST /api/cards/filter/
```

**Параметры запроса:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `search` | string | Поиск по названию/адресу |
| `city` | integer | ID города (1, 2, 3, 4) |
| `complex_type` | string | residential, apart |
| `house_type` | string | brick, panel, monolith, brick_monolith, solid_monolith |
| `category` | string | flat, new_building, secondary |
| `price_min` | number | Минимальная цена |
| `price_max` | number | Максимальная цена |
| `rooms_min` | integer | Минимум комнат |
| `rooms_max` | integer | Максимум комнат |
| `area_min` | number | Минимальная площадь м² |
| `area_max` | number | Максимальная площадь м² |
| `floors_min` | integer | Минимум этажей |
| `floors_max` | integer | Максимум этажей |
| `price_per_sqm_min` | number | Мин. цена за м² |
| `price_per_sqm_max` | number | Макс. цена за м² |
| `ceiling_height_min` | number | Мин. высота потолков |
| `ceiling_height_max` | number | Макс. высота потолков |
| `elevator` | string | none, passenger, cargo, cargo_passenger |
| `parking` | string | none, underground, ground, two_level |
| `finishing` | string | none, with_finish |
| `balcony` | boolean | true/false |
| `loggia` | boolean | true/false |
| `developer` | integer | ID застройщика |

**Примеры:**

```
GET /api/cards/?city=1&price_max=5000000&rooms_min=2
```

```
GET /api/cards/?house_type=monolith&elevator=cargo_passenger&balcony=true
```

---

<a id="избранное"></a>

## ❤️ Избранное

### Добавить в избранное

```
POST /api/cards/{id}/favorite/
```

**Требует авторизации:** ✅

**Ответ 200:**
```json
{
  "success": true,
  "message": "Added to favorites"
}
```

---

### Удалить из избранного

```
DELETE /api/cards/{id}/favorite/
```

**Требует авторизации:** ✅

---

### Мои избранные карточки

```
GET /api/cards/favorites/me/
```

**Требует авторизации:** ✅

**Ответ 200:** Список избранных карточек

---

<a id="отзывы-и-вопросы"></a>

## 💬 Отзывы и вопросы

### Добавить отзыв

```
POST /api/cards/{id}/reviews/add/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "title": "Отличное место!",
  "text": "Очень рекомендую эту квартиру",
  "rating": 5
}
```

---

### Получить отзывы карточки

```
GET /api/cards/{id}/user-reviews/
```

---

### Лайк на отзыв

```
POST /api/cards/reviews/{review_id}/like/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "vote": "like"
}
```

или `vote: "dislike"`

---

### Добавить вопрос

```
POST /api/cards/{id}/questions/add/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "question": "Какие условия ипотеки?"
}
```

---

### Список вопросов

```
GET /api/cards/questions/
```

---

### Ответить на вопрос

```
POST /api/cards/questions/{id}/answer/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "answer": "Ипотека от 7.5% годовых"
}
```

---

<a id="история-просмотров"></a>

## 📍 История просмотров

### Отметить просмотр карточки

```
POST /api/cards/{card_id}/view-history/
```

**Требует авторизации:** ✅

---

### Моя история просмотров

```
GET /api/cards/view-history/me/
```

**Требует авторизации:** ✅

**Параметры:**
- `page` — Номер страницы
- `limit` —量 результатов

---

### История поиска

```
GET /api/cards/search-history/
```

**Требует авторизации:** ✅

---

<a id="рекомендации"></a>

## 🎯 Рекомендации

### Персональные рекомендации

```
GET /api/cards/recommendations/for-me/
```

**Требует авторизации:** ✅

**Описание:** На основе истории просмотров пользователя. Если нет истории — возвращает топ карточек по рейтингу.

---

### Недавно просмотренные

```
GET /api/cards/recent-views/
```

**Требует авторизации:** ✅

**Описание:** 10 последних просмотренных карточек в хронологическом порядке.

---

### AI Рекомендации

```
GET /api/cards/recommendations/
```

**Требует авторизации:** ✅

**Описание:** Умные рекомендации через AI ассистент

---

<a id="застройщики"></a>

## 🏗️ Застройщики

### Список застройщиков

```
GET /api/developers/
```

**Ответ 200:**
```json
[
  {
    "id": 1,
    "name": "ПИК",
    "phone": "92-62-66",
    "logo": "/media/developers/logos/pik.png",
    "is_subscribed": false
  }
]
```

---

### Детали застройщика

```
GET /api/developers/{id}/
```

---

### Карточки застройщика

```
GET /api/developers/{developer_id}/cards/
```

---

### Подписаться на застройщика

```
POST /api/developers/{developer_id}/subscribe/
```

**Требует авторизации:** ✅

---

### Отписаться от застройщика

```
DELETE /api/developers/{developer_id}/subscribe/
```

**Требует авторизации:** ✅

---

### Мои подписки

```
GET /api/developers/me/subscriptions/
```

**Требует авторизации:** ✅

---

<a id="уведомления"></a>

## 🔔 Уведомления

### Список уведомлений

```
GET /api/notifications/
```

**Требует авторизации:** ✅

**Параметры:**
- `page` — Номер страницы
- `is_read` — true/false (фильтр по прочитанности)

**Ответ 200:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "title": "Новая квартира",
      "message": "ПИК выложил новый объект",
      "type": "subscription",
      "card": {
        "id": 5,
        "title": "ЖК Солнечный",
        "price": 5000000,
        "phone": "92-62-66"
      },
      "old_price": null,
      "image_url": "/media/cards/images/photo.jpg",
      "is_read": false,
      "created_at": "2026-02-05T12:00:00Z"
    }
  ]
}
```

---

### Отметить уведомление как прочитанное

```
POST /api/notifications/{id}/read/
```

**Требует авторизации:** ✅

---

### Настройки уведомлений

```
GET /api/notifications/settings/
POST /api/notifications/settings/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "push_enabled": true,
  "email_enabled": false,
  "new_cards": true,
  "price_changes": true,
  "subscription_updates": true,
  "promotions": false
}
```

---

<a id="ai-ассистент"></a>

## 🤖 AI Ассистент

### Чат с AI

```
POST /api/cards/ai/chat/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "message": "Найди мне двухкомнатную квартиру в Махачкале до 5 млн",
  "mode": "search",
  "user_preferences": {
    "city": 1,
    "rooms_min": 2,
    "rooms_max": 2,
    "price_max": 5000000
  }
}
```

**Параметр `mode`:**
- `search` — Поиск с результатами из БД
- `free` — Свободный чат без поиска

**Ответ 200:**
```json
{
  "id": 1,
  "message": "Найди мне двухкомнатную квартиру...",
  "response": "Вот лучшие варианты для вас...",
  "ai_response": "Вот лучшие варианты для вас...",
  "referenced_cards": [
    {
      "id": 5,
      "title": "ЖК Солнечный",
      "price": 5000000,
      "area": 80,
      "rooms": 2
    }
  ],
  "mode": "search",
  "created_at": "2026-02-05T12:00:00Z"
}
```

---

### История чата

```
GET /api/cards/ai/history/
```

**Требует авторизации:** ✅

---

### Оценить ответ AI

```
POST /api/cards/ai/chat/{pk}/rate/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "rating": 5,
  "comment": "Супер!"
}
```

---

### Запросить скидку

```
POST /api/cards/{id}/discount/
```

**Требует авторизации:** ✅

**Параметры:**
```json
{
  "suggested_price": 4500000,
  "message": "Готов заключить договор немедленно"
}
```

---

### Мои запросы на скидку

```
GET /api/cards/discounts/me/
```

**Требует авторизации:** ✅

**Ответ 200:**
```json
[
  {
    "id": 1,
    "card": {
      "id": 5,
      "title": "ЖК Солнечный",
      "price": 5000000
    },
    "original_price": 5000000,
    "suggested_price": 4500000,
    "status": "pending",
    "created_at": "2026-02-04T10:00:00Z"
  }
]
```

**Статусы:**
- `pending` — На рассмотрении
- `approved` — Одобрено
- `rejected` — Отклонено

---

<a id="справочники"></a>

## 📚 Справочники

### Справочник: Города

| ID | Название |
|----|----------|
| 1 | Махачкала |
| 2 | Каспийск |
| 3 | Дербент |
| 4 | Избербаш |

### Справочник: Тип комплекса

| Значение | Название |
|----------|----------|
| `residential` | Жилой комплекс |
| `apart` | Апарт-комплекс |

### Справочник: Тип дома

| Значение | Название |
|----------|----------|
| `brick` | Кирпичный |
| `panel` | Панельный |
| `monolith` | Монолитный |
| `brick_monolith` | Кирпично-монолитный |
| `solid_monolith` | Цельно-монолитный |

### Справочник: Категория

| Значение | Название |
|----------|----------|
| `flat` | Квартира |
| `new_building` | Новостройка |
| `secondary` | Вторичное |

### Справочник: Лифт

| Значение | Название |
|----------|----------|
| `none` | Нет |
| `passenger` | Пассажирский |
| `cargo` | Грузовой |
| `cargo_passenger` | Грузопассажирский |
| `passenger_and_cargo` | Пассажирский и грузовой |

### Справочник: Парковка

| Значение | Название |
|----------|----------|
| `none` | Нет |
| `underground` | Подземная |
| `ground` | Наземная |
| `two_level` | Двухуровневая |

### Справочник: Отделка

| Значение | Название |
|----------|----------|
| `none` | Без отделки |
| `with_finish` | С отделкой |

### Справочник: Тип лифта

| Значение | Название |
|----------|----------|
| `none` | Нет |
| `passenger` | Пассажирский |
| `cargo` | Грузовой |
| `cargo_passenger` | Грузопассажирский |
| `passenger_and_cargo` | Пассажирский и грузовой |

---

## 🔐 Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | ✅ OK — Успешно |
| 201 | ✅ Created — Создано |
| 204 | ✅ No Content — Успешно удалено |
| 400 | ❌ Bad Request — Ошибка в параметрах |
| 401 | ❌ Unauthorized — Требуется авторизация |
| 403 | ❌ Forbidden — Доступ запрещён |
| 404 | ❌ Not Found — Не найдено |
| 500 | ❌ Server Error — Ошибка сервера |

---

## 📞 Rate Limiting

API ограничивает количество запросов:
- **Без авторизации:** 100 запросов/час
- **С авторизацией:** 1000 запросов/час

Лимиты передаются в заголовках:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1675000000
```

---

## 🚀 Примеры запросов

### cURL

```bash
# Получить список карточек
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.dreamhouse05.com/api/cards/

# Фильтр по цене
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.dreamhouse05.com/api/cards/?city=1&price_min=1000000&price_max=5000000"

# Добавить в избранное
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.dreamhouse05.com/api/cards/5/favorite/

# Поиск через AI
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Найди двухкомнатную квартиру","mode":"search"}' \
  https://api.dreamhouse05.com/api/cards/ai/chat/
```

### JavaScript/Fetch

```javascript
// Получить карточки
const token = localStorage.getItem('accessToken');
const response = await fetch('https://api.dreamhouse05.com/api/cards/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const cards = await response.json();

// Добавить в избранное
await fetch('https://api.dreamhouse05.com/api/cards/5/favorite/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Python

```python
import requests

token = 'your_access_token'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Получить карточки
response = requests.get(
    'https://api.dreamhouse05.com/api/cards/',
    headers=headers,
    params={'city': 1, 'price_max': 5000000}
)
cards = response.json()

# Поиск через AI
response = requests.post(
    'https://api.dreamhouse05.com/api/cards/ai/chat/',
    headers=headers,
    json={
        'message': 'Найди мне квартиру в центре',
        'mode': 'search'
    }
)
ai_response = response.json()
```

---

*Документация актуальна на февраль 2026. Для вопросов обратитесь в поддержку.*

# 🔌 Dream House API - Полная документация

## 📚 Содержание
1. [Аутентификация](#authentication)
2. [Скидки](#discounts)
3. [Рекомендации](#recommendations)
4. [AI Чат](#ai-chat)

---

## <a name="authentication"></a>🔐 Аутентификация

Все endpoints требуют Bearer токена в заголовке:

```bash
Authorization: Bearer <your_token>
```

Получить токен:
```bash
curl -X POST http://localhost:8000/api/token/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+79999999999",
    "password": "your_password"
  }'
```

---

## <a name="discounts"></a>💰 API Скидок

### Создать запрос на скидку
**POST** `/api/cards/<card_id>/discount/`

**Параметры:**
- `card_id` (int) - ID карточки
- `requested_price` (int) - желаемая цена
- `message` (string, опционально) - сообщение

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/cards/5/discount/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_price": 2800000,
    "message": "Готов торговаться"
  }'
```

**Пример ответа (201 Created):**
```json
{
  "id": 42,
  "card": 5,
  "card_title": "Квартира в центре",
  "user": 123,
  "user_phone": "+79999999999",
  "original_price": 3000000,
  "requested_price": 2800000,
  "discount_percent": 6.67,
  "status": "pending",
  "message": "Готов торговаться",
  "admin_comment": null,
  "created_at": "2025-12-11T16:35:00Z"
}
```

**Статус коды:**
- `201` - Запрос успешно создан
- `400` - Некорректные данные
- `401` - Не авторизован
- `404` - Карточка не найдена

---

### Получить свои запросы на скидки
**GET** `/api/cards/discounts/me/`

**Параметры запроса (опционально):**
- `status` - фильтр по статусу (pending, approved, rejected)
- `page` - номер страницы (по умолчанию 1)
- `limit` - количество на странице (по умолчанию 10)

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/cards/discounts/me/?status=pending" \
  -H "Authorization: Bearer TOKEN"
```

**Пример ответа:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "card": 5,
      "card_title": "Квартира в центре",
      "original_price": 3000000,
      "requested_price": 2800000,
      "discount_percent": 6.67,
      "status": "pending",
      "message": "Готов торговаться",
      "admin_comment": null,
      "created_at": "2025-12-11T16:35:00Z"
    },
    {
      "id": 41,
      "card": 3,
      "card_title": "Дом в пригороде",
      "original_price": 5000000,
      "requested_price": 4500000,
      "discount_percent": 10.0,
      "status": "approved",
      "message": "Нужна скидка для срочной покупки",
      "admin_comment": "Согласны на 10% скидку. Свяжитесь с риелтором.",
      "created_at": "2025-12-10T12:00:00Z"
    }
  ]
}
```

**Статус коды:**
- `200` - Успешно
- `401` - Не авторизован

---

## <a name="recommendations"></a>🎯 API Рекомендаций

### Получить рекомендации
**GET** `/api/cards/recommendations/`

При первом запросе система автоматически анализирует ваши избранные карточки и создает рекомендации.

**Параметры запроса (опционально):**
- `page` - номер страницы (по умолчанию 1)
- `limit` - количество на странице (по умолчанию 10)

**Пример запроса:**
```bash
curl -X GET http://localhost:8000/api/cards/recommendations/ \
  -H "Authorization: Bearer TOKEN"
```

**Пример ответа:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "card": {
        "id": 12,
        "title": "Элегантная квартира",
        "description": "3-комнатная квартира в новом доме...",
        "price": 2900000,
        "city": "Махачкала",
        "address": "ул. Ленина, 25",
        "house_type": "apartment",
        "rooms": 3,
        "area": 85.5,
        "rating": 4.8,
        "image": "http://example.com/image.jpg"
      },
      "score": 0.95,
      "reason": "Похожа по типу и городу на ваши избранные",
      "created_at": "2025-12-11T16:30:00Z"
    },
    {
      "id": 2,
      "card": {
        "id": 15,
        "title": "Просторный дом",
        "description": "Частный дом с участком...",
        "price": 4500000,
        "city": "Махачкала",
        "address": "пос. Новый, 10",
        "house_type": "house",
        "rooms": 4,
        "area": 120,
        "rating": 4.6,
        "image": "http://example.com/image2.jpg"
      },
      "score": 0.90,
      "reason": "Высокий рейтинг, близкий ценовой диапазон",
      "created_at": "2025-12-11T16:30:00Z"
    }
  ]
}
```

**Структура Card объекта:**
```json
{
  "id": 12,
  "title": "Название",
  "description": "Описание",
  "price": 2900000,
  "city": "Махачкала",
  "address": "Адрес",
  "house_type": "apartment|house|townhouse",
  "rooms": 3,
  "area": 85.5,
  "rating": 4.8,
  "image": "URL изображения"
}
```

**Статус коды:**
- `200` - Успешно
- `401` - Не авторизован

---

## <a name="ai-chat"></a>🤖 API AI Чата

### Отправить сообщение AI
**POST** `/api/cards/ai/chat/`

**Тело запроса:**
```json
{
  "message": "Строка сообщения (макс 2000 символов)",
  "user_preferences": {
    "city": 1,
    "price_min": 1000000,
    "price_max": 5000000,
    "rooms": 3,
    "house_type": "apartment",
    "area_min": 50,
    "area_max": 150
  }
}
```

**Параметры:**
- `message` (string, обязательно) - вопрос или запрос
- `user_preferences` (object, опционально) - предпочтения для поиска:
  - `city` (int) - ID города
  - `price_min` (int) - минимальная цена
  - `price_max` (int) - максимальная цена
  - `rooms` (int) - количество комнат
  - `house_type` (string) - тип дома (apartment, house, townhouse)
  - `area_min` (int) - минимальная площадь
  - `area_max` (int) - максимальная площадь

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Найди мне лучшую трёхкомнатную квартиру в Махачкале",
    "user_preferences": {
      "city": 1,
      "rooms": 3,
      "price_max": 3500000
    }
  }'
```

**Пример ответа (201 Created):**
```json
{
  "id": 42,
  "message": "Найди мне лучшую трёхкомнатную квартиру в Махачкале",
  "response": "Я нашел для вас отличный вариант! Это трёхкомнатная квартира в центре Махачкалы по цене 2,9 миллиона. Квартира имеет площадь 85 кв.м, высокий рейтинг 4.8 и находится в новом доме с современными удобствами.",
  "referenced_cards": [12, 15, 18],
  "tokens_used": 245,
  "is_helpful": null,
  "created_at": "2025-12-11T16:40:00Z"
}
```

**Параметры ответа:**
- `id` - ID сообщения (используется для оценки)
- `message` - ваше исходное сообщение
- `response` - ответ от AI
- `referenced_cards` - список ID карточек, упомянутых в ответе
- `tokens_used` - количество использованных токенов (для статистики)
- `is_helpful` - ваша оценка (null до оценки)
- `created_at` - время создания

**Статус коды:**
- `201` - Сообщение успешно обработано
- `400` - Некорректные данные или сообщение слишком длинное
- `401` - Не авторизован
- `503` - AI сервис недоступен (проверьте API ключ)

---

### Получить историю чатов
**GET** `/api/cards/ai/history/`

Получить все ваши сообщения с AI, упорядоченные по времени (новые сверху).

**Параметры запроса (опционально):**
- `page` - номер страницы (по умолчанию 1)
- `limit` - количество на странице (по умолчанию 20)
- `is_helpful` - фильтр (true, false, null)

**Пример запроса:**
```bash
curl -X GET "http://localhost:8000/api/cards/ai/history/?page=1&limit=10" \
  -H "Authorization: Bearer TOKEN"
```

**Пример ответа:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 42,
      "message": "Найди мне лучшую трёхкомнатную квартиру",
      "response": "Я нашел для вас отличный вариант...",
      "referenced_cards": [12, 15, 18],
      "tokens_used": 245,
      "is_helpful": true,
      "created_at": "2025-12-11T16:40:00Z"
    },
    {
      "id": 41,
      "message": "Какие самые рейтинговые дома в Махачкале?",
      "response": "Вот топ дома по рейтингу...",
      "referenced_cards": [5, 8, 10],
      "tokens_used": 180,
      "is_helpful": null,
      "created_at": "2025-12-11T16:35:00Z"
    }
  ]
}
```

**Статус коды:**
- `200` - Успешно
- `401` - Не авторизован

---

### Оценить ответ AI
**PATCH** `/api/cards/ai/chat/<message_id>/rate/`

Оцените полезность ответа для обучения системы.

**Параметры:**
- `message_id` (int) - ID сообщения
- `is_helpful` (boolean) - true если ответ был полезен, false если нет

**Пример запроса:**
```bash
curl -X PATCH http://localhost:8000/api/cards/ai/chat/42/rate/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_helpful": true
  }'
```

**Пример ответа:**
```json
{
  "id": 42,
  "message": "Найди мне лучшую трёхкомнатную квартиру",
  "response": "Я нашел для вас отличный вариант...",
  "referenced_cards": [12, 15, 18],
  "tokens_used": 245,
  "is_helpful": true,
  "created_at": "2025-12-11T16:40:00Z"
}
```

**Статус коды:**
- `200` - Успешно обновлено
- `400` - Некорректные данные
- `401` - Не авторизован
- `404` - Сообщение не найдено

---

## 📋 Коды ошибок

| Код | Описание | Решение |
|-----|---------|---------|
| 400 | Bad Request | Проверьте формат JSON и необходимые поля |
| 401 | Unauthorized | Используйте корректный Bearer токен |
| 404 | Not Found | Объект не существует в БД |
| 500 | Server Error | Свяжитесь с администратором |
| 503 | Service Unavailable | AI сервис недоступен, проверьте API ключ |

---

## 🔧 Примеры на разных языках

### Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

# Отправить сообщение AI
response = requests.post(
    "http://localhost:8000/api/cards/ai/chat/",
    headers=headers,
    json={
        "message": "Найди квартиру в Махачкале",
        "user_preferences": {
            "city": 1,
            "rooms": 3,
            "price_max": 3500000
        }
    }
)

print(response.json())

# Получить историю
history = requests.get(
    "http://localhost:8000/api/cards/ai/history/",
    headers=headers
)

print(history.json())

# Оценить ответ
rating = requests.patch(
    "http://localhost:8000/api/cards/ai/chat/42/rate/",
    headers=headers,
    json={"is_helpful": True}
)

print(rating.json())
```

### JavaScript
```javascript
const token = "YOUR_TOKEN";
const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};

// Отправить сообщение
fetch("http://localhost:8000/api/cards/ai/chat/", {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    message: "Найди квартиру в Махачкале",
    user_preferences: {
      city: 1,
      rooms: 3,
      price_max: 3500000
    }
  })
})
.then(r => r.json())
.then(data => console.log(data));

// Получить историю
fetch("http://localhost:8000/api/cards/ai/history/", {
  headers: headers
})
.then(r => r.json())
.then(data => console.log(data));

// Оценить ответ
fetch("http://localhost:8000/api/cards/ai/chat/42/rate/", {
  method: "PATCH",
  headers: headers,
  body: JSON.stringify({ is_helpful: true })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 🚨 Тестирование

### Checklist перед production:
- [ ] API ключ установлен и работает
- [ ] Все endpoints возвращают 200+ статусы
- [ ] Лимиты на запросы установлены
- [ ] Ошибки обрабатываются корректно
- [ ] Чат история сохраняется
- [ ] Рекомендации генерируются корректно
- [ ] Скидки обрабатываются корректно

### Быстрый тест:
```bash
# 1. Получить токен
TOKEN=$(curl -X POST http://localhost:8000/api/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79999999999", "password": "pass"}' \
  | jq -r '.access')

# 2. Протестировать AI чат
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!"}'

# 3. Получить рекомендации
curl -X GET http://localhost:8000/api/cards/recommendations/ \
  -H "Authorization: Bearer $TOKEN"
```

---

**Последнее обновление:** 11 декабря 2025

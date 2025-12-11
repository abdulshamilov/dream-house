# 🔌 Dream House API - Полная документация

> 📚 **Интерактивная документация доступна**: https://api.dreamhouse05.com/api/docs/
> 
> Все endpoints, параметры и примеры можно протестировать прямо там!

## 📚 Содержание
1. [Аутентификация](#authentication)
2. [Карточки и фильтры](#cards)
3. [Скидки](#discounts)
4. [Рекомендации](#recommendations)
5. [AI Чат](#ai-chat)

---

## <a name="authentication"></a>🔐 Аутентификация

Все endpoints требуют Bearer токена в заголовке:

```bash
Authorization: Bearer <your_token>
```

Получить токен:
```bash
curl -X POST https://api.dreamhouse05.com/api/token/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+79999999999",
    "password": "your_password"
  }'
```

---

## <a name="cards"></a>🏠 API Карточек и фильтры

### Получить список карточек (GET)
**GET** `/api/cards/`

Получить список всех карточек с поддержкой фильтрации через query параметры.

**Доступные параметры фильтрации:**

| Параметр | Тип | Описание | Пример |
|----------|-----|---------|--------|
| `search` | string | Поиск по названию, описанию, адресу | `?search=квартира` |
| `city` | int | Город (1=Махачкала, 2=Каспийск, 3=Дербент) | `?city=1` |
| `house_type` | string | Тип дома (apartment, house) | `?house_type=apartment` |
| `building_material` | string | Материал (brick, panel, monolith) | `?building_material=brick` |
| `category` | string | Категория (flat, new_building) | `?category=flat` |
| `elevator` | string | Лифт (none, passenger, cargo) | `?elevator=passenger` |
| `parking` | string | Парковка (none, underground) | `?parking=underground` |
| `balcony` | bool | Наличие балкона (true/false) | `?balcony=true` |
| `price_min` | int | Минимальная цена | `?price_min=1000000` |
| `price_max` | int | Максимальная цена | `?price_max=5000000` |
| `rooms_min` | int | Минимум комнат | `?rooms_min=2` |
| `rooms_max` | int | Максимум комнат | `?rooms_max=4` |
| `area_min` | float | Минимальная площадь (м²) | `?area_min=50` |
| `area_max` | float | Максимальная площадь (м²) | `?area_max=150` |
| `floors_min` | int | Минимум этажей в доме | `?floors_min=5` |
| `floors_max` | int | Максимум этажей в доме | `?floors_max=20` |

**Пример запроса (несколько фильтров):**
```bash
curl -X GET "https://api.dreamhouse05.com/api/cards/?city=1&price_min=1000000&price_max=5000000&house_type=apartment&rooms_min=2" \
  -H "Content-Type: application/json"
```

**Пример ответа (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Квартира в центре",
    "address": "ул. Ленина, 25",
    "description": "3-комнатная квартира в новом доме...",
    "price": 2900000,
    "rooms": 3,
    "city": 1,
    "house_type": "apartment",
    "area": 85.5,
    "building_material": "brick",
    "category": "flat",
    "floors_total": 12,
    "elevator": "passenger",
    "parking": "underground",
    "balcony": true,
    "ceiling_height": 2.8,
    "latitude": 42.9813,
    "longitude": 47.5025,
    "rating": 4.8,
    "rating_count": 15,
    "owner": "Иван Петров",
    "developer": {
      "id": 5,
      "name": "СК Развитие",
      "logo": "http://example.com/logo.png"
    },
    "images": [
      {"id": 1, "image": "http://example.com/img1.jpg"},
      {"id": 2, "image": "http://example.com/img2.jpg"}
    ],
    "videos": [
      {"id": 1, "video": "http://example.com/video1.mp4"}
    ],
    "documents": [
      {"id": 1, "title": "План", "file": "http://example.com/plan.pdf", "uploaded_at": "2025-12-10T10:00:00Z"}
    ],
    "reviews": ["Отличная квартира!", "Рекомендую!"],
    "questions": ["Можно ли торговаться?"],
    "created_at": "2025-12-01T14:30:00Z",
    "is_favorite": false
  },
  {
    "id": 2,
    "title": "Уютная квартира",
    "address": "пр. Пушкина, 10",
    "description": "2-комнатная квартира...",
    "price": 1800000,
    "rooms": 2,
    "city": 1,
    "house_type": "apartment",
    "area": 65.0,
    "building_material": "panel",
    "category": "flat",
    "floors_total": 9,
    "elevator": "passenger",
    "parking": "none",
    "balcony": false,
    "ceiling_height": 2.5,
    "latitude": 42.9820,
    "longitude": 47.5030,
    "rating": 4.5,
    "rating_count": 8,
    "owner": "Мария Сидорова",
    "developer": null,
    "images": [],
    "videos": [],
    "documents": [],
    "reviews": [],
    "questions": [],
    "created_at": "2025-12-05T16:00:00Z",
    "is_favorite": true
  }
]
```

**Статус коды:**
- `200` - Успешно
- `400` - Некорректные параметры фильтра

---

### Получить список карточек с фильтрами (POST)
**POST** `/api/cards/filter/`

Альтернативный способ фильтрации - передача параметров в теле JSON. Удобен когда много фильтров или нужна сложная логика.

**Тело запроса (все параметры опциональны):**
```json
{
  "search": "квартира в центре",
  "city": 1,
  "house_type": "apartment",
  "building_material": "brick",
  "category": "flat",
  "elevator": "passenger",
  "parking": "underground",
  "balcony": true,
  "price_min": 1000000,
  "price_max": 5000000,
  "rooms_min": 2,
  "rooms_max": 4,
  "area_min": 50,
  "area_max": 150,
  "floors_min": 5,
  "floors_max": 20
}
```

**Пример запроса:**
```bash
curl -X POST https://api.dreamhouse05.com/api/cards/filter/ \
  -H "Content-Type: application/json" \
  -d '{
    "city": 1,
    "price_min": 1000000,
    "price_max": 5000000,
    "house_type": "apartment",
    "rooms_min": 2,
    "elevator": "passenger"
  }'
```

**Пример ответа (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Квартира в центре",
    "address": "ул. Ленина, 25",
    "description": "3-комнатная квартира в новом доме...",
    "price": 2900000,
    "rooms": 3,
    "city": 1,
    "house_type": "apartment",
    "area": 85.5,
    "building_material": "brick",
    "category": "flat",
    "floors_total": 12,
    "elevator": "passenger",
    "parking": "underground",
    "balcony": true,
    "ceiling_height": 2.8,
    "latitude": 42.9813,
    "longitude": 47.5025,
    "rating": 4.8,
    "rating_count": 15,
    "owner": "Иван Петров",
    "developer": {
      "id": 5,
      "name": "СК Развитие",
      "logo": "http://example.com/logo.png"
    },
    "images": [
      {"id": 1, "image": "http://example.com/img1.jpg"}
    ],
    "videos": [],
    "documents": [],
    "reviews": ["Отличная квартира!"],
    "questions": [],
    "created_at": "2025-12-01T14:30:00Z",
    "is_favorite": false
  }
]
```

**Статус коды:**
- `200` - Успешно
- `400` - Некорректные данные в теле запроса

---

**Рекомендация:**
- **GET /api/cards/** - для простых фильтров (1-3 параметра), поддерживает кэширование
- **POST /api/cards/filter/** - для сложных фильтров (много параметров), удобнее работать с JSON

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
curl -X POST https://api.dreamhouse05.com/api/cards/5/discount/ \
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
curl -X GET "https://api.dreamhouse05.com/api/cards/discounts/me/?status=pending" \
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
curl -X GET https://api.dreamhouse05.com/api/cards/recommendations/ \
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

AI Ассистент поддерживает два режима работы:
- **`search`** (по умолчанию) - AI ищет квартиры в БД и рекомендует их
- **`free`** - обычный чат без поиска в БД

### Отправить сообщение AI (режим поиска)
**POST** `/api/cards/ai/chat/`

**Тело запроса:**
```json
{
  "message": "Найди мне квартиру в Махачкале",
  "mode": "search",
  "user_preferences": {
    "city": 1,
    "price_min": 1000000,
    "price_max": 5000000,
    "rooms": 3,
    "house_type": "apartment"
  }
}
```

**Параметры:**
- `message` (string, обязательно) - вопрос или запрос
- `mode` (string, опционально) - `'search'` или `'free'` (по умолчанию `'search'`)
- `user_preferences` (object, опционально) - предпочтения для поиска (только для режима `'search'`):
  - `city` (int) - ID города
  - `price_min` (int) - минимальная цена
  - `price_max` (int) - максимальная цена
  - `rooms` (int) - количество комнат
  - `house_type` (string) - тип дома (apartment, house, townhouse)
  - `area_min` (int) - минимальная площадь
  - `area_max` (int) - максимальная площадь

**Пример запроса (поиск квартир):**
```bash
curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Найди мне 3-комнатную квартиру в Махачкале",
    "mode": "search",
    "user_preferences": {
      "city": 1,
      "rooms": 3,
      "price_max": 3500000
    }
  }'
```

**Пример запроса (обычный чат):**
```bash
curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Как лучше выбирать недвижимость?",
    "mode": "free"
  }'
```
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
curl -X GET "https://api.dreamhouse05.com/api/cards/ai/history/?page=1&limit=10" \
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
curl -X PATCH https://api.dreamhouse05.com/api/cards/ai/chat/42/rate/ \
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

# Отправить сообщение AI (режим поиска)
response = requests.post(
    "https://api.dreamhouse05.com/api/cards/ai/chat/",
    headers=headers,
    json={
        "message": "Найди квартиру в Махачкале",
        "mode": "search",
        "user_preferences": {
            "city": 1,
            "rooms": 3,
            "price_max": 3500000
        }
    }
)

print(response.json())

# Отправить сообщение AI (обычный чат)
response = requests.post(
    "https://api.dreamhouse05.com/api/cards/ai/chat/",
    headers=headers,
    json={
        "message": "Как лучше выбирать недвижимость?",
        "mode": "free"
    }
)

print(response.json())

# Получить историю
history = requests.get(
    "https://api.dreamhouse05.com/api/cards/ai/history/",
    headers=headers
)

print(history.json())

# Оценить ответ
rating = requests.patch(
    "https://api.dreamhouse05.com/api/cards/ai/chat/42/rate/",
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

// Отправить сообщение (режим поиска)
fetch("https://api.dreamhouse05.com/api/cards/ai/chat/", {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    message: "Найди квартиру в Махачкале",
    mode: "search",
    user_preferences: {
      city: 1,
      rooms: 3,
      price_max: 3500000
    }
  })
})
.then(r => r.json())
.then(data => console.log(data));

// Отправить сообщение (обычный чат)
fetch("https://api.dreamhouse05.com/api/cards/ai/chat/", {
  method: "POST",
  headers: headers,
  body: JSON.stringify({
    message: "Как лучше выбирать недвижимость?",
    mode: "free"
  })
})
.then(r => r.json())
.then(data => console.log(data));

// Получить историю
fetch("https://api.dreamhouse05.com/api/cards/ai/history/", {
  headers: headers
})
.then(r => r.json())
.then(data => console.log(data));

// Оценить ответ
fetch("https://api.dreamhouse05.com/api/cards/ai/chat/42/rate/", {
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
TOKEN=$(curl -X POST https://api.dreamhouse05.com/api/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79999999999", "password": "pass"}' \
  | jq -r '.access')

# 2. Протестировать AI чат (search mode - с поиском недвижимости)
curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Покажи мне квартиры в Москве",
    "mode": "search",
    "user_preferences": {"city": "Moscow", "house_type": "apartment"}
  }'

# 3. Протестировать AI чат (free mode - обычный чат)
curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!", "mode": "free"}'

# 4. Получить рекомендации
curl -X GET https://api.dreamhouse05.com/api/cards/recommendations/ \
  -H "Authorization: Bearer $TOKEN"
```

---

**Последнее обновление:** 11 декабря 2025

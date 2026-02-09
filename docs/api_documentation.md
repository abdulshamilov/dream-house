# Dream House API Documentation

## Содержание
- [Аутентификация (SMS)](#аутентификация-sms)
- [Регистрация](#регистрация)
- [Профиль пользователя](#профиль-пользователя)
- [Реферальная система](#реферальная-система)
- [Сброс пароля](#сброс-пароля)
- [Удаление аккаунта](#удаление-аккаунта)
- [Карточки недвижимости](#карточки-недвижимости)
- [Фильтры](#фильтры)
- [Застройщики](#застройщики)
- [Заявки на звонок](#заявки-на-звонок)
- [AI Ассистент](#ai-ассистент)
- [Примеры запросов](#примеры-запросов)

---

## Аутентификация (SMS)

Вход в систему осуществляется через SMS-код (без пароля).

### Запрос SMS-кода

```
POST /api/users/sms/request/
```

**Request:**
```json
{
  "phone_number": "+79991234567"
}
```

**Response (200):**
```json
{
  "detail": "OTP sent to your phone",
  "phone_number": "+79991234567",
  "otp": "123456"  // только в debug режиме
}
```

### Проверка SMS-кода и вход

```
POST /api/users/sms/verify/
```

**Request:**
```json
{
  "phone_number": "+79991234567",
  "otp": "123456"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Регистрация

Двухэтапная регистрация с подтверждением по SMS.

### Шаг 1: Запрос регистрации

```
POST /api/users/register/
```

**Request:**
```json
{
  "phone_number": "+79991234567",
  "name": "Иван Иванов",
  "ref_code": "550e8400-e29b-41d4-a716-446655440000"  // опционально
}
```

**Response (200):**
```json
{
  "detail": "OTP sent to your phone",
  "phone_number": "+79991234567",
  "otp": "123456"  // только в debug режиме
}
```

### Шаг 2: Подтверждение регистрации

```
POST /api/users/register/confirm/
```

**Request:**
```json
{
  "phone_number": "+79991234567",
  "otp": "123456"
}
```

**Response (201):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Профиль пользователя

### Получить информацию о текущем пользователе

```
GET /api/users/me/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 1,
  "phone_number": "+79991234567",
  "name": "Иван Иванов",
  "profile_photo": "https://api.dreamhouse05.com/media/users/photo.jpg"
}
```

### Обновить профиль (имя и/или фото)

```
PUT /api/users/update-profile/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request (form-data):**
| Поле | Тип | Описание |
|------|-----|----------|
| `name` | string | Новое имя (опционально) |
| `profile_photo` | file | Фото профиля (JPEG, PNG, GIF, HEIC). Макс 5MB |

**Response (200):** UserSerializer

### Удалить фото профиля

```
DELETE /api/users/update-profile/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "detail": "Photo deleted successfully"
}
```

---

## Реферальная система

### Получить реферальную ссылку

```
GET /api/users/referral-link/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "referral_link": "https://dreamhouse05.com/register/?ref=550e8400-e29b-41d4-a716-446655440000"
}
```

### Список приглашённых пользователей

```
GET /api/users/referrals/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
[
  {
    "id": 1,
    "referred_name": "Пётр Петров",
    "referred_phone": "+79997654321",
    "reward_amount": "1000.00",
    "created_at": "2026-02-01T12:00:00Z"
  }
]
```

---

## Сброс пароля

### Запрос сброса пароля

```
POST /api/users/password-reset/request/
```

**Request:**
```json
{
  "phone_number": "+79991234567"
}
```

**Response (200):**
```json
{
  "detail": "OTP sent to your phone"
}
```

### Подтверждение сброса пароля

```
POST /api/users/password-reset/confirm/
```

**Request:**
```json
{
  "phone_number": "+79991234567",
  "otp": "123456",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Удаление аккаунта

### Шаг 1: Запрос SMS-кода для удаления

```
POST /api/users/delete-account/request-otp/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "detail": "OTP sent to your phone"
}
```

### Шаг 2: Подтверждение удаления

```
DELETE /api/users/delete-account/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "otp": "123456"
}
```

**Response (204):** No content

---

## Карточки недвижимости

### Базовый URL
```
GET /api/cards/
GET /api/cards/{id}/
```

### Поля карточки

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор |
| `title` | string | Название объекта |
| `address` | string | Адрес |
| `description` | string | Описание |
| `price` | decimal | Цена (₽) |
| `price_metr` | decimal | Цена за м² (вычисляемое) |
| `phone` | string | Телефон застройщика |
| `rooms` | integer | Количество комнат |
| `area` | decimal | Площадь (м²) |
| `city` | integer | Город (см. справочник) |
| `complex_type` | string | Тип комплекса |
| `house_type` | string | Тип дома |
| `category` | string | Категория |
| `floors_total` | integer | Этажность |
| `elevator` | string | Тип лифта |
| `parking` | string | Парковка |
| `balcony` | boolean | Наличие балкона |
| `loggia` | boolean | Наличие лоджии |
| `finishing` | string | Отделка |
| `ceiling_height` | decimal | Высота потолков (м) |
| `latitude` | float | Широта |
| `longitude` | float | Долгота |
| `rating` | decimal | Рейтинг (0-5) |
| `rating_count` | integer | Количество оценок |
| `developer` | object | Застройщик |
| `images` | array | Фотографии |
| `floor_plans` | array | Планировки |
| `videos` | array | Видео |
| `documents` | array | Документы |
| `is_favorite` | boolean | В избранном |
| `created_at` | datetime | Дата создания |

### Справочники

#### Города (city)
| Значение | Название |
|----------|----------|
| `1` | Махачкала |
| `2` | Каспийск |
| `3` | Дербент |
| `4` | Избербаш |

#### Тип комплекса (complex_type)
| Значение | Название |
|----------|----------|
| `residential` | Жилой комплекс |
| `apart` | Апарт-комплекс |

#### Тип дома (house_type)
| Значение | Название |
|----------|----------|
| `brick` | Кирпичный |
| `panel` | Панельный |
| `monolith` | Монолитный |
| `brick_monolith` | Кирпично-монолитный |
| `solid_monolith` | Цельно-монолитный |

#### Категория (category)
| Значение | Название |
|----------|----------|
| `flat` | Квартира |
| `new_building` | Новостройка |
| `secondary` | Вторичное |

#### Лифт (elevator)
| Значение | Название |
|----------|----------|
| `none` | Нет |
| `passenger` | Пассажирский |
| `cargo` | Грузовой |
| `cargo_passenger` | Грузопассажирский |
| `passenger_and_cargo` | Пассажирский и грузовой |

#### Парковка (parking)
| Значение | Название |
|----------|----------|
| `none` | Нет |
| `underground` | Подземная |
| `ground` | Наземная |
| `two_level` | Двухуровневая |

#### Отделка (finishing)
| Значение | Название |
|----------|----------|
| `none` | Без отделки |
| `with_finish` | С отделкой |

---

## Фильтры

### Базовый URL
```
GET /api/cards/?{параметры}
```

### Текстовый поиск

| Параметр | Тип | Описание |
|----------|-----|----------|
| `search` | string | Поиск по названию, описанию, адресу |

### Фильтры по выбору

| Параметр | Тип | Описание |
|----------|-----|----------|
| `complex_type` | string | Тип комплекса (residential, apart) |
| `house_type` | string | Тип дома (brick, panel, monolith, brick_monolith, solid_monolith) |
| `city` | integer | Город (1, 2, 3, 4) |
| `developer` | integer | ID застройщика |
| `category` | string | Категория (flat, new_building, secondary) |
| `finishing` | string | Отделка (none, with_finish) |
| `elevator` | string | Лифт (можно несколько через &) |
| `parking` | string | Парковка (none, underground, ground, two_level) |

### Булевые фильтры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `balcony` | boolean | Наличие балкона (true/false) |
| `loggia` | boolean | Наличие лоджии (true/false) |

### Числовые диапазоны

| Параметр | Тип | Описание |
|----------|-----|----------|
| `price_min` | number | Минимальная цена (₽) |
| `price_max` | number | Максимальная цена (₽) |
| `rooms_min` | integer | Минимум комнат |
| `rooms_max` | integer | Максимум комнат |
| `area_min` | number | Минимальная площадь (м²) |
| `area_max` | number | Максимальная площадь (м²) |
| `floors_min` | integer | Минимум этажей |
| `floors_max` | integer | Максимум этажей |
| `price_per_sqm_min` | number | Мин. цена за м² |
| `price_per_sqm_max` | number | Макс. цена за м² |
| `ceiling_height_min` | number | Мин. высота потолков (м) |
| `ceiling_height_max` | number | Макс. высота потолков (м) |

---

## Застройщики

### Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/developers/` | Список застройщиков |
| GET | `/api/developers/{id}/` | Детали застройщика |
| POST | `/api/developers/{id}/subscribe/` | Подписаться |
| DELETE | `/api/developers/{id}/unsubscribe/` | Отписаться |
| GET | `/api/developers/subscriptions/` | Мои подписки |

### Поля застройщика

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный ID |
| `name` | string | Название компании |
| `phone` | string | Телефон (по умолчанию: 92-62-66) |
| `logo` | string | URL логотипа |
| `cards` | array | Карточки застройщика |
| `is_subscribed` | boolean | Подписан ли текущий пользователь |

### Пример ответа

```json
{
  "id": 1,
  "name": "Dream Development",
  "phone": "92-62-66",
  "logo": "/media/developers/logos/dream.png",
  "is_subscribed": true,
  "cards": [...]
}
```

---

## Заявки на звонок

### Создать заявку на звонок

```
POST /api/cards/{id}/call-request/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "phone_number": "+79991234567",
  "name": "Иван Иванов",
  "preferred_time": "Вечером после 18:00"
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `phone_number` | string | Да | Номер телефона для связи |
| `name` | string | Да | Имя клиента |
| `preferred_time` | string | Нет | Предпочтительное время звонка |

**Response (201):**
```json
{
  "id": 1,
  "phone_number": "+79991234567",
  "name": "Иван Иванов",
  "preferred_time": "Вечером после 18:00",
  "card": 5
}
```

---

## AI Ассистент

### Чат с AI

```
POST /api/cards/ai/chat/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "message": "Покажи квартиры в Махачкале до 5 млн",
  "mode": "search",
  "user_preferences": {
    "city": 1,
    "price_max": 5000000
  }
}
```

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `message` | string | Да | Сообщение пользователя |
| `mode` | string | Нет | `search` (по умолчанию) или `free` |
| `user_preferences` | object | Нет | Фильтры поиска (city, price_min, price_max, rooms) |

**Response (201):**
```json
{
  "id": 1,
  "user": 1,
  "message": "Покажи квартиры в Махачкале до 5 млн",
  "response": "Вот 3 лучших варианта...",
  "ai_response": "Вот 3 лучших варианта...",
  "ai_response_json": {"cards": [5, 12, 8]},
  "mode": "search",
  "referenced_cards": [
    {"id": 5, "title": "2-комн. в ЖК Мечта", ...},
    {"id": 12, "title": "1-комн. в центре", ...},
    {"id": 8, "title": "Студия у моря", ...}
  ],
  "created_at": "2026-02-09T12:00:00Z"
}
```

### Получить рекомендации

```
GET /api/cards/ai/recommendations/
Authorization: Bearer {access_token}
```

Возвращает персонализированные рекомендации на основе истории просмотров.

**Response (200):** Массив карточек (CardSerializer)

---

## Примеры запросов

### Поиск квартир в Махачкале до 5 млн

```
GET /api/cards/?city=1&price_max=5000000
```

### Двухкомнатные квартиры с лифтом

```
GET /api/cards/?rooms_min=2&rooms_max=2&elevator=passenger&elevator=cargo_passenger
```

### Новостройки с отделкой

```
GET /api/cards/?category=new_building&finishing=with_finish
```

### Поиск по тексту

```
GET /api/cards/?search=центр
```

### Квартиры конкретного застройщика

```
GET /api/cards/?developer=5
```

### Фильтр по цене за метр

```
GET /api/cards/?price_per_sqm_min=50000&price_per_sqm_max=100000
```

### Комбинированный запрос

```
GET /api/cards/?city=1&rooms_min=1&rooms_max=3&price_max=10000000&house_type=monolith&balcony=true
```

---

## Пагинация

Все списки поддерживают пагинацию:

| Параметр | Описание |
|----------|----------|
| `page` | Номер страницы (с 1) |
| `page_size` | Размер страницы (по умолчанию 10) |

### Пример ответа

```json
{
  "count": 150,
  "next": "http://api.example.com/cards/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Авторизация

Все защищённые эндпоинты требуют JWT токен:

```
Authorization: Bearer {access_token}
```

### Получение токена (через SMS)

1. Запросить код: `POST /api/users/sms/request/`
2. Подтвердить код: `POST /api/users/sms/verify/`

### Обновление токена

```
POST /api/users/token/refresh/
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Важные замечания

### Фильтр комнат
Используйте `rooms_min` и `rooms_max` (числа), **НЕ** массив `rooms: [1,2,3]`.

```
GET /api/cards/?rooms_min=2&rooms_max=3
```

### Текстовый поиск
Параметр называется `search` (не `q` и не `query`).

```
GET /api/cards/?search=центр
```

### Поля города
Поле `region` **отсутствует**. Используйте только `city` (1-4).

---

*Документация актуальна на февраль 2026*

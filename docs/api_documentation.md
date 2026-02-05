# Dream House API Documentation

## Содержание
- [Карточки недвижимости](#карточки-недвижимости)
- [Фильтры](#фильтры)
- [Застройщики](#застройщики)
- [Примеры запросов](#примеры-запросов)

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

Большинство эндпоинтов требуют JWT токен:

```
Authorization: Bearer {access_token}
```

### Получение токена

```
POST /api/users/token/
{
  "phone_number": "+79991234567",
  "password": "your_password"
}
```

---

*Документация актуальна на февраль 2026*

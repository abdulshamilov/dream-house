# DreamHouse — Notifications API (v1.0)

## Эндпоинты
- **GET** `/api/notifications/` — список уведомлений (Bearer JWT обязателен).
- **PATCH** `/api/notifications/{id}/read/` — пометить уведомление прочитанным (только своё).

## Формат ответа списка
```json
{
  "count": 10,
  "next": "https://api.dreamhouse.ru/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Цена снижена на 15%!",
      "message": "2-комнатная квартира в ЖК Престиж теперь доступнее",
      "type": "price_drop",
      "is_read": false,
      "created_at": "2025-01-15T10:30:00Z",
      "card_id": "123",
      "image_url": "https://api.dreamhouse.ru/media/apartments/123/photo1.jpg",
      "price": 4500000,
      "old_price": 5300000
    }
  ]
}
```

## Поля уведомления
- `id` — integer
- `title` — string|null
- `message` — string|null
- `type` — string|null (`price_drop`, `sale`, `discount`, `subscription`, `new`, `system`)
- `is_read` — boolean
- `created_at` — ISO 8601
- `card_id` — string|null (ID карточки)
- `image_url` — string|null (первое фото карточки или null)
- `price` — integer|null (текущая цена карточки, округление ROUND_HALF_UP)
- `old_price` — integer|null (только если задана и строго больше `price`)

## Логика заполнения
- `card_id`: null, если нет связи с объектом.
- `image_url`: первое фото карточки; если фото нет или карточки нет — null.
- `price`: текущая цена карточки, иначе null.
- `old_price`: отдаётся только если > `price`; иначе null.

## Типы и бейджи
- `price_drop`, `sale`, `discount` → зелёный.
- `subscription` → синий.
- `new` → красный.
- `system` → нейтральный.

## UI-гайд
- **С фото (`image_url` есть)**: карточка 16:9, бейдж слева сверху, индикатор непрочитанности справа сверху, дата справа снизу на фото; под фото — заголовок, описание, цена/скидка.
- **Без фото**: компактная текстовая карточка; верхняя строка — бейдж + дата; ниже — заголовок и описание.
- **Цены**: если `price` есть — показываем; если `old_price` > `price` — показываем старую зачёркнутой и процент скидки `(old_price - price) / old_price`.

## Пагинация
- Параметр `page`; в ответе `count`, `next`, `previous`, `results`.
- По умолчанию `page_size = 10`.

## Маркировка прочитанным
- `PATCH /api/notifications/{id}/read/` без тела.
- Доступно только владельцу уведомления; чужие вернут 404.

## Быстрая проверка
1) Авторизоваться (Bearer JWT).
2) `GET /api/notifications/` — проверить поля `image_url`, `price`, `old_price` по логике выше.
3) `PATCH /api/notifications/{id}/read/` — убедиться, что `is_read` меняется и чужие уведомления недоступны.

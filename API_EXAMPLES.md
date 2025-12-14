# 🎯 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ НОВЫХ ФУНКЦИЙ

## 1️⃣ AI ЧАТ - РЕЖИМ ПОИСКА КВАРТИР

### Запрос
```bash
curl -X POST http://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Ищу красивую 2-комнатную квартиру в Махачкале не дороже 5 миллионов",
    "user_preferences": {
      "city": 1,
      "rooms": 2,
      "price_max": 5000000,
      "house_type": "apartment"
    },
    "mode": "search"
  }'
```

### Ответ
```json
{
  "success": true,
  "response": "Я нашел для вас 3 отличные 2-комнатные квартиры в Махачкале:\n\n1. Современная квартира на Проспекте Дагестана - 4,850,000₽\n   Площадь: 56 м², Рейтинг: 4.8/5\n\n2. Уютная квартира в центре - 4,200,000₽\n   Площадь: 52 м², Рейтинг: 4.5/5\n\n3. Семейная квартира с видом - 4,999,999₽\n   Площадь: 62 м², Рейтинг: 4.9/5",
  "tokens_used": 245,
  "referenced_cards": [1, 5, 12],
  "mode": "search"
}
```

---

## 2️⃣ AI ЧАТ - РЕЖИМ ОБЫЧНОГО КОНСУЛЬТИРОВАНИЯ

### Запрос
```bash
curl -X POST http://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "В чем разница между монолитным и панельным домом?",
    "mode": "free"
  }'
```

### Ответ
```json
{
  "success": true,
  "response": "Отличный вопрос! Вот основные различия:\n\n🏗️ МОНОЛИТНЫЕ ДОМА:\n✅ Лучше звукоизоляция\n✅ Больше гибкости в планировке квартир\n✅ Выше цена\n✅ Более современный метод строительства\n\n🏢 ПАНЕЛЬНЫЕ ДОМА:\n✅ Ниже цена\n✅ Быстрее строятся\n⚠️ Хуже звукоизоляция\n⚠️ Меньше вариантов планировки\n\nДля семьи с детьми рекомендую монолитные дома, так как они тише и комфортнее.",
  "tokens_used": 189,
  "referenced_cards": [],
  "mode": "free"
}
```

---

## 3️⃣ ПОДПИСКА НА ЗАСТРОЙЩИКА И ИНФОРМАЦИЯ О НЕЙ

### Запрос карточки с информацией о подписке
```bash
curl http://api.dreamhouse05.com/api/cards/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ответ (фрагмент с developer)
```json
{
  "id": 1,
  "title": "Квартира в ЖК Парк у дома",
  "price": 4850000,
  "developer": {
    "id": 6,
    "name": "ЖК \"Парк у дома\"",
    "logo": "https://api.dreamhouse05.com/media/developers/logos/i_3.webp",
    "is_subscribed": true  // 🔑 true или false
  },
  "list_curations": [5, 12, 18],  // ID похожих квартир
  "document_lists": [
    {
      "id": 1,
      "name": "Правоустанавливающие документы",
      "documents": [
        {"id": 1, "title": "Свидетельство", "file": "..."},
        {"id": 2, "title": "Договор", "file": "..."}
      ]
    }
  ]
}
```

---

## 4️⃣ ПОДБОРКИ ДОКУМЕНТОВ - СОЗДАНИЕ

### Создать подборку "Правоустанавливающие документы"
```bash
curl -X POST http://api.dreamhouse05.com/api/cards/1/document-lists/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "name": "Правоустанавливающие документы"
  }'
```

### Ответ
```json
{
  "id": 1,
  "name": "Правоустанавливающие документы",
  "documents": [],
  "created_at": "2025-12-14T10:30:00Z"
}
```

### Просмотр подборок для карточки
```bash
curl http://api.dreamhouse05.com/api/cards/1/document-lists/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ответ
```json
[
  {
    "id": 1,
    "name": "Правоустанавливающие документы",
    "documents": [
      {
        "id": 1,
        "title": "Свидетельство о государственной регистрации",
        "file": "https://...",
        "uploaded_at": "2025-12-10T15:20:00Z"
      },
      {
        "id": 2,
        "title": "Договор купли-продажи",
        "file": "https://...",
        "uploaded_at": "2025-12-10T15:21:00Z"
      }
    ],
    "created_at": "2025-12-10T15:00:00Z"
  },
  {
    "id": 2,
    "name": "Техническая документация",
    "documents": [...]
  }
]
```

---

## 5️⃣ ИСТОРИЯ ПРОСМОТРОВ - СОХРАНЕНИЕ

### Сохранить просмотр при открытии карточки (АВТОМАТИЧЕСКИ)
```bash
curl http://api.dreamhouse05.com/api/cards/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
→ Просмотр автоматически сохраняется!

### Явное сохранение с длительностью
```bash
curl -X POST http://api.dreamhouse05.com/api/cards/1/view-history/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "duration_seconds": 45
  }'
```

### Ответ
```json
{
  "message": "View saved",
  "id": 123
}
```

---

## 6️⃣ ИСТОРИЯ ПРОСМОТРОВ - ПОЛУЧЕНИЕ

### Получить историю просмотров текущего пользователя
```bash
curl http://api.dreamhouse05.com/api/cards/view-history/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ответ
```json
[
  {
    "id": 1,
    "card": {
      "id": 1,
      "title": "Квартира в ЖК Парк у дома",
      "price": 4850000,
      "rooms": 2,
      "area": 56,
      "city": 1,
      "rating": 4.8,
      "developer": {...}
    },
    "card_title": "Квартира в ЖК Парк у дома",
    "viewed_at": "2025-12-14T10:30:15Z",
    "duration_seconds": 45
  },
  {
    "id": 2,
    "card": {
      "id": 5,
      "title": "Уютная квартира в центре",
      "price": 4200000,
      "rooms": 2,
      "area": 52,
      "city": 1,
      "rating": 4.5,
      "developer": {...}
    },
    "card_title": "Уютная квартира в центре",
    "viewed_at": "2025-12-14T09:15:30Z",
    "duration_seconds": 23
  }
]
```

---

## 7️⃣ ПОДБОРКИ В КАРТОЧКЕ (LIST_CURATIONS)

### Структура в ответе карточки
```json
{
  "id": 1,
  "title": "Квартира в ЖК Парк у дома",
  "list_curations": [5, 12, 18],  // ID похожих квартир
  ...
}
```

### В ответе как объекты карточек (экономный формат)
```json
{
  "id": 1,
  "title": "Квартира в ЖК Парк у дома",
  "list_curations": [
    {
      "id": 5,
      "title": "Уютная квартира в центре",
      "price": 4200000,
      "rooms": 2,
      "area": 52,
      "city": 1,
      "rating": 4.5,
      "developer": {
        "id": 6,
        "name": "ЖК \"Парк у дома\"",
        "logo": "...",
        "is_subscribed": true
      },
      "is_favorite": false
    },
    {
      "id": 12,
      "title": "Семейная квартира с видом",
      "price": 4999999,
      "rooms": 2,
      "area": 62,
      "city": 1,
      "rating": 4.9,
      "developer": {...},
      "is_favorite": true
    }
  ],
  ...
}
```

---

## 📊 DJANGO ADMIN

### Управление подборками документов
```
Admin → Cards → CardDocumentList
```
- Создавать новые подборки
- Редактировать названия
- Просмотривать дату создания/обновления

### Просмотр истории просмотров
```
Admin → Cards → ViewHistory
```
- Фильтры: по пользователю, по карточке, по дате
- Просмотр времени просмотра (viewed_at)
- Просмотр длительности просмотра (duration_seconds)
- Защита: нельзя добавлять вручную (только через API)

---

## 🔐 БЕЗОПАСНОСТЬ

- ✅ `is_subscribed` зависит от текущего пользователя (request.user)
- ✅ ViewHistory защищена от анонимных пользователей
- ✅ CardDocumentList доступна всем, но редактируемая только админам
- ✅ All new endpoints require proper authentication where needed

---

## 🚀 РАЗВЁРТЫВАНИЕ

```bash
# 1. Применить миграции
python manage.py migrate

# 2. Перезагрузить сервер
supervisorctl restart dream_house

# 3. Проверить
python manage.py check
```

✅ **ВСЕ ИЗМЕНЕНИЯ ГОТОВЫ К ИСПОЛЬЗОВАНИЮ!**

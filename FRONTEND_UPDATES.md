# 🚀 ОБНОВЫ ДЛЯ ФРОНТЕНДА - API ИЗМЕНЕНИЯ

## 📌 ВЕРСИЯ: v1.2.0
## 📅 ДАТА: 14 декабря 2025
## ✅ СТАТУС: Production Ready

---

## 1️⃣ AI ЧАТ - УЛУЧШЕННЫЙ ПОИСК КВАРТИР

### Эндпоинт
```
POST /api/cards/ai/chat/
```

### Запрос (режим поиска)
```json
{
  "message": "Ищу красивую 2-комнатную квартиру в Махачкале до 5 миллионов",
  "user_preferences": {
    "city": 1,
    "rooms": 2,
    "house_type": "apartment",
    "price_max": 5000000
  },
  "mode": "search"
}
```

### Параметры `user_preferences`:
```
city: 1 (Махачкала), 2 (Каспийск), 3 (Дербент)
rooms: число комнат
house_type: "apartment" или "private"
price_min: минимальная цена
price_max: максимальная цена
```

### Ответ
```json
{
  "success": true,
  "response": "Я нашел для вас 3 отличные 2-комнатные квартиры в Махачкале...\n\n1. Современная квартира...",
  "tokens_used": 245,
  "referenced_cards": [1, 5, 12],
  "mode": "search"
}
```

### Что изменилось:
- ✅ **Умнее поиск** - разбирает ключевые слова, находит города по названию
- ✅ **Лучший контекст** - AI видит цену, площадь, рейтинг каждой квартиры
- ✅ **Оба режима работают** - 'search' и 'free'
- ✅ **Валидация** - проверяет пустые сообщения

---

## 2️⃣ AI ЧАТ - РЕЖИМ КОНСУЛЬТИРОВАНИЯ

### Запрос (режим free)
```json
{
  "message": "Чем отличается монолитный дом от панельного?",
  "mode": "free"
}
```

### Ответ
```json
{
  "success": true,
  "response": "Отличный вопрос! Вот основные различия:\n\n🏗️ МОНОЛИТНЫЕ...",
  "tokens_used": 189,
  "referenced_cards": [],
  "mode": "free"
}
```

### Что это дает:
- ✅ Консультации без поиска в БД
- ✅ Ответы на общие вопросы о недвижимости
- ✅ Советы по выбору квартиры

---

## 3️⃣ ИНФОРМАЦИЯ О ПОДПИСКЕ НА ЗАСТРОЙЩИКА

### Эндпоинт
```
GET /api/cards/{id}/
```

### Структура ответа (новое поле)
```json
{
  "id": 1,
  "title": "Квартира в ЖК Парк у дома",
  "price": 4850000,
  "developer": {
    "id": 6,
    "name": "ЖК \"Парк у дома\"",
    "logo": "https://api.dreamhouse05.com/media/developers/logos/i_3.webp",
    "is_subscribed": true
  },
  ...
}
```

### Что означает `is_subscribed`:
```
true  → пользователь подписан на этого застройщика
false → пользователь НЕ подписан на застройщика
```

### Использование на фронте:
```javascript
// Если подписан → показать "Отписаться"
// Если не подписан → показать "Подписаться"

if (card.developer.is_subscribed) {
  // Показать кнопку "Отписаться от застройщика"
} else {
  // Показать кнопку "Подписаться на застройщика"
}
```

---

## 4️⃣ ПОДБОРКИ В КАРТОЧКЕ (ПОХОЖИЕ ОБЪЕКТЫ)

### Структура ответа (новое поле)
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
  ]
}
```

### Как использовать:
```javascript
// Показать блок "Похожие квартиры" или "Подборка для вас"
card.list_curations.forEach(curation => {
  // Отобразить карточку с основной информацией
  console.log(`${curation.title} - ${curation.price}₽`);
});
```

### Что показать:
- Название
- Цену
- Комнаты и площадь
- Рейтинг
- Застройщика
- Кнопку "В избранное" / "Из избранного" (основана на `is_favorite`)

---

## 5️⃣ ПОДБОРКИ ДОКУМЕНТОВ

### Эндпоинт
```
GET /api/cards/{id}/document-lists/
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
        "file": "https://api.dreamhouse05.com/media/cards/documents/...",
        "uploaded_at": "2025-12-10T15:20:00Z"
      },
      {
        "id": 2,
        "title": "Договор купли-продажи",
        "file": "https://api.dreamhouse05.com/media/cards/documents/...",
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

### Как использовать:
```javascript
// Отобразить документы в группах по названиям
documentLists.forEach(list => {
  console.log(`Папка: ${list.name}`);
  list.documents.forEach(doc => {
    console.log(`  - ${doc.title} (скачать)`);
  });
});
```

### На фронте:
- Аккордион или вкладки с названиями подборок
- Внутри каждой - список документов
- Кнопка "Скачать" для каждого документа (link на `file`)

---

## 6️⃣ ИСТОРИЯ ПРОСМОТРОВ

### Сохранение просмотра (АВТОМАТИЧЕСКОЕ)
```
GET /api/cards/{id}/
```
→ **Просмотр автоматически сохраняется!**

### Явное сохранение с длительностью
```
POST /api/cards/{id}/view-history/

Тело:
{
  "duration_seconds": 45
}

Ответ:
{
  "message": "View saved",
  "id": 123
}
```

### Получение истории просмотров
```
GET /api/cards/view-history/me/
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
    "card": {...},
    "card_title": "Уютная квартира в центре",
    "viewed_at": "2025-12-14T09:15:30Z",
    "duration_seconds": 23
  }
]
```

### Как использовать:
```javascript
// Показать раздел "История просмотров"
viewHistory.forEach(view => {
  console.log(`${view.card_title} - просмотрена ${view.duration_seconds}с`);
});

// Или создать быстрый доступ к часто просматриваемым квартирам
const frequentlyViewed = viewHistory.slice(0, 5);
```

### Отслеживание на фронте:
```javascript
// При открытии карточки, засечь время
const startTime = Date.now();

// При закрытии или переходе
const duration = Math.floor((Date.now() - startTime) / 1000);
await fetch(`/api/cards/${cardId}/view-history/`, {
  method: 'POST',
  body: JSON.stringify({ duration_seconds: duration }),
  headers: { 'Content-Type': 'application/json' }
});
```

---

## 📋 ПОЛНЫЙ СПИСОК НОВЫХ ЭНДПОИНТОВ

| Метод | Путь | Описание |
|-------|------|---------|
| **POST** | `/api/cards/ai/chat/` | Чат с AI (поиск или консультация) |
| **GET** | `/api/cards/{id}/` | Карточка (обновлена структура developer + list_curations) |
| **GET** | `/api/cards/{id}/document-lists/` | Подборки документов |
| **POST** | `/api/cards/{id}/document-lists/create/` | Создать подборку (только админ) |
| **POST** | `/api/cards/{id}/view-history/` | Сохранить просмотр |
| **GET** | `/api/cards/view-history/me/` | Моя история просмотров |

---

## 🔐 ТРЕБОВАНИЯ АВТОРИЗАЦИИ

```
❌ GET  /api/cards/                      → AllowAny
❌ GET  /api/cards/{id}/                 → AllowAny
✅ POST /api/cards/ai/chat/              → IsAuthenticated
✅ GET  /api/cards/{id}/view-history/    → IsAuthenticated
✅ POST /api/cards/{id}/view-history/    → IsAuthenticated
✅ GET  /api/cards/view-history/me/      → IsAuthenticated
❌ GET  /api/cards/{id}/document-lists/  → AllowAny
✅ POST /api/cards/{id}/document-lists/create/ → IsAdminOrReadOnly
```

---

## 📱 ПРИМЕРЫ КОДА ДЛЯ ФРОНТА

### JavaScript/React - AI поиск

```javascript
async function searchApartments() {
  const response = await fetch('/api/cards/ai/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message: 'Ищу 2-комнатную квартиру в Махачкале',
      user_preferences: {
        city: 1,
        rooms: 2,
        price_max: 5000000
      },
      mode: 'search'
    })
  });

  const data = await response.json();
  console.log(data.response); // Ответ от AI
  
  // Получить ID рекомендованных квартир
  const cardIds = data.referenced_cards;
}
```

### JavaScript - Проверка подписки

```javascript
const card = await fetch(`/api/cards/${cardId}/`).then(r => r.json());

if (card.developer.is_subscribed) {
  // Показать кнопку "Отписаться"
  document.getElementById('subscribe-btn').textContent = 'Отписаться';
  document.getElementById('subscribe-btn').className = 'btn-unsubscribe';
} else {
  // Показать кнопку "Подписаться"
  document.getElementById('subscribe-btn').textContent = 'Подписаться';
  document.getElementById('subscribe-btn').className = 'btn-subscribe';
}
```

### JavaScript - Отобразить подборки

```javascript
const card = await fetch(`/api/cards/${cardId}/`).then(r => r.json());

if (card.list_curations && card.list_curations.length > 0) {
  // Показать блок "Похожие квартиры"
  const curations = card.list_curations.map(c => `
    <div class="curation-card">
      <h3>${c.title}</h3>
      <p>${c.price.toLocaleString('ru-RU')}₽</p>
      <p>${c.rooms} комнат • ${c.area}м²</p>
      <p>Рейтинг: ${c.rating}/5</p>
      <button onclick="viewCard(${c.id})">Смотреть</button>
    </div>
  `).join('');
  
  document.getElementById('curations-container').innerHTML = curations;
}
```

### JavaScript - История просмотров

```javascript
async function getViewHistory() {
  const response = await fetch('/api/cards/view-history/me/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const history = await response.json();
  
  history.forEach(view => {
    console.log(`Просмотрели: ${view.card_title}`);
    console.log(`Время просмотра: ${view.duration_seconds}с`);
  });
}
```

### JavaScript - Отслеживание времени просмотра

```javascript
let viewStartTime = null;

function openCard(cardId) {
  viewStartTime = Date.now();
  // Загрузить карточку...
}

function closeCard(cardId) {
  const duration = Math.floor((Date.now() - viewStartTime) / 1000);
  
  fetch(`/api/cards/${cardId}/view-history/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ duration_seconds: duration })
  });
}
```

---

## 🎨 РЕКОМЕНДУЕМЫЕ UI ИЗМЕНЕНИЯ

### 1. Карточка квартиры - добавить блоки:

```
┌─────────────────────────────────┐
│  Фото квартиры                  │
├─────────────────────────────────┤
│ Название                        │
│ Цена: 4.850.000₽              │
│ 2 комн | 56м² | Рейтинг: 4.8   │
├─────────────────────────────────┤
│ Застройщик: ЖК "Парк у дома"   │
│ [Подписаться / Отписаться]      │ ← NEW (is_subscribed)
├─────────────────────────────────┤
│ 📑 Подборки документов           │ ← NEW
│  • Правоустанавливающие        │
│  • Техническая документация     │
├─────────────────────────────────┤
│ 🔗 Похожие квартиры             │ ← NEW (list_curations)
│ [Карточка 1] [Карточка 2]      │
├─────────────────────────────────┤
│ Описание, отзывы, вопросы       │
└─────────────────────────────────┘
```

### 2. Добавить вкладку "Мои просмотры" в профиль

```
История просмотров:
- Квартира 1 (просмотрено 45 сек) 
- Квартира 2 (просмотрено 23 сек)
- Квартира 3 (просмотрено 1 мин)
```

### 3. Добавить чат с AI в меню

```
💬 Консультация с AI
├─ 🔍 Поиск квартир
└─ ❓ Общие вопросы
```

---

## 🧪 CURL ПРИМЕРЫ ДЛЯ ТЕСТИРОВАНИЯ

### AI поиск
```bash
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Ищу 2-комнатную квартиру в Махачкале",
    "user_preferences": {"city": 1, "rooms": 2},
    "mode": "search"
  }'
```

### История просмотров
```bash
curl http://localhost:8000/api/cards/view-history/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Документы
```bash
curl http://localhost:8000/api/cards/1/document-lists/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ CHECKLIST ДЛЯ ФРОНТ-РАЗРАБОТЧИКА

- [ ] Обновить компонент карточки квартиры
  - [ ] Добавить отображение `is_subscribed` в developer
  - [ ] Добавить блок "Похожие квартиры" (list_curations)
  - [ ] Добавить блок "Документы" (document_lists)

- [ ] Создать компонент AI чата
  - [ ] Форма для ввода сообщения
  - [ ] Выбор режима (поиск/консультация)
  - [ ] Отображение ответа AI
  - [ ] Клик на рекомендованные квартиры

- [ ] Добавить историю просмотров
  - [ ] Вкладка в профиле
  - [ ] Отображение списка просмотренных квартир
  - [ ] Отслеживание времени просмотра

- [ ] Обновить логику подписки на застройщика
  - [ ] Показать правильную кнопку (Подписаться/Отписаться)
  - [ ] Обновить состояние после клика

- [ ] Тестирование
  - [ ] Проверить все новые эндпоинты
  - [ ] Проверить авторизацию
  - [ ] Тесты на разных устройствах

---

**🚀 ОБНОВЫ ГОТОВЫ К ИСПОЛЬЗОВАНИЮ!**

Все новые функции интегрированы и протестированы.
Документация и примеры выше помогут вам быстро их внедрить.

Вопросы? Смотрите документы:
- `API_EXAMPLES.md` - полные примеры
- `CHANGES_SUMMARY.md` - техническое описание

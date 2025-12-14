# ⚡ QUICK START - БЫСТРЫЙ СТАРТ ДЛЯ ФРОНТЕНДА

## 🎯 ЧТО ИЗМЕНИЛОСЬ И ЧТО НУЖНО СДЕЛАТЬ

---

## #1 AI ЧАТ - ЧТО ДЕЛАТЬ

### ДО (старый код):
```javascript
// Поиск только в режиме search
POST /api/cards/ai/chat/
{
  "message": "Ищу квартиру",
  "user_preferences": {...}
}
```

### ПОСЛЕ (новый код):
```javascript
// Теперь два режима!
POST /api/cards/ai/chat/
{
  "message": "Ищу квартиру",
  "user_preferences": {...},
  "mode": "search"  // или "free"
}
```

### ✅ Что нужно добавить:
1. Поле `mode` в request (по умолчанию `"search"`)
2. Обработка `mode: "free"` для консультаций
3. Больше не нужна проверка на empty fields - валидируется на бэке

---

## #2 DEVELOPER - ПОДПИСКА

### ДО (старая структура):
```javascript
{
  "developer": {
    "id": 6,
    "name": "ЖК Парк у дома",
    "logo": "..."
  }
}
```

### ПОСЛЕ (новая структура):
```javascript
{
  "developer": {
    "id": 6,
    "name": "ЖК Парк у дома",
    "logo": "...",
    "is_subscribed": true  // ← НОВОЕ!
  }
}
```

### ✅ Что нужно добавить:
```javascript
// Проверить наличие is_subscribed
if (card.developer.is_subscribed) {
  // Показать "Отписаться"
} else {
  // Показать "Подписаться"
}
```

---

## #3 СПИСОК ПОДБОРОК В КАРТОЧКЕ

### ДО:
Поле `list_curations` не было вообще

### ПОСЛЕ:
```javascript
{
  "id": 1,
  "list_curations": [
    {
      "id": 5,
      "title": "Уютная квартира",
      "price": 4200000,
      "rooms": 2,
      "area": 52,
      ...
    }
  ]
}
```

### ✅ Что нужно добавить:
```javascript
// Проверить наличие подборок
if (card.list_curations && card.list_curations.length > 0) {
  // Показать блок "Похожие квартиры"
  card.list_curations.forEach(item => {
    // Отобразить как карточку
  });
}
```

---

## #4 ПОДБОРКИ ДОКУМЕНТОВ

### ДО:
```javascript
{
  "documents": [
    {"id": 1, "title": "Свидетельство", "file": "..."},
    {"id": 2, "title": "Договор", "file": "..."}
  ]
}
// Все документы в одном массиве
```

### ПОСЛЕ:
```javascript
GET /api/cards/{id}/document-lists/

[
  {
    "id": 1,
    "name": "Правоустанавливающие документы",
    "documents": [
      {"id": 1, "title": "Свидетельство", "file": "..."},
      {"id": 2, "title": "Договор", "file": "..."}
    ]
  },
  {
    "id": 2,
    "name": "Техническая документация",
    "documents": [...]
  }
]
```

### ✅ Что нужно добавить:
```javascript
// Вместо плоского списка - вложенная структура
async function loadDocuments(cardId) {
  const docs = await fetch(`/api/cards/${cardId}/document-lists/`)
    .then(r => r.json());
    
  // Документы теперь организованы в папки
  docs.forEach(list => {
    console.log(`Папка: ${list.name}`);
    list.documents.forEach(doc => {
      // Отобразить документ
    });
  });
}
```

---

## #5 ИСТОРИЯ ПРОСМОТРОВ

### ДО:
История просмотров не отслеживалась

### ПОСЛЕ:
```javascript
// Автоматически сохраняется при открытии карточки
GET /api/cards/{id}/

// Явное сохранение времени просмотра
POST /api/cards/{id}/view-history/
{ "duration_seconds": 45 }

// Получить мою историю
GET /api/cards/view-history/me/
```

### ✅ Что нужно добавить:

```javascript
// Отслеживать время просмотра
let startTime = null;

function openCard(cardId) {
  startTime = Date.now();
  // Загрузить карточку
}

function closeCard(cardId) {
  const seconds = Math.floor((Date.now() - startTime) / 1000);
  
  // Отправить на бэк
  fetch(`/api/cards/${cardId}/view-history/`, {
    method: 'POST',
    body: JSON.stringify({ duration_seconds: seconds }),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });
}

// Показать историю
async function showHistory() {
  const history = await fetch('/api/cards/view-history/me/')
    .then(r => r.json());
    
  history.forEach(view => {
    console.log(`${view.card_title} (${view.duration_seconds}с)`);
  });
}
```

---

## 📊 ТАБЛИЦА ИЗМЕНЕНИЙ

| Что | Было | Стало | Тип |
|-----|------|-------|-----|
| AI режимы | только search | search + free | ✅ Добавлено |
| Developer | 3 поля | + is_subscribed | ✅ Добавлено |
| Подборки | нет | list_curations | ✅ Добавлено |
| Документы | массив | структурированы | ✅ Изменено |
| История | нет | отслеживается | ✅ Добавлено |

---

## 🔴 ЧТО СЛОМАЛОСЬ?

**НИЧЕГО НЕ СЛОМАЛОСЬ!** ✅

- Все старые поля на месте
- Все старые эндпоинты работают
- Просто добавлены новые поля и функции
- 100% обратная совместимость

### Проверка совместимости:
```javascript
// Старый код сработает:
card.developer.id ✅
card.developer.name ✅
card.developer.logo ✅

// Новые поля опционально:
card.developer.is_subscribed ✅ (новое)
card.list_curations ✅ (новое)
card.document_lists ✅ (новое в main Card)
```

---

## 🚀 ПОШАГОВАЯ ИНТЕГРАЦИЯ

### Шаг 1: Обновить компонент Card (5 минут)
```javascript
function CardComponent(props) {
  const card = props.card;
  
  return (
    <div>
      {/* Старое */}
      <h1>{card.title}</h1>
      <p>{card.price}₽</p>
      
      {/* Новое - Developer + подписка */}
      {card.developer && (
        <div className="developer">
          <img src={card.developer.logo} />
          <h3>{card.developer.name}</h3>
          <button>
            {card.developer.is_subscribed ? 'Отписаться' : 'Подписаться'}
          </button>
        </div>
      )}
      
      {/* Новое - Похожие объекты */}
      {card.list_curations?.length > 0 && (
        <div className="curations">
          <h3>Похожие квартиры</h3>
          {card.list_curations.map(c => (
            <CuratorCard key={c.id} card={c} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### Шаг 2: Добавить компонент документов (5 минут)
```javascript
async function DocumentListsComponent(props) {
  const { cardId } = props;
  const docs = await fetch(`/api/cards/${cardId}/document-lists/`)
    .then(r => r.json());
    
  return (
    <div className="documents">
      {docs.map(list => (
        <div key={list.id} className="document-list">
          <h4>{list.name}</h4>
          {list.documents.map(doc => (
            <a key={doc.id} href={doc.file}>
              {doc.title} (скачать)
            </a>
          ))}
        </div>
      ))}
    </div>
  );
}
```

### Шаг 3: Добавить AI чат (10 минут)
```javascript
async function AIChatComponent() {
  const [message, setMessage] = useState('');
  const [mode, setMode] = useState('search');
  const [response, setResponse] = useState('');
  
  const handleChat = async () => {
    const result = await fetch('/api/cards/ai/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message,
        mode,  // ← НОВОЕ: выбор режима
        user_preferences: {
          city: 1,
          rooms: 2
        }
      }),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    }).then(r => r.json());
    
    setResponse(result.response);
  };
  
  return (
    <div>
      <input 
        value={message} 
        onChange={e => setMessage(e.target.value)} 
        placeholder="Что вы ищете?" 
      />
      
      <select value={mode} onChange={e => setMode(e.target.value)}>
        <option value="search">Поиск квартир</option>
        <option value="free">Консультация</option>
      </select>
      
      <button onClick={handleChat}>Отправить</button>
      
      {response && <p className="response">{response}</p>}
    </div>
  );
}
```

### Шаг 4: Добавить историю просмотров (10 минут)
```javascript
let viewStartTime;

function openCard(cardId) {
  viewStartTime = Date.now();
}

function closeCard(cardId) {
  const duration = Math.floor((Date.now() - viewStartTime) / 1000);
  fetch(`/api/cards/${cardId}/view-history/`, {
    method: 'POST',
    body: JSON.stringify({ duration_seconds: duration }),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });
}

async function ViewHistoryComponent() {
  const history = await fetch('/api/cards/view-history/me/')
    .then(r => r.json());
    
  return (
    <div className="history">
      <h2>История просмотров</h2>
      {history.map(view => (
        <div key={view.id}>
          <h4>{view.card_title}</h4>
          <p>Просмотрено: {view.duration_seconds}с</p>
        </div>
      ))}
    </div>
  );
}
```

---

## ⚙️ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

Ничего менять не нужно! API URL остается тем же.

```javascript
// Используйте существующий BASE_URL
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Просто добавляйте новые пути
const chatUrl = `${BASE_URL}/cards/ai/chat/`;
const historyUrl = `${BASE_URL}/cards/view-history/me/`;
const docsUrl = (cardId) => `${BASE_URL}/cards/${cardId}/document-lists/`;
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Чек-лист перед запуском:

- [ ] GET /api/cards/1/ → видно `is_subscribed`, `list_curations`
- [ ] POST /api/cards/ai/chat/ (mode: search) → работает
- [ ] POST /api/cards/ai/chat/ (mode: free) → работает
- [ ] GET /api/cards/1/document-lists/ → видны папки с документами
- [ ] POST /api/cards/1/view-history/ → сохраняется
- [ ] GET /api/cards/view-history/me/ → видна история

---

## 📞 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

1. **Ошибка 404** → путь неправильный (смотрите в FRONTEND_UPDATES.md таблицу)
2. **Ошибка 401** → забыли `Authorization` хедер
3. **Пустой ответ** → может быть, нет данных (проверьте в админ-панели)
4. **CORS ошибка** → уже исправлено на бэке (если нет, дайте знать)

---

## ✨ ГОТОВО!

Все примеры выше - это copy-paste готовый код.
Просто вставьте в свой проект и адаптируйте.

**Успехов! 🚀**

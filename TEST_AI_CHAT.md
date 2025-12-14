# 🔧 Тестирование AI Chat API

## ✅ Правильный способ вызова AI Chat

### 1️⃣ Сначала получите токен (Login)

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

**Ответ (сохраните токен):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2️⃣ Используйте токен в AI Chat запросе

⚠️ **ВАЖНО**: Токен должен быть в `Authorization` header как **`Bearer TOKEN`**

```bash
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "message": "Найди мне квартиры в Москве",
    "mode": "search"
  }'
```

**Или с user_preferences:**

```bash
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "Найди хорошую квартиру",
    "mode": "search",
    "user_preferences": {
      "min_price": 1000000,
      "max_price": 5000000,
      "city": "Москва",
      "rooms": 2
    }
  }'
```

---

## 📱 Пример для JavaScript/Fetch

```javascript
// 1. Получить токен
const loginResponse = await fetch('http://localhost:8000/api/users/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'your-email@example.com',
    password: 'your-password'
  })
});

const { access } = await loginResponse.json();

// 2. Использовать токен для AI Chat
const chatResponse = await fetch('http://localhost:8000/api/cards/ai/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access}`  // ✅ ПРАВИЛЬНЫЙ ФОРМАТ
  },
  body: JSON.stringify({
    message: 'Найди мне квартиры в Москве',
    mode: 'search'
  })
});

const result = await chatResponse.json();
console.log(result);
```

---

## 🐍 Пример для Python

```python
import requests

# 1. Получить токен
login_response = requests.post(
    'http://localhost:8000/api/users/login/',
    json={
        'email': 'your-email@example.com',
        'password': 'your-password'
    }
)

access_token = login_response.json()['access']

# 2. Использовать токен для AI Chat
chat_response = requests.post(
    'http://localhost:8000/api/cards/ai/chat/',
    headers={
        'Authorization': f'Bearer {access_token}'  # ✅ ПРАВИЛЬНЫЙ ФОРМАТ
    },
    json={
        'message': 'Найди мне квартиры в Москве',
        'mode': 'search'
    }
)

print(chat_response.json())
```

---

## ❌ ЧАСТЫЕ ОШИБКИ

### Ошибка 1: Забыли слово "Bearer"
```bash
# ❌ НЕПРАВИЛЬНО
-H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# ✅ ПРАВИЛЬНО
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ошибка 2: Забыли Authorization header вообще
```bash
# ❌ НЕПРАВИЛЬНО - возвращает 401
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "..."}'

# ✅ ПРАВИЛЬНО - добавьте Authorization header
curl -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "..."}'
```

### Ошибка 3: Неправильный режим
```bash
# ❌ НЕПРАВИЛЬНО - mode должен быть "search" или "free"
-d '{"message": "...", "mode": "invalid"}'

# ✅ ПРАВИЛЬНО
-d '{"message": "...", "mode": "search"}'
```

---

## 🔍 Как диагностировать 401?

### Шаг 1: Убедитесь, что пользователь зарегистрирован
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

Если возвращает `401` - пользователь не существует или пароль неправильный.

### Шаг 2: Убедитесь, что токен в правильном формате
```bash
# Скопируйте access токен из ответа выше и используйте его
echo "Мой токен: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Шаг 3: Проверьте Authorization header
```bash
# Посмотрите, что реально отправляется
curl -v -X POST http://localhost:8000/api/cards/ai/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "mode": "search"}'
```

Из вывода с флагом `-v` вы увидите, какие headers отправились.

---

## 📊 Структура ответа от AI Chat

### ✅ Успешный ответ (201 Created)
```json
{
  "id": 123,
  "user": 1,
  "message": "Найди мне квартиры в Москве",
  "response": "Нашел квартиры по вашим критериям...",
  "mode": "search",
  "created_at": "2024-01-15T10:30:00Z",
  "is_helpful": null,
  "search_results": [
    {
      "id": 1,
      "title": "Квартира 2-комнатная",
      "price": 3000000,
      "city": "Москва"
    }
  ]
}
```

### ❌ Ошибка 401 (Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Решение:** Добавьте `Authorization: Bearer TOKEN` header

### ❌ Ошибка 400 (Bad Request)
```json
{
  "message": ["This field is required."]
}
```

**Решение:** Проверьте, что отправляете `message` в JSON body

### ❌ Ошибка 503 (Service Unavailable)
```json
{
  "error": "AI provider error",
  "message": "Could not connect to OpenAI"
}
```

**Решение:** Проверьте:
- Что вы задали правильный AI provider (OpenAI/Claude/DeepSeek)
- Что у вас есть valid API key в `.env`
- Что сервис доступен

---

## 🧪 Быстрый тест с готовым пользователем

Если у вас уже есть суперпользователь, можете использовать его:

```bash
# Получить токен
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}'
```

Если не знаете пароль, создайте:
```bash
python manage.py createsuperuser
```

---

## 💡 Итог

**Главное правило:**

```
Authorization: Bearer {access_token}
```

Если вы видите **401 Unauthorized**, то скорее всего:
1. ❌ Забыли добавить `Authorization` header
2. ❌ Забыли слово `Bearer` перед токеном
3. ❌ Токен неправильный или истек
4. ❌ Пользователь не существует

Используйте примеры выше и все заработает! 🚀

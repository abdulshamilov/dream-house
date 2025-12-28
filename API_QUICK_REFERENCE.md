# 🚀 QUICK REFERENCE - Новые API Endpoints

## 📌 Профиль и Аккаунт

### Смена фото профиля
```
PUT /api/users/update-profile/
Content-Type: multipart/form-data

Body:
- profile_photo (file) - Фото (JPEG/PNG/GIF, макс 5MB)
- name (string) - Имя (optional)

Response (200):
{
  "id": 1,
  "phone_number": "+79999999999",
  "name": "John Doe",
  "profile_photo": "http://..."
}
```

### Удалить фото
```
DELETE /api/users/update-profile/

Response (200):
{ "detail": "Photo deleted successfully" }
```

### Удалить аккаунт
```
DELETE /api/users/delete-account/
Content-Type: application/json

Body:
{
  "password": "your_password"
}

Response (204): No Content
```

### Смена пароля
```
POST /api/users/change-password/
Content-Type: application/json

Body:
{
  "old_password": "current_password",
  "new_password": "new_password_123",
  "new_password_confirm": "new_password_123"
}

Response (200):
{ "detail": "Password changed successfully" }
```

### Регистрация с реферальным кодом
```
POST /api/users/register/
Content-Type: application/json

Body:
{
  "phone_number": "+79999999999",
  "password": "password123",
  "ref_code": "550e8400-e29b-41d4-a716-446655440000" (optional)
}

Response (201):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🏠 Карточки недвижимости

### Список карточек (с пагинацией)
```
GET /api/cards/?limit=10&page=1

Query params:
- limit (int) - Размер страницы (1-100, по умолчанию 10)
- page (int) - Номер страницы (по умолчанию 1)

Response (200):
{
  "count": 150,
  "next": "http://api/cards/?limit=10&page=2",
  "previous": null,
  "page": 1,
  "page_size": 10,
  "total_pages": 15,
  "results": [
    {
      "id": 1,
      "title": "Квартира 2+1",
      "address": "ул. Ленина, 10",
      "price": "5000000",
      "rooms": 2,
      "area": "70.5",
      "city": 1,
      "rating": "4.5",
      "list_curations": [
        {
          "id": 2,
          "title": "Похожая квартира",
          "address": "ул. Маркса, 5",
          "price": "4800000",
          ...
        }
      ]
    }
  ]
}
```

### Подборка для меня
```
GET /api/cards/recommendations/for-me/?limit=20&page=1

Auth: Required (JWT)

Query params:
- limit (int) - Размер страницы (1-100, по умолчанию 10)
- page (int) - Номер страницы (по умолчанию 1)

Response (200): Массив CardSerializer с пагинацией
```

### Недавно просмотренные (3-4 последние)
```
GET /api/cards/recent-views/?limit=4&page=1

Auth: Required (JWT)

Query params:
- limit (int) - Размер страницы (макс 4)
- page (int) - Номер страницы

Response (200): Массив CardSerializer (максимум 4 карточки)
```

### История чатов с AI (последние 5 сообщений)
```
GET /api/cards/ai/history/

Auth: Required (JWT)

Response (200):
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "message": "Найди квартиру в центре",
      "response": "Я нашел 5 подходящих вариантов...",
      "referenced_cards": [1, 2, 3],
      "created_at": "2025-12-28T12:00:00Z"
    }
  ]
}
```

---

## 📊 Структура ответов

### CardSerializer (полная карточка)
```json
{
  "id": 1,
  "title": "Квартира 2+1",
  "address": "ул. Ленина, 10",
  "description": "Красивая квартира в центре",
  "price": "5000000",
  "rooms": 2,
  "area": "70.5",
  "city": 1,
  "house_type": "apartment",
  "building_material": "brick",
  "category": "new_building",
  "floors_total": 10,
  "ceiling_height": "2.70",
  "elevator": "passenger",
  "parking": "underground",
  "balcony": true,
  "rating": "4.5",
  "rating_count": 42,
  "latitude": 43.1234,
  "longitude": 47.5678,
  "developer": {
    "id": 1,
    "name": "АО Строй",
    "logo": "http://...",
    "is_subscribed": false
  },
  "list_curations": [
    {
      "id": 2,
      "title": "Похожая квартира",
      "address": "ул. Маркса, 5",
      "price": "4800000",
      "rooms": 2,
      "area": "68.0",
      "city": 1,
      "rating": "4.3",
      "is_favorite": false
    }
  ],
  "is_favorite": false,
  "created_at": "2025-12-20T10:00:00Z"
}
```

### CustomPagination ответ
```json
{
  "count": 150,
  "next": "http://api/resource/?limit=10&page=2",
  "previous": null,
  "page": 1,
  "page_size": 10,
  "total_pages": 15,
  "results": [...]
}
```

---

## ⚠️ Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 🔐 Авторизация

Все endpoints требующие `Auth: Required` должны включать JWT токен:

```
Header: Authorization: Bearer {access_token}
```

Получение токенов:
```
POST /api/users/register/        # При регистрации
POST /api/users/login/           # При входе
POST /api/token/refresh/         # Обновление токена
```

---

## 📱 Примеры кода

### JavaScript/Fetch
```javascript
// Смена фото
const formData = new FormData();
formData.append('profile_photo', fileInput.files[0]);
formData.append('name', 'New Name');

const response = await fetch('/api/users/update-profile/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

// Список с пагинацией
const response = await fetch('/api/cards/?limit=20&page=2', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const data = await response.json();
console.log(`Страница ${data.page} из ${data.total_pages}`);
console.log(`Всего элементов: ${data.count}`);
```

### React Hook
```javascript
const useCards = (limit = 10, page = 1) => {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/cards/?limit=${limit}&page=${page}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(r => r.json())
    .then(data => {
      setCards(data.results);
      setLoading(false);
    })
    .catch(err => {
      setError(err);
      setLoading(false);
    });
  }, [limit, page, token]);

  return { cards, loading, error };
};
```

### Python
```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Регистрация с реф. кодом
response = requests.post(
    'http://localhost:8000/api/users/register/',
    json={
        'phone_number': '+79999999999',
        'password': 'password123',
        'ref_code': 'uuid-here'
    }
)

# Список с пагинацией
response = requests.get(
    'http://localhost:8000/api/cards/',
    headers=headers,
    params={'limit': 20, 'page': 1}
)

data = response.json()
print(f"Всего: {data['count']} | Страниц: {data['total_pages']}")
```

---

## 🧪 Тестирование

### cURL примеры

Все endpoints:
```bash
# Смена фото
curl -X PUT http://localhost:8000/api/users/update-profile/ \
  -H "Authorization: Bearer TOKEN" \
  -F "profile_photo=@photo.jpg"

# Список с пагинацией
curl http://localhost:8000/api/cards/?limit=20&page=1 \
  -H "Authorization: Bearer TOKEN"

# Подборка для меня
curl http://localhost:8000/api/cards/recommendations/for-me/ \
  -H "Authorization: Bearer TOKEN"

# Недавно просмотренные
curl http://localhost:8000/api/cards/recent-views/ \
  -H "Authorization: Bearer TOKEN"

# История чатов (5 максимум)
curl http://localhost:8000/api/cards/ai/history/ \
  -H "Authorization: Bearer TOKEN"
```

---

## ✨ Новые возможности

✅ Смена фото с валидацией (5MB, JPEG/PNG/GIF)  
✅ Удаление аккаунта с подтверждением пароля  
✅ История чатов ограничена 5 сообщениями  
✅ Персональные рекомендации на основе просмотров  
✅ Реферальная программа при регистрации  
✅ Адрес включен в подборки  
✅ Недавние просмотры (3-4 последние)  
✅ Пагинация со статистикой (limit/page)  

---

**Version**: 2.0  
**Last Updated**: 28 Dec 2025  
**Status**: ✅ Production Ready

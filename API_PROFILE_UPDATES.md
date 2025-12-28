# API для смены фото и удаления аккаунта

Документация по новой функциональности для управления профилем пользователя.

## 1. Смена фото профиля (Update Profile Photo)

### Endpoint
```
PUT /api/users/update-profile/
```

### Авторизация
Требуется JWT токен в заголовке `Authorization: Bearer {access_token}`

### Описание
Позволяет пользователю загрузить новое фото профиля или изменить имя.

### Параметры запроса
- `profile_photo` (file, optional) - Новое фото профиля
  - Поддерживаемые форматы: JPEG, PNG, GIF
  - Максимальный размер: 5MB
- `name` (string, optional) - Новое имя пользователя (максимум 50 символов)

### Пример запроса (cURL)
```bash
curl -X PUT http://localhost:8000/api/users/update-profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "profile_photo=@/path/to/photo.jpg" \
  -F "name=John Doe"
```

### Пример запроса (Python)
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
}

files = {
    'profile_photo': open('/path/to/photo.jpg', 'rb'),
}

data = {
    'name': 'John Doe'
}

response = requests.put(
    'http://localhost:8000/api/users/update-profile/',
    headers=headers,
    files=files,
    data=data
)

print(response.json())
```

### Успешный ответ (200 OK)
```json
{
  "id": 1,
  "phone_number": "+79999999999",
  "name": "John Doe",
  "profile_photo": "http://localhost:8000/media/users/profiles/photo_abc123.jpg"
}
```

### Ошибки
- `400 Bad Request` - Файл слишком большой или неподдерживаемый формат
- `401 Unauthorized` - Токен отсутствует или неверный
- `403 Forbidden` - Доступ запрещен

### Валидация
- Размер фото не должен превышать 5MB
- Поддерживаются только форматы: JPEG, PNG, GIF
- Имя не должно превышать 50 символов

---

## 2. Удаление фото профиля (Delete Profile Photo)

### Endpoint
```
DELETE /api/users/update-profile/
```

### Авторизация
Требуется JWT токен в заголовке `Authorization: Bearer {access_token}`

### Описание
Удаляет текущее фото профиля пользователя.

### Пример запроса (cURL)
```bash
curl -X DELETE http://localhost:8000/api/users/update-profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Пример запроса (Python)
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
}

response = requests.delete(
    'http://localhost:8000/api/users/update-profile/',
    headers=headers
)

print(response.json())
```

### Успешный ответ (200 OK)
```json
{
  "detail": "Photo deleted successfully"
}
```

---

## 3. Удаление аккаунта (Delete Account)

### Endpoint
```
DELETE /api/users/delete-account/
```

### Авторизация
Требуется JWT токен в заголовке `Authorization: Bearer {access_token}`

### Важно ⚠️
**Эта операция необратима!** При удалении аккаунта будут удалены:
- Все данные профиля
- Все квартиры/объекты недвижимости
- Все отзывы и комментарии
- История чатов и сообщений
- Все связанные файлы и фото

### Параметры запроса
- `password` (string, required) - Пароль пользователя для подтверждения

### Пример запроса (cURL)
```bash
curl -X DELETE http://localhost:8000/api/users/delete-account/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "user_password"}'
```

### Пример запроса (Python)
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
}

data = {
    'password': 'user_password'
}

response = requests.delete(
    'http://localhost:8000/api/users/delete-account/',
    headers=headers,
    json=data
)

print(response.status_code)
print(response.json())
```

### Успешный ответ (204 No Content)
```
[Пустой ответ с кодом 204]
```

### Альтернативный ответ (204 с сообщением)
```json
{
  "detail": "Account and all associated data deleted successfully"
}
```

### Ошибки
- `400 Bad Request` - Неверный пароль
- `401 Unauthorized` - Токен отсутствует или неверный

### Примечания
- Пароль обязателен для подтверждения удаления
- После удаления аккаунта пользователь будет выведен из системы
- Невозможно восстановить удаленный аккаунт

---

## 4. Смена пароля (Change Password)

### Endpoint
```
POST /api/users/change-password/
```

### Авторизация
Требуется JWT токен в заголовке `Authorization: Bearer {access_token}`

### Параметры запроса
- `old_password` (string, required) - Текущий пароль
- `new_password` (string, required) - Новый пароль (минимум 6 символов)
- `new_password_confirm` (string, required) - Подтверждение нового пароля

### Пример запроса
```bash
curl -X POST http://localhost:8000/api/users/change-password/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "current_password",
    "new_password": "new_password_123",
    "new_password_confirm": "new_password_123"
  }'
```

### Успешный ответ (200 OK)
```json
{
  "detail": "Password changed successfully"
}
```

---

## 5. Получение информации о текущем пользователе (Me)

### Endpoint
```
GET /api/users/me/
```

### Авторизация
Требуется JWT токен

### Пример запроса
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Успешный ответ (200 OK)
```json
{
  "id": 1,
  "phone_number": "+79999999999",
  "name": "John Doe",
  "profile_photo": "http://localhost:8000/media/users/profiles/photo_abc123.jpg"
}
```

---

## Коды состояния HTTP

| Код | Значение |
|-----|----------|
| 200 | OK - Успешный запрос |
| 204 | No Content - Успешно удалено |
| 400 | Bad Request - Неверные параметры |
| 401 | Unauthorized - Требуется авторизация |
| 403 | Forbidden - Доступ запрещен |
| 404 | Not Found - Ресурс не найден |
| 500 | Internal Server Error - Ошибка сервера |

---

## Требования безопасности

1. **Все запросы** должны выполняться по HTTPS в production
2. **JWT токены** должны храниться безопасно на клиенте
3. **Пароли** всегда передаются в теле запроса (никогда в URL)
4. **Фото профиля** автоматически валидируются по размеру и типу

---

## Миграции БД

После обновления кода выполните:
```bash
python manage.py migrate
```

Эти изменения не требуют новых миграций, так как используют существующие поля модели User.

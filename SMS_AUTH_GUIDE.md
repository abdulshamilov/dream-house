# SMS-Based Authentication (как Ozon)

## Описание
Система авторизации без пароля, основанная на SMS кодах. Пользователь вводит номер телефона, получает OTP код, и может зайти в систему введя правильный код.

## Endpoints

### 1. Запрос OTP кода
**POST** `/api/users/sms/request/`

#### Request:
```json
{
  "phone_number": "+79991234567"
}
```

#### Response (200 OK):
```json
{
  "detail": "OTP sent to your phone",
  "otp": "123456"
}
```

**Note:** В продакшене поле `otp` не должно возвращаться! Это только для разработки.

---

### 2. Проверка OTP и вход/регистрация
**POST** `/api/users/sms/verify/`

#### Request:
```json
{
  "phone_number": "+79991234567",
  "otp": "123456"
}
```

#### Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "phone_number": "+79991234567",
    "name": null,
    "profile_photo": null
  },
  "is_new": true
}
```

#### Ошибки:
- `400` - Invalid OTP (неверный код)
- `400` - OTP expired or already used (код истек или уже использован)

---

## Процесс авторизации

### Шаг 1: Запросить OTP
```bash
curl -X POST "http://localhost:8000/api/users/sms/request/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+79991234567"}'
```

### Шаг 2: Получить OTP из SMS (или из response в dev)
Код действует 5 минут.

### Шаг 3: Отправить код для верификации
```bash
curl -X POST "http://localhost:8000/api/users/sms/verify/" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+79991234567", "otp": "123456"}'
```

### Шаг 4: Сохранить токены и использовать
```bash
# Использовать access token для доступа к защищённым endpoints
curl -X GET "http://localhost:8000/api/users/me/" \
  -H "Authorization: Bearer <access_token>"
```

---

## Логика

1. **Первый вход**: Если пользователя с таким номером нет, он будет автоматически создан
2. **Повторный вход**: Если пользователь существует, он просто получит новые токены
3. **OTP Валидность**: 5 минут с момента создания
4. **Пароль**: Для SMS-авторизации пароль генерируется случайно и не используется

---

## Интеграция с SMS провайдером

### Текущее состояние (Development):
```python
# В SMSRequestView.post():
print(f"OTP for {phone_number}: {otp}")  # Печатает в консоль
# Также возвращается в response для разработки
```

### Интеграция с реальным SMS провайдером:
Замените логику отправки в `SMSRequestView.post()`:

#### Пример с Twilio:
```python
from twilio.rest import Client

account_sid = 'your_sid'
auth_token = 'your_token'
client = Client(account_sid, auth_token)

message = client.messages.create(
    body=f"Your verification code: {otp}",
    from_='+1234567890',
    to=phone_number
)
```

#### Пример с AWS SNS:
```python
import boto3

sns = boto3.client('sns')
sns.publish(
    PhoneNumber=phone_number,
    Message=f"Your verification code: {otp}"
)
```

---

## Безопасность

### Production Checklist:
- [ ] Удалить поле `otp` из response `SMSRequestView`
- [ ] Интегрировать реальный SMS провайдер
- [ ] Настроить rate limiting для endpoint'ов
- [ ] Добавить логирование попыток входа
- [ ] Использовать HTTPS
- [ ] Увеличить complexity OTP генератора если нужно

### Rate Limiting Рекомендация:
```python
# Ограничивать количество OTP запросов с одного номера
# Например: максимум 3 запроса в 30 минут
```

---

## Связанные Endpoints

- `GET /api/users/me/` - Получить информацию о текущем пользователе (требует токен)
- `POST /api/users/logout/` - Выход (удаление токенов на клиенте)
- `PUT /api/users/update-profile/` - Обновить профиль (имя, фото)


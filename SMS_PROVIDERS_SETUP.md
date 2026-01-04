# SMS Провайдеры - Инструкция по подключению

## Текущее состояние

В dev режиме (`DEBUG=True`) SMS коды печатаются в консоль и возвращаются в response для удобства тестирования.
Дополнительно можно управлять поведением через переменные:
- `SEND_REAL_SMS` — если `true`, отправляет реальное SMS даже при `DEBUG=True`
- `SMS_DEBUG_RETURN_OTP` — если `true`, возвращает OTP в ответе (НЕ включать в прод)

## Подключение реального SMS провайдера

### Шаг 1: Выбрать провайдера

Поддерживаемые провайдеры:
- **Twilio** - популярный, надёжный, есть free tier
- **AWS SNS** - если уже используешь AWS
- **Email-to-SMS** - для российских операторов (MTS, Beeline, Megafon, Rostelecom)
- **sms.ru** - российский провайдер, простой HTTP API

### Шаг 2: Настроить переменные окружения

#### Вариант 1: Twilio

```bash
# .env или set env vars
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

Установить клиент:
```bash
pip install twilio
```

#### Вариант 2: AWS SNS

```bash
SMS_PROVIDER=aws
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

Установить клиент:
```bash
pip install boto3
```

#### Вариант 3: Email-to-SMS (для России)

```bash
SMS_PROVIDER=smtp
SMS_CARRIER=mts  # или beeline, megafon, rostelecom
```

#### Вариант 4: sms.ru

```bash
SMS_PROVIDER=smsru
SMSRU_API_ID=your_smsru_api_id
# Опционально: FROM алфанумерик, если одобрен
```

### Шаг 3: Обновить `requirements.txt`

В зависимости от провайдера:

```
twilio>=8.0.0    # для Twilio
boto3>=1.26.0    # для AWS SNS
```

### Шаг 4: Как работает отправка

**Файл:** `users/views.py` → `SMSRequestView._send_sms()`

```python
def _send_sms(self, phone_number, otp):
    if DEBUG:
        # Dev: печатает в консоль
        logger.info(f"[SMS DEV] OTP for {phone_number}: {otp}")
    else:
        # Prod: отправляет реальное SMS
        self._send_via_provider(phone_number, otp)
```

---

## Примеры использования

### Twilio

**Регистрация:**
1. Создать аккаунт на https://www.twilio.com/
2. Получить Account SID и Auth Token
3. Купить номер для отправки SMS

**Test:**
```bash
curl -X POST http://localhost:8000/api/users/sms/request/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+79991234567"}'
```

### AWS SNS

**Регистрация:**
1. AWS аккаунт
2. IAM пользователь с SNS permissions
3. Access Key ID и Secret Access Key

**Test:**
```bash
AWS_REGION=us-east-1 python manage.py shell
>>> from users.views import SMSRequestView
>>> view = SMSRequestView()
>>> view._send_via_aws_sns("+79991234567", "123456")
```

### Email-to-SMS (Россия)

Для российских номеров можно использовать email-to-SMS гейтвеи:
- MTS: `79991234567@mts.ru`
- Beeline: `79991234567@beelinetel.ru`
- Megafon: `79991234567@megafon.ru`
- Rostelecom: `79991234567@rostelecom.ru`

Это требует настройки SMTP.

---

## Безопасность для Production

### Checklist:

```
[ ] Удалить OTP из response (сейчас возвращается для dev)
[ ] Настроить реальный SMS провайдер
[ ] Использовать HTTPS
[ ] Добавить rate limiting на endpoints
[ ] Логировать попытки входа
[ ] Настроить логирование ошибок SMS
[ ] Добавить alerting если SMS не отправляется
[ ] Использовать environment переменные для всех ключей
[ ] Не коммитить credentials в git
```

### Пример обновления response для production:

```python
# Текущее (DEV):
return Response({
    "detail": "OTP sent to your phone",
    "otp": otp if settings.DEBUG else None  # убрать otp в prod
}, status=200)

# Production-ready:
return Response({
    "detail": "OTP sent to your phone"
}, status=200)
```

---

## Rate Limiting (рекомендация)

Добавить в `requirements.txt`:
```
djangorestframework-ratelimit
```

Использовать в views:
```python
from rest_framework.throttling import UserRateThrottle

class SMSThrottle(UserRateThrottle):
    scope = 'sms'
    rate = '3/h'  # 3 запроса в час с одного номера

class SMSRequestView(APIView):
    throttle_classes = [SMSThrottle]
```

---

## Логирование

Все SMS события логируются. Проверить логи:

```python
import logging
logger = logging.getLogger('users.views')

# Смотреть логи в консоли или в файле:
# DEBUG: [SMS DEV] OTP for +79991234567: 123456
# INFO: SMS sent via Twilio. SID: SM1234567890abcdef
# ERROR: Twilio error: Invalid phone number
```

---

## Troubleshooting

### OTP не приходит
- Проверить логи сервера
- Проверить credentials SMS провайдера
- Проверить номер телефона (правильный формат?)
- Проверить баланс в аккаунте провайдера

### InvalidPhoneNumber ошибка
- Номер должен быть в формате `+79991234567`
- Не должно быть пробелов или дефисов в коде

### TimeoutError
- Провайдер не ответил
- Проверить интернет
- Проверить credentials


# p1sms - Интеграция

## Краткое описание

p1sms - российский SMS провайдер с удобным API. Отличный выбор для отправки OTP кодов в России.

## Настройка

### 1. Получить API ключ

1. Зарегистрируйтесь на https://p1sms.ru/
2. Пополните баланс
3. Получите API ключ в личном кабинете

### 2. Настроить environment переменные

```bash
# .env файл или переменные окружения
SMS_PROVIDER=p1sms
P1SMS_API_KEY=FhcWTKyO2r5ed3PSLiTMu2ZQ409EMjp8ajB6FtS21Y1EJnMqxjUQU8u3RTOK

# Отключить DEBUG для production
DEBUG=False
```

### 3. Установить зависимости

```bash
pip install requests
```

## Как это работает

### API Endpoint

```
POST https://p1sms.ru/api/push
```

### Параметры запроса

| Параметр | Описание | Пример |
|----------|---------|--------|
| `key` | Ваш API ключ | `FhcWTK...` |
| `to` | Номер телефона (11 цифр, начиная с 7) | `79991234567` |
| `text` | Текст сообщения (не более 160 символов) | `Kod: 123456` |
| `from` | Имя отправителя (опционально) | `DreamHouse` |

### Пример запроса

```bash
curl -X POST https://p1sms.ru/api/push \
  -d "key=FhcWTK..." \
  -d "to=79991234567" \
  -d "text=Kod: 123456" \
  -d "from=DreamHouse"
```

## Автоматическое преобразование номеров

Система автоматически преобразует номера телефонов:
- `+79991234567` → `79991234567`
- `89991234567` → `79991234567`
- `9991234567` → `79991234567`

## Тестирование

### Локально (DEBUG=True)

OTP печатается в консоль и возвращается в response.

### Production (DEBUG=False)

OTP отправляется реальное SMS через p1sms API.

### Проверить отправку

```python
import requests
import os
from users.views import SMSRequestView

os.environ['SMS_PROVIDER'] = 'p1sms'
os.environ['P1SMS_API_KEY'] = 'your_key'
os.environ['DEBUG'] = 'False'

view = SMSRequestView()
request_obj = type('Request', (), {'method': 'POST'})()
logger = __import__('logging').getLogger()

view._send_sms('+79991234567', '123456')  # Should send real SMS
```

## Стоимость

- SMS в Россию: ~0.5-1 рубль за сообщение
- Интеграция: Бесплатная

## Документация p1sms

- Официальный сайт: https://p1sms.ru/
- API документация: https://p1sms.ru/api-docs/
- Поддержка: support@p1sms.ru

## Что делает код

1. **Валидация ключа**: Проверяет наличие API ключа
2. **Нормализация номера**: Преобразует номер в формат `7XXXXXXXXXX`
3. **Форматирование текста**: Подготавливает OTP сообщение
4. **Отправка**: Делает POST запрос к p1sms API
5. **Логирование**: Логирует успешную отправку или ошибку

## Обработка ошибок

| Ошибка | Решение |
|--------|---------|
| API key not configured | Проверить `P1SMS_API_KEY` в env |
| Timeout | Интернет соединение или перегруз p1sms |
| Invalid phone number | Проверить формат номера |
| Insufficient balance | Пополнить баланс в личном кабинете |

## Логирование

Все события логируются в `logs/` или консоль:

```
INFO: SMS sent via p1sms to +79991234567. Response: {status: ok, id: 123}
ERROR: p1sms error: Insufficient balance
```

## Security

- ✅ API ключ хранится в env переменных (не в коде)
- ✅ Номера телефонов нормализуются
- ✅ OTP код генерируется случайно
- ✅ OTP действует 5 минут
- ✅ OTP помечается как использованный после входа


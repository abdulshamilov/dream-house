# 💜 DeepSeek API Setup Guide

## 🎯 Почему DeepSeek?

- **Цена**: DeepSeek R1 в 5-10 раз дешевле GPT-4
- **Качество**: Сравнимо с GPT-4, Claude 3.5
- **Скорость**: Быстрая обработка на русском языке
- **Простота**: OpenAI-совместимый API (используем ту же библиотеку что и для OpenAI)

---

## 📥 Шаг 1: Получить API ключ

1. **Переходим на** https://platform.deepseek.com/
2. **Регистрируемся** (если не зарегистрированы)
3. **Вводим номер телефона** для подтверждения
4. **Переходим в Dashboard** → API Keys
5. **Создаем новый ключ** ("Create API Key")
6. **Копируем ключ** (выглядит как `sk-...`)

> **Внимание!** Скопируйте сразу, вторично не покажет!

---

## 🔧 Шаг 2: Установить переменную окружения

### Windows PowerShell:
```powershell
# Установить переменную (только для текущей сессии)
$env:DEEPSEEK_API_KEY = "sk-your-deepseek-key-here"

# Проверить
echo $env:DEEPSEEK_API_KEY
```

### Постоянно (Windows):
```powershell
# Через переменные окружения системы
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-your-key", "User")
```

### Linux/Mac:
```bash
export DEEPSEEK_API_KEY="sk-your-deepseek-key-here"
```

---

## ⚙️ Шаг 3: Настроить в админке

1. **Откройте** https://api.dreamhouse05.com/admin/
2. **Войдите** с admin/admin
3. **Найдите** "AI Ассистент"
4. **Отредактируйте** существующую запись или создайте новую:

| Параметр | Значение |
|----------|----------|
| Имя | Dream House AI |
| API провайдер | **DeepSeek** |
| API ключ | (оставить пусто - будет использована переменная окружения) |
| Модель | `deepseek-chat` или `deepseek-reasoner` |
| Temperature | 0.7 |
| Max tokens | 500 |
| Активно | ✅ (галочка) |

### Выбор модели:

- **`deepseek-chat`** - быстрая, хорошо подходит для реального времени
- **`deepseek-reasoner`** - медленнее, но умнее, лучше для сложных задач

---

## 🧪 Шаг 4: Тестирование

### Через curl:
```bash
$TOKEN = "your_access_token"

curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "message": "Найди мне квартиру в Махачкале за 3 миллиона",
    "user_preferences": {
      "city": 1,
      "rooms": 3,
      "price_max": 3000000
    }
  }'
```

### Ожидаемый ответ:
```json
{
  "id": 42,
  "message": "Найди мне квартиру в Махачкале за 3 миллиона",
  "response": "Я нашел для вас отличные варианты...",
  "referenced_cards": [1, 2, 3],
  "tokens_used": 245,
  "is_helpful": null,
  "created_at": "2025-12-11T18:20:00Z"
}
```

---

## 💰 Смета затрат

DeepSeek очень дешевый! Вот примерные цены:

| Операция | Цена |
|---------|------|
| 1000 токенов input (deepseek-chat) | $0.14 |
| 1000 токенов output (deepseek-chat) | $0.28 |
| 1000 токенов input (deepseek-reasoner) | $0.55 |
| 1000 токенов output (deepseek-reasoner) | $2.19 |

**Пример:** 100 чатов по 300 токенов = 30k токенов = примерно $0.10

---

## 🔗 API Совместимость

DeepSeek использует OpenAI-совместимый API, поэтому:

```python
# Один и тот же код работает!
from openai import OpenAI

# Для OpenAI
client = OpenAI(api_key="sk-...")

# Для DeepSeek (просто другой base_url)
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com")
```

---

## 📊 Мониторинг использования

1. **Входите** на https://platform.deepseek.com/dashboard
2. **Смотрите** Usage → Billing
3. **Видите** сколько потрачено токенов за период
4. **Устанавливаете** лимиты если нужно

---

## ❓ FAQ

**Q: Может ли DeepSeek русский?**
A: Да! Отлично понимает и генерирует на русском. Может быть даже лучше чем GPT-4 для русского контекста.

**Q: А если закончится бюджет?**
A: API вернет ошибку, чат просто не будет работать. Пополните баланс на платформе.

**Q: Какая модель лучше?**
A: Для недвижимости используйте `deepseek-chat` - быстрее и достаточно умна. `deepseek-reasoner` нужна для очень сложных задач.

**Q: Как переключиться между моделями?**
A: В админке измените `model_name` и сохраните. Готово!

**Q: Может ли быть одновременно несколько AI Assistant?**
A: Да, но в админке работает только первый активный (is_active=True).

---

## 🚀 Использование в коде

Если хотите использовать DeepSeek в своем Python коде:

```python
from cards.ai_service import AIAssistantService

ai = AIAssistantService()

result = ai.chat(
    user_message="Помогите выбрать недвижимость",
    user_preferences={'city': 1, 'rooms': 3},
    user_id=123
)

print(result['response'])
print(f"Стоимость: ~${result['tokens_used'] * 0.0002}")  # примерный расчет
```

---

## 📞 Поддержка

- **Документация DeepSeek**: https://api-docs.deepseek.com/
- **Статус API**: https://status.deepseek.com/
- **На что пожаловаться**: support@deepseek.com

---

**Всё готово! Используйте DeepSeek и экономьте 💜**

# 🤖 AI Provider Comparison

## Сравнение провайдеров API

| Параметр | OpenAI (GPT-4) | Anthropic (Claude) | DeepSeek (R1) |
|----------|---|---|---|
| **Цена (1M токенов)** | $30 input / $60 output | $3 input / $15 output | $0.14 input / $0.28 output ⭐ |
| **Качество** | Отличное | Отличное | Отличное |
| **Скорость** | Быстро | Средне | Быстро |
| **Русский язык** | Хорошо | Хорошо | Отлично ⭐ |
| **Контекст** | 128K токенов | 100K токенов | 64K токенов |
| **Соответствие API** | Native | Native | OpenAI-совместимый ⭐ |
| **Рекомендуется для** | Высокие требования | Безопасность | 💵 Экономия |

---

## 🚀 Рекомендации

### Начинающим (разработка)
👉 **Используйте DeepSeek** 
- Дешево экспериментировать
- Хорошего качества
- OpenAI SDK, никаких различий в коде

### Production (высокие требования)
👉 **Используйте OpenAI**
- Стабильность
- Наилучшее качество для английского
- Широкая поддержка

### Безопасность (конфиденциальные данные)
👉 **Используйте Anthropic (Claude)**
- Лучший контроль над безопасностью
- Прекрасный русский
- Дороже, но надежнее

---

## 📋 Быстрая справка

### Установка ключей

```bash
# DeepSeek (РЕКОМЕНДУЕТСЯ)
$env:DEEPSEEK_API_KEY = "sk-..."

# OpenAI
$env:OPENAI_API_KEY = "sk-..."

# Anthropic
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### Названия моделей

```
OpenAI:    gpt-4, gpt-4-turbo, gpt-3.5-turbo
Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku
DeepSeek:  deepseek-chat, deepseek-reasoner
```

---

## 💾 Текущая конфигурация

```python
# cards/models.py - AIAssistant model
api_provider = models.CharField(
    max_length=50,
    choices=[
        ('openai', 'OpenAI (GPT-4)'),
        ('anthropic', 'Anthropic (Claude)'),
        ('deepseek', 'DeepSeek (R1)'),
        ('disabled', 'Отключен'),
    ],
    default='openai'
)
```

---

## 🔄 Переключение между провайдерами

1. Откройте `/admin/cards/aiassistant/`
2. Измените `api_provider` на нужный
3. Убедитесь что переменная окружения установлена
4. Сохраните
5. Готово! API автоматически переключится

---

## 📝 Примеры использования

### Python

```python
from cards.ai_service import AIAssistantService

ai = AIAssistantService()

result = ai.chat(
    user_message="Найди квартиру в Махачкале",
    user_preferences={"city": 1, "price_max": 3000000},
    user_id=123
)

print(f"Ответ: {result['response']}")
print(f"Токенов: {result['tokens_used']}")
```

### cURL

```bash
curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Какие квартиры в Махачкале?",
    "user_preferences": {"city": 1}
  }'
```

---

## 🔐 Безопасность API ключей

### ✅ DO:
- Используйте переменные окружения (`$env:...` или `export ...`)
- Хранитесь ключи в `.env` файле (в `.gitignore`)
- Регулярно ротируйте ключи
- Используйте разные ключи для dev/prod

### ❌ DON'T:
- Не коммитьте ключи в гит
- Не показывайте ключи логах
- Не используйте одинаковые ключи для разных проектов
- Не делитесь ключами по сети в открытом виде

---

## 📞 Поддержка

**OpenAI**: https://support.openai.com/
**Anthropic**: https://support.anthropic.com/
**DeepSeek**: https://api-docs.deepseek.com/

---

**Выбрали провайдера? Следуйте соответствующему гайду:**
- 💜 **DeepSeek** → читайте [DEEPSEEK_SETUP.md](./DEEPSEEK_SETUP.md)
- 🔷 **OpenAI** → читайте [QUICK_START.md](./QUICK_START.md) (раздел про OpenAI)
- 🔴 **Anthropic** → читайте [AI_GUIDE.md](./AI_GUIDE.md)

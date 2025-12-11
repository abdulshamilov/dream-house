# ⚡ Quick Start Guide - AI Ассистент

## 🎯 Задача за 5 минут

### Шаг 1: Установить зависимости (30 сек)

```bash
pip install openai anthropic
pip install -r requirements.txt
```

### Шаг 2: Получить API ключ (1 мин)

**Вариант A: OpenAI (GPT-4)**
1. Перейти на https://platform.openai.com/api-keys
2. Создать новый ключ
3. Скопировать: `sk-...`

**Вариант B: Anthropic (Claude)**
1. Перейти на https://console.anthropic.com/
2. Создать ключ
3. Скопировать: `sk-ant-...`

**Вариант C: DeepSeek (R1) - 💜 Рекомендуется**
1. Перейти на https://platform.deepseek.com/
2. Создать ключ
3. Скопировать: `sk-...` (тот же формат как у OpenAI)

### Шаг 3: Установить переменную окружения (30 сек)

```bash
# Windows PowerShell - OpenAI
$env:OPENAI_API_KEY = "sk-your-key-here"

# или для Anthropic
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# или для DeepSeek
$env:DEEPSEEK_API_KEY = "sk-your-deepseek-key"

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

### Шаг 4: Запустить сервер

```bash
python manage.py runserver
```

### Шаг 5: Настроить в админке (1.5 мин)

1. Открыть https://api.dreamhouse05.com/admin/
2. Войти с admin/admin
3. Найти "AI Ассистент"
4. Создать новую запись:
   - **Имя:** AI Помощник
   - **API провайдер:** 
     - OpenAI (gpt-4)
     - Anthropic (claude-3-opus)
     - **DeepSeek (deepseek-chat или deepseek-reasoner)** ⭐
   - **API ключ:** (оставить пустым - будет использована переменная окружения)
   - **Модель:** 
     - `gpt-4` (OpenAI)
     - `claude-3-opus` (Anthropic)
     - `deepseek-chat` или `deepseek-reasoner` (DeepSeek)
   - **Temperature:** 0.7
   - **Max tokens:** 500
   - **Активно:** ☑ (галочка)
5. Сохранить

---

## 🧪 Быстрый тест

### Через curl

```bash
# 1. Получить токен
$TOKEN = (curl -X POST https://api.dreamhouse05.com/api/token/login/ `
  -Headers @{'Content-Type'='application/json'} `
  -Body '{"phone": "+79999999999", "password": "your_password"}' | ConvertFrom-Json).access

# 2. Тестировать AI
curl -X POST https://api.dreamhouse05.com/api/cards/ai/chat/ `
  -Headers @{'Authorization'="Bearer $TOKEN"; 'Content-Type'='application/json'} `
  -Body '{"message":"Привет! Найди мне квартиру в Махачкале"}'

# 3. История
curl -X GET https://api.dreamhouse05.com/api/cards/ai/history/ `
  -Headers @{'Authorization'="Bearer $TOKEN"}
```

### Через Postman

1. **Создать новый запрос**
2. **URL:** `POST https://api.dreamhouse05.com/api/cards/ai/chat/`
3. **Headers:** 
   - `Authorization: Bearer TOKEN`
   - `Content-Type: application/json`
4. **Body (raw JSON):**
```json
{
  "message": "Найди мне квартиру в Махачкале",
  "user_preferences": {
    "city": 1,
    "rooms": 3,
    "price_max": 3500000
  }
}
```
5. **Отправить → Видишь ответ от AI ✅**

---

## 📚 Что это даёт?

| Функция | Что делает | Где использовать |
|---------|-----------|-----------------|
| **AI Чат** | Пользователь пишет - AI ищет подходящие карточки и отвечает | Основная фишка приложения |
| **История** | Сохраняет все чаты пользователя | Показать историю поиска |
| **Оценка** | Пользователь может сказать "это было полезно" | Улучшить AI со временем |
| **Скидки** | Пользователь запрашивает скидку - админ одобряет | Интерактивная торговля |
| **Рекомендации** | AI предлагает похожие карточки | Без необходимости спрашивать |

---

## 🔌 Все endpoints в одном месте

```
POST   /api/cards/ai/chat/              - Отправить сообщение AI
GET    /api/cards/ai/history/           - История чатов
PATCH  /api/cards/ai/chat/<id>/rate/    - Оценить ответ

GET    /api/cards/recommendations/      - Получить рекомендации
POST   /api/cards/<id>/discount/        - Запросить скидку
GET    /api/cards/discounts/me/         - Мои запросы на скидку
```

---

## ❓ FAQ

**Q: AI не отвечает**
A: Проверьте:
1. API ключ установлен: `echo $env:OPENAI_API_KEY`
2. AIAssistant создан в админке с is_active=True
3. Интернет работает

**Q: Как изменить температуру (творческость)?**
A: В админке → AI Ассистент → Temperature (0 = точный ответ, 1 = творческий)

**Q: Можно ли использовать Claude вместо GPT-4?**
A: Да! В админке выбрать "Anthropic" и ввести модель "claude-3-opus"

**Q: Какой лимит на сообщения?**
A: Максимум 2000 символов на сообщение. Больше - это spam.

**Q: Могу ли я видеть чаты других пользователей?**
A: Нет, каждый видит только свои. Админ видит все для модерации.

---

## 📊 Что смотреть в админке

**Discounts:**
- Какие скидки запросили пользователи
- Автоматически считается % скидки
- Одобрить/отклонить с комментарием

**AI Assistant:**
- Включить/выключить AI
- Выбрать провайдера (OpenAI/Anthropic)
- Настроить параметры

**Chat Messages:**
- История всех чатов
- Сколько токенов использовано
- Была ли полезной ответ (для улучшения)

**Recommendations:**
- Какие рекомендации система создала
- Score (0-1) релевантности
- Когда создана

---

## 🚀 Следующие шаги

1. **Frontend:** Создать UI для чата (JavaScript/React)
2. **Webhook:** Добавить Telegram бот для уведомлений о скидках
3. **Анализ:** Смотреть статистику - какие вопросы чаще задают
4. **Улучшение:** Подбирать лучший system_prompt для AI

---

## 🎓 Примеры использования

### Пример 1: Пользователь ищет квартиру

```
User: "Найди мне трёхкомнатную в Махачкале до 3 млн"

AI: "Я нашел вам 3 отличных варианта! 
     - Квартира в центре (85 кв.м, рейтинг 4.8)
     - Новостройка на окраине (90 кв.м, рейтинг 4.5)
     - Студия с хорошим видом (75 кв.м, рейтинг 4.6)
     
     Хотите увидеть подробнее?"

📌 Система автоматически привязала 3 карточки к чату
```

### Пример 2: Пользователь запрашивает скидку

```
User: Нажимает "Запросить скидку" на карточке за 3 млн

Post: /api/cards/5/discount/
Body: {
  "requested_price": 2800000,
  "message": "Готов рассмотреть эту сумму"
}

Response: {
  "discount_percent": 6.67,
  "status": "pending",
  ...
}

👨‍💼 Админ видит в панели и может одобрить
```

### Пример 3: Рекомендации

```
User имеет избранные: 
- 3-комнатная квартира в Махачкала, 3 млн
- Частный дом в Махачкала, 4.5 млн

GET /api/cards/recommendations/

Response: [
  {id: 12, score: 0.95, title: "3-комнатная в центре"},
  {id: 15, score: 0.90, title: "Дом в пригороде"},
  {id: 18, score: 0.85, title: "3-комнатная на красивой улице"}
]

✅ Система предложила похожие по типу, городу и цене
```

---

## 🔐 Безопасность

✅ **DO:**
- Используйте переменные окружения для ключей
- Ограничьте API лимиты
- Логируйте все запросы
- Валидируйте input от пользователя

❌ **DON'T:**
- Не коммитьте ключи в гит
- Не показывайте ключи в логах
- Не ограничивайте только одного провайдера

---

**Готово! Система работает. Вопросы?** 🚀

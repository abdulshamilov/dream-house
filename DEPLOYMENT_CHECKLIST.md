# ✅ ФИНАЛЬНЫЙ CHECKLIST ПРОВЕРКИ

## 🔍 Что было реализовано:

### ✅ 1. Управление профилем пользователя
- [x] Смена фото профиля (PUT `/api/users/update-profile/`)
- [x] Смена пароля (POST `/api/users/change-password/`)
- [x] Удаление аккаунта (DELETE `/api/users/delete-account/`)

### ✅ 2. Система отзывов
- [x] Модель Review с автоматическим рейтингом
- [x] Endpoints для создания, просмотра, редактирования отзывов
- [x] Сигнал для обновления рейтинга Card при создании отзыва
- [x] Админ-панель для управления отзывами

### ✅ 3. История AI сообщений
- [x] Ограничение истории на 10 последних сообщений
- [x] Интеграция истории в AI контекст
- [x] GET `/api/cards/ai/history/` endpoint
- [x] AI видит предыдущие сообщения для лучших ответов

### ✅ 4. Система рекомендаций
- [x] Алгоритм рекомендаций на основе истории просмотров
- [x] GET `/api/cards/recommendations/` endpoint
- [x] Персонализированные подборки для пользователя

### ✅ 5. Кураций карточек (list_curations)
- [x] Обновлен формат list_curations на JSON с полной информацией
- [x] Метод `Card.generate_curations()` для автогенерации
- [x] GET `/api/cards/{id}/curations/` endpoint
- [x] Поддержка персонализированных кураций по истории пользователя

---

## 📋 Структура файлов для production:

```
📁 users/
├── serializers.py (обновлен)
├── views.py (обновлен)
└── urls.py (обновлен)

📁 cards/
├── models.py (обновлен)
├── serializers.py (обновлен)
├── views.py (обновлен)
├── views_ai.py (обновлен)
├── urls.py (обновлен)
├── signals.py (обновлен)
├── admin.py (обновлен)
├── ai_service.py (обновлен)
└── migrations/
    └── 0023_alter_card_list_curations_review.py (новый)
```

---

## 🚀 Команды для deployment на production:

```bash
# 1. Копируем все обновленные файлы на сервер

# 2. Применяем миграции
python manage.py migrate

# 3. Собираем static файлы (если нужно)
python manage.py collectstatic --noinput

# 4. Перезагружаем gunicorn
sudo systemctl restart gunicorn
# или если gunicorn запущен вручную:
sudo fuser -k 8000/tcp
gunicorn config.wsgi:application --bind 0.0.0.0:8000 &
```

---

## ✅ Быстрая проверка localhost:

```bash
# 1. Запустить сервер
python manage.py runserver

# 2. Открыть Swagger UI
# Перейти на http://localhost:8000/api/schema/swagger-ui/

# 3. Протестировать endpoints:

# A. Смена пароля
POST /api/users/change-password/
Content-Type: application/json
Authorization: Bearer <token>

{
  "old_password": "current_pass",
  "new_password": "new_pass",
  "new_password_confirm": "new_pass"
}

# B. История AI чатов
GET /api/cards/ai/history/
Authorization: Bearer <token>

# C. Отзывы
GET /api/cards/1/user-reviews/
POST /api/cards/1/user-reviews/
{
  "rating": 5,
  "text": "Great apartment!"
}

# D. Кураций
GET /api/cards/1/curations/

# E. Рекомендации
GET /api/cards/recommendations/
Authorization: Bearer <token>
```

---

## 🐛 Возможные проблемы и решения:

### Ошибка: `Field 'id' expected a number but got 'xxx'`
- Проверьте что передаете правильный ID в URL

### Ошибка: `403 Forbidden`
- Проверьте что передан правильный Authorization токен
- Некоторые endpoints требуют IsAuthenticated permission

### Ошибка: `Не применяется миграция`
- Убедитесь что вы в правильной директории проекта
- Проверьте что DATABASE правильно настроена в settings.py

### Ошибка: `Review.user matches the given query doesn't exist`
- Проверьте что пользователь существует в БД
- Используйте `python manage.py createsuperuser` если нет

### Отзывы не обновляют рейтинг
- Проверьте что signal правильно зарегистрирован
- Убедитесь что Review модель импортирована в signals.py
- Перезагрузите сервер после изменения signals.py

---

## 📊 Тестирование

### Синтаксис
```bash
python -m py_compile cards/ai_service.py
python -m py_compile cards/models.py
python -m py_compile cards/views.py
python -m py_compile users/views.py
```

### Миграции
```bash
python manage.py makemigrations --dry-run  # Проверить без применения
python manage.py migrate --plan  # Показать что будет применено
python manage.py migrate  # Применить
```

### Django Shell
```bash
python manage.py shell

# Проверить модели
from cards.models import Review, Card
print(Review.objects.all())
print(Card.objects.first().list_curations)

# Проверить методы
from cards.ai_service import AIAssistantService
ai = AIAssistantService()
ai._parse_price_from_text("до 2млн")  # (None, 2000000)
ai._parse_rooms_from_text("двухкомнатная")  # 2

exit()
```

---

## ✨ Дополнительные возможности

### Можно добавить позже:
- [ ] Очистка старых сообщений (старше 30 дней)
- [ ] Кеширование рекомендаций
- [ ] Background задачи для пересчета рейтингов
- [ ] Email уведомления при новом отзыве
- [ ] GraphQL API альтернатива
- [ ] Elasticsearch для полнотекстового поиска

---

## 📞 Контакт

Если возникают проблемы:
1. Проверьте логи: `tail -f gunicorn.log`
2. Проверьте Django логи: `tail -f /var/log/django.log`
3. Проверьте PostgreSQL: `psql -U user -d database_name -c "SELECT * FROM cards_review;"`

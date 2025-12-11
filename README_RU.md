# Dream House API - Инструкция по запуску

## 🚀 Быстрый старт

### 1. Установка зависимостей

```powershell
# Активируйте виртуальное окружение (если используется)
# .\.venv\Scripts\Activate.ps1

# Установите требуемые пакеты
pip install -r requirements.txt
```

### 2. Миграции БД

```powershell
# Создать и применить миграции
python manage.py migrate
```

### 3. Запуск dev сервера

```powershell
python manage.py runserver
```

Откройте в браузере:
- API docs: http://localhost:8000/api/docs/
- Админка: http://localhost:8000/admin/
- API: http://localhost:8000/api/

---

## 📦 Что изменилось (исправления от 11.12.2025)

### ✅ Исправлена ошибка 500 при загрузке файлов в админке
- Добавлена защитная обработка импорта `channels`
- Установлены пакеты `channels` и `channels-redis`

### ✅ Удалены дублирующиеся модели и импорты
- Удалена дублирующаяся `CardQuestion` в models.py
- Удалены дублирующиеся импорты в serializers.py

### ✅ Улучшен поиск
- Поиск теперь работает по title, description, address
- Добавлен фильтр с методом `filter_search()`

### ✅ Добавлены индексы БД для оптимизации
- Индексы на: title, city, house_type, price, created_at
- Композитный индекс на (city, house_type)

### ✅ Зарегистрированы сигналы приложения
- Добавлен метод `ready()` в `CardsConfig`

---

## 🔑 Переменные окружения

Создайте файл `.env` в корне проекта (опционально):

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False  # Установить False для production!
```

---

## 📚 API Endpoints

### Карточки
- `GET /api/cards/` — список всех карточек
- `GET /api/cards/?title=...&city=...` — фильтрация
- `GET /api/cards/<id>/` — детали карточки
- `POST /api/cards/filter/` — фильтрация через JSON

### Поиск
- `GET /api/cards/search/?q=название` — полнотекстовый поиск

### Избранное
- `POST /api/cards/<id>/favorite/` — добавить в избранное
- `DELETE /api/cards/<id>/favorite/` — убрать из избранного
- `GET /api/cards/favorites/me/` — мои избранные

### Оценки
- `POST /api/cards/<id>/rate/` — поставить оценку (1-5)

### Вопросы
- `POST /api/cards/<id>/questions/add/` — задать вопрос
- `GET /api/cards/questions/` — все вопросы
- `PATCH /api/cards/questions/<id>/answer/` — ответить на вопрос (админ)

### Отзывы
- `POST /api/cards/<id>/reviews/add/` — оставить отзыв

### Заявка на звонок
- `POST /api/cards/<id>/call_request/` — создать заявку

---

## 🗂️ Структура проекта

```
dream_house/
├── config/           # Конфиги Django
│   ├── settings.py   # Основные настройки
│   ├── urls.py       # URL routes
│   └── wsgi.py       # WSGI приложение
├── cards/            # Приложение карточек недвижимости
│   ├── models.py     # Модели (Card, CardImage, CardVideo и т.д.)
│   ├── views.py      # API views
│   ├── serializers.py# DRF сериализаторы
│   ├── filters.py    # Фильтры поиска
│   ├── signals.py    # Django сигналы
│   └── urls.py       # API routes
├── users/            # Приложение пользователей
├── developers/       # Приложение застройщиков
├── notifications/    # Приложение уведомлений
├── media/            # Медиафайлы (загружаемые)
├── static/           # Статические файлы (CSS, JS, images)
├── db.sqlite3        # База данных (SQLite)
└── requirements.txt  # Python зависимости
```

---

## 🐛 Решение типичных проблем

### Ошибка: `ModuleNotFoundError: No module named 'channels'`
```powershell
pip install channels channels-redis
```

### Ошибка при миграциях
```powershell
python manage.py migrate --fake-initial
```

### Статические файлы не загружаются
```powershell
python manage.py collectstatic
```

### Очистить БД и начать заново
```powershell
Remove-Item db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 👨‍💻 Для разработчиков

### Создание новой миграции
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Запуск тестов
```powershell
python manage.py test
```

### Доступ к Django shell
```powershell
python manage.py shell
```

### Создание суперпользователя
```powershell
python manage.py createsuperuser
```

---

## ⚙️ Production чеклист

Перед развёртыванием на production:

- [ ] Установить `DEBUG=False` в settings.py
- [ ] Установить сильный `SECRET_KEY`
- [ ] Настроить ALLOWED_HOSTS
- [ ] Использовать PostgreSQL вместо SQLite
- [ ] Настроить HTTPS
- [ ] Включить security middleware
- [ ] Настроить CORS правильно (не `CORS_ALLOW_ALL_ORIGINS`)
- [ ] Настроить логирование (Sentry или аналог)
- [ ] Использовать Gunicorn/uWSGI вместо runserver
- [ ] Настроить reverse proxy (Nginx)
- [ ] Включить кеширование (Redis)

---

## 📞 Поддержка

Для вопросов и проблем смотри файл `FIXES_SUMMARY.md` с подробным описанием всех изменений.

---

**Последнее обновление:** 11 декабря 2025

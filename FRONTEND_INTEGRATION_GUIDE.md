# Инструкция по интеграции для фронтенда - Управление профилем

## Обзор

Бэк был обновлен с улучшенной функциональностью для управления профилем пользователя:
1. ✅ Смена фото профиля
2. ✅ Удаление фото профиля  
3. ✅ Удаление аккаунта

## API Endpoints

### 1. Смена фото и имени
```
PUT /api/users/update-profile/
Content-Type: multipart/form-data

Параметры:
- profile_photo (file, optional) - Новое фото (JPEG, PNG, GIF, max 5MB)
- name (string, optional) - Новое имя (max 50 chars)

Ответ (200 OK):
{
  "id": 1,
  "phone_number": "+79999999999",
  "name": "John Doe",
  "profile_photo": "http://..."
}
```

### 2. Удаление фото
```
DELETE /api/users/update-profile/

Ответ (200 OK):
{
  "detail": "Photo deleted successfully"
}
```

### 3. Удаление аккаунта
```
DELETE /api/users/delete-account/
Content-Type: application/json

Body:
{
  "password": "user_password"
}

Ответ (204 No Content)
```

## Примеры кода для фронтенда

### React - Смена фото

```jsx
import React, { useState } from 'react';

function UpdateProfilePhoto() {
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('access_token');

  const handlePhotoChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Проверка размера (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Размер фото не должен превышать 5MB');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('profile_photo', file);

    try {
      const response = await fetch('/api/users/update-profile/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Фото обновлено:', data.profile_photo);
        // Обновить UI с новым фото
      } else {
        const error = await response.json();
        alert('Ошибка: ' + error.detail);
      }
    } catch (err) {
      alert('Ошибка загрузки: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        accept="image/*"
        onChange={handlePhotoChange}
        disabled={loading}
      />
      {loading && <p>Загрузка...</p>}
    </div>
  );
}
```

### React - Удаление фото

```jsx
function DeleteProfilePhoto() {
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('access_token');

  const handleDeletePhoto = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить фото профиля?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/users/update-profile/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        console.log('Фото удалено');
        // Обновить UI
      } else {
        alert('Ошибка удаления фото');
      }
    } catch (err) {
      alert('Ошибка: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleDeletePhoto} disabled={loading}>
      {loading ? 'Удаление...' : 'Удалить фото'}
    </button>
  );
}
```

### React - Удаление аккаунта

```jsx
function DeleteAccount() {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('access_token');

  const handleDeleteAccount = async () => {
    if (!password) {
      alert('Введите пароль для подтверждения');
      return;
    }

    if (!window.confirm('⚠️ ВНИМАНИЕ! Эта операция необратима. Вы удалите свой аккаунт и ВСЕ данные. Вы уверены?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/users/delete-account/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
      });

      if (response.status === 204 || response.ok) {
        // Удалить токены и перенаправить на начальную страницу
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
      } else if (response.status === 400) {
        const error = await response.json();
        alert('Неверный пароль');
      }
    } catch (err) {
      alert('Ошибка: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Введите пароль"
      />
      <button onClick={handleDeleteAccount} disabled={loading}>
        {loading ? 'Удаление...' : 'Удалить аккаунт'}
      </button>
    </div>
  );
}
```

### Vue.js - Смена фото

```vue
<template>
  <div>
    <input 
      type="file" 
      accept="image/*"
      @change="handlePhotoChange"
      :disabled="loading"
    />
    <p v-if="loading">Загрузка...</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: false
    };
  },
  methods: {
    async handlePhotoChange(e) {
      const file = e.target.files[0];
      if (!file) return;

      if (file.size > 5 * 1024 * 1024) {
        alert('Размер фото не должен превышать 5MB');
        return;
      }

      this.loading = true;
      const formData = new FormData();
      formData.append('profile_photo', file);

      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/users/update-profile/', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Фото обновлено:', data);
          this.$emit('photo-updated', data);
        }
      } catch (err) {
        alert('Ошибка: ' + err.message);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## Обработка ошибок

### Типичные ошибки и решения

1. **400 Bad Request - Файл слишком большой**
   - Решение: Проверьте размер файла на клиенте перед отправкой

2. **400 Bad Request - Неподдерживаемый формат**
   - Решение: Используйте только JPEG, PNG, GIF
   - Валидация на клиенте: `accept="image/jpeg,image/png,image/gif"`

3. **401 Unauthorized**
   - Решение: Проверьте наличие JWT токена
   - Обновите токен если истек refresh token

4. **400 Bad Request при удалении аккаунта - Неверный пароль**
   - Решение: Попросите пользователя ввести пароль еще раз

## UI/UX Рекомендации

### Смена фото
```
┌─────────────────────────────────┐
│ Фото профиля                    │
├─────────────────────────────────┤
│                                 │
│      [Текущее фото]             │
│                                 │
├─────────────────────────────────┤
│ [Выбрать новое фото] [Удалить]  │
└─────────────────────────────────┘
```

### Удаление аккаунта
```
⚠️ ОПАСНАЯ ЗОНА
┌─────────────────────────────────┐
│ Удалить аккаунт                 │
│                                 │
│ Это действие необратимо.         │
│ Будут удалены все данные:        │
│ • Профиль                        │
│ • Квартиры                       │
│ • Отзывы                         │
│ • Чаты и сообщения              │
│                                 │
│ Пароль: [___________]           │
│                                 │
│      [Отмена] [Удалить]         │
└─────────────────────────────────┘
```

## Тестовые случаи

### Test Case 1: Смена фото
1. Загрузить фото JPEG
2. Проверить что фото обновилось
3. Попытаться загрузить файл > 5MB (должна быть ошибка)
4. Попытаться загрузить видео (должна быть ошибка)

### Test Case 2: Удаление фото
1. Загрузить фото
2. Нажать "Удалить фото"
3. Проверить что фото удалено
4. В GET /api/users/me/ profile_photo должно быть null

### Test Case 3: Удаление аккаунта
1. Попытаться удалить с неверным паролем (должна быть ошибка)
2. Удалить с правильным паролем
3. Проверить что пользователь выведен из системы
4. Попытаться использовать старый токен (должна быть ошибка 401)

## Checklist для интеграции

- [ ] Реализовать UI для смены фото
- [ ] Добавить валидацию размера и типа файла на клиенте
- [ ] Реализовать UI для удаления фото
- [ ] Добавить подтверждение перед удалением фото
- [ ] Реализовать UI для удаления аккаунта
- [ ] Добавить яркое предупреждение об необратимости
- [ ] Добавить обработку ошибок для всех случаев
- [ ] Протестировать на различных устройствах
- [ ] Добавить loading состояния
- [ ] Документировать для пользователей

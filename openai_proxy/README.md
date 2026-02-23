# Universal API Proxy + VPN на голландском сервере

Максимум пользы за 400₽/мес:
- ✅ Прокси OpenAI API (обход блокировки)
- ✅ Прокси Anthropic API (Claude тоже заблокирован)
- ✅ Кеширование ответов (экономия на повторных запросах)
- ✅ VPN для себя (WireGuard)

## Быстрый старт

### 1. Скопируйте папку `openai_proxy` на голландский сервер

```bash
scp -r openai_proxy/ user@your-netherlands-server:/opt/openai_proxy/
```

### 2. На голландском сервере

```bash
cd /opt/openai_proxy

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Скопируйте и настройте .env
cp .env.example .env
nano .env  # Укажите API ключи
```

### 3. Запуск через systemd

Создайте файл `/etc/systemd/system/api-proxy.service`:

```ini
[Unit]
Description=Universal API Proxy
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/openai_proxy
Environment="PATH=/opt/openai_proxy/venv/bin"
EnvironmentFile=/opt/openai_proxy/.env
ExecStart=/opt/openai_proxy/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8080 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable api-proxy
sudo systemctl start api-proxy
```

### 4. Настройка nginx (HTTPS)

```nginx
server {
    listen 443 ssl;
    server_name proxy.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 120s;
    }
}
```

---

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /health` | Проверка статуса |
| `GET /stats` | Статистика (нужна авторизация) |
| `POST /v1/*` | Прокси к OpenAI |
| `POST /anthropic/*` | Прокси к Anthropic |
| `POST /cache/clear` | Очистить кеш |

---

## Настройка основного сервера (Россия)

В `.env` добавьте:

```bash
OPENAI_PROXY_URL=https://your-proxy-server.com
OPENAI_PROXY_SECRET=ваш-секретный-ключ
```

---

## Бонус: VPN за 5 минут

WireGuard для личного использования:

```bash
sudo bash setup_wireguard.sh
```

Скрипт автоматически:
- Установит WireGuard
- Сгенерирует ключи
- Покажет QR-код для телефона

---

## Кеширование

Повторные идентичные запросы к GPT возвращаются из кеша (экономия денег!).

- `CACHE_ENABLED=true` — включить (по умолчанию)
- `CACHE_TTL=3600` — время жизни кеша в секундах

---

## Безопасность

1. **PROXY_SECRET_KEY** — длинный случайный ключ: `openssl rand -hex 32`
2. **Firewall** — разрешите доступ только с IP основного сервера
3. **HTTPS** — обязательно используйте SSL

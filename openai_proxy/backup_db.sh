#!/bin/bash
# Скрипт для автоматического бэкапа базы данных с основного сервера
# Запускать на голландском сервере через cron

# Настройки
MAIN_SERVER="user@your-main-server.com"
REMOTE_DB_PATH="/path/to/dream_house/db.sqlite3"
LOCAL_BACKUP_DIR="/opt/backups/dream_house"
KEEP_DAYS=7

# Создаём директорию если нет
mkdir -p "$LOCAL_BACKUP_DIR"

# Имя файла с датой
BACKUP_FILE="$LOCAL_BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sqlite3"

# Скачиваем базу
echo "Downloading database backup..."
scp "$MAIN_SERVER:$REMOTE_DB_PATH" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Сжимаем
    gzip "$BACKUP_FILE"
    echo "Backup saved: ${BACKUP_FILE}.gz"
    
    # Удаляем старые бэкапы
    find "$LOCAL_BACKUP_DIR" -name "*.gz" -mtime +$KEEP_DAYS -delete
    echo "Old backups cleaned up (older than $KEEP_DAYS days)"
else
    echo "Backup failed!"
    exit 1
fi

# Добавить в cron (ежедневно в 3:00):
# crontab -e
# 0 3 * * * /opt/openai_proxy/backup_db.sh >> /var/log/backup.log 2>&1

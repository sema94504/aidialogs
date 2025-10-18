# Развёртывание на удалённом сервере

Полная инструкция для развёртывания системы на производственном сервере.

## Предварительные требования

На сервере должны быть установлены:
- Docker (20.10+)
- Docker Compose (2.0+)
- Git
- curl (для healthchecks)

Проверка:
```bash
docker --version
docker-compose --version
```

## Пошаговое развёртывание

### 1. Подключитесь к серверу

```bash
ssh user@your-server.com
cd /opt  # или другая директория для приложений
```

### 2. Клонируйте репозиторий

```bash
git clone https://github.com/sema94504/aidialogs.git
cd aidialogs
```

### 3. Создайте .env файл

```bash
cp .env.example .env
nano .env  # или vi .env
```

**Заполните обязательные переменные:**

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=ваш_реальный_токен

# LLM Configuration
LLM_BASE_URL=http://ваш-llm-сервер:3000/v1
LLM_MODEL=gemma3:4b
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt

# API Configuration
API_URL=https://api.yourdomain.com  # публичный URL вашего API
API_WORKERS=8

# Frontend
NODE_ENV=production

# Logging
LOG_LEVEL=warning
```

### 4. Запустите систему

```bash
# Production версия с оптимизациями
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Проверьте статус
docker-compose ps

# Просмотрите логи
docker-compose logs -f
```

### 5. Проверьте доступность

```bash
# API healthcheck
curl http://localhost:8063/health

# Frontend
curl http://localhost:3063/

# Логи отдельного сервиса
docker-compose logs api
docker-compose logs bot
docker-compose logs frontend
```

## Управление данными

### Где хранятся данные?

```bash
# Узнать расположение volumes
docker volume inspect aidialogs_db_volume

# Обычно по пути:
/var/lib/docker/volumes/aidialogs_db_volume/_data/
```

### Резервная копия БД

```bash
# Создать backup
docker run --rm -v aidialogs_db_volume:/data -v $(pwd):/backup \
  alpine cp /data/app.db /backup/backup-$(date +%Y%m%d-%H%M%S).db

# Проверить backup
ls -lh backup-*.db
```

### Восстановление из backup

```bash
# Остановить сервисы
docker-compose down

# Восстановить БД
docker run --rm -v aidialogs_db_volume:/data -v $(pwd):/backup \
  alpine cp /backup/backup-YYYYMMDD-HHMMSS.db /data/app.db

# Запустить
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Обновление системы

```bash
# Получить последние изменения
git pull origin main

# Перезагрузить образы
docker-compose pull

# Перезапустить контейнеры
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Мониторинг

### Проверка статуса

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f --tail=50
```

### Healthchecks

Система автоматически проверяет здоровье сервисов:

```bash
# API healthcheck
curl -s http://localhost:8063/health | jq .

# Посмотреть статус healthcheck в Docker
docker-compose ps
# STATUS column должна показывать "healthy"
```

### Ошибки и troubleshooting

```bash
# Если контейнер не запускается
docker-compose logs <service_name>

# Перезапустить сервис
docker-compose restart <service_name>

# Пересобрать без кэша
docker-compose pull --no-parallel
docker-compose up -d

# Полная очистка (ВНИМАНИЕ: удалит данные!)
docker-compose down -v
```

## Интеграция с reverse proxy (nginx)

Если используете nginx спереди, добавьте в конфиг:

```nginx
upstream api {
    server localhost:8063;
}

upstream frontend {
    server localhost:3063;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Настройка автозагрузки

Добавьте в crontab для автозагрузки при перезагрузке сервера:

```bash
crontab -e

# Добавьте строку:
@reboot cd /opt/aidialogs && docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Логирование и метрики

Логи автоматически ротируются:
- Максимальный размер одного файла: 50MB
- Максимум файлов: 5
- Находятся в: `/var/lib/docker/containers/...`

Для более продвинутого мониторинга можно использовать:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Prometheus + Grafana
- New Relic / Datadog

## Безопасность

### Важно:

1. **Защитите .env файл**
   ```bash
   chmod 600 .env
   ```

2. **Используйте firewall**
   ```bash
   # Разрешить только нужные порты
   sudo ufw allow 22/tcp      # SSH
   sudo ufw allow 80/tcp      # HTTP (для Let's Encrypt)
   sudo ufw allow 443/tcp     # HTTPS
   sudo ufw enable
   ```

3. **Настройте SSL сертификаты**
   - Используйте Let's Encrypt с certbot
   - Или corporate certificate

4. **Регулярные резервные копии**
   ```bash
   # Добавить в crontab
   0 2 * * * cd /opt/aidialogs && docker run --rm -v aidialogs_db_volume:/data -v /backups:/backup \
     alpine cp /data/app.db /backup/backup-$(date +\%Y\%m\%d).db
   ```

## Контакты и поддержка

Если возникли проблемы:
- Проверьте логи: `docker-compose logs`
- Прочитайте DOCKER.md
- Посмотрите DOCKER-COMPOSE-REFERENCE.md

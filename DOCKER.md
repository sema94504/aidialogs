# Docker Compose Setup

## Структура

- **docker-compose.yml** — основная конфигурация с pre-built образами из GHCR
- **docker-compose.prod.yml** — production overrides (более строгие лимиты, лучшее логирование)
- **docker-compose.dev.yml** — локальная разработка (сборка из Dockerfile, volume binds)
- **.env.example** — пример переменных окружения

## Структура сервисов

### sqlite
Volume для SQLite БД (монтируется в bot и api)

### bot
- Образ: ghcr.io/sema94504/bot:latest
- Зависит от: sqlite
- Лимиты: 256M RAM, 0.5 CPU (dev), 384M/0.75 CPU (prod)
- Переменные: TELEGRAM_BOT_TOKEN, LLM_BASE_URL, LLM_MODEL, SYSTEM_PROMPT_FILE, LOG_LEVEL

### api
- Образ: ghcr.io/sema94504/api:latest
- Зависит от: sqlite
- Порт: 8063:8000
- Healthcheck: /health (30s interval в dev, 15s в prod)
- Лимиты: 512M RAM, 1 CPU (dev), 768M/1.5 CPU (prod)

### frontend
- Образ: ghcr.io/sema94504/frontend:latest
- Зависит от: api
- Порт: 3063:3000
- Healthcheck: / (30s interval в dev, 15s в prod)
- Лимиты: 256M RAM, 0.5 CPU (dev), 384M/0.75 CPU (prod)

## Использование

### Production (с pre-built образами)

```bash
cp .env.example .env
# Отредактировать .env с реальными значениями
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Локальная разработка (с сборкой из Dockerfile)

```bash
cp .env.example .env
docker-compose -f docker-compose.dev.yml up -d
```

## Network и Volumes

- **Network**: aidialogs_network (bridge)
- **Volumes**: 
  - db_volume (для SQLite)
  - logs_volume (для логов)

## Logging

Все сервисы используют json-file driver с ротацией:
- Production: max-size 50m, max-file 5
- Development: max-size 1m, max-file 1

## Healthchecks

API и Frontend имеют healthchecks:

**Development:**
- Interval: 30s
- Timeout: 10s
- Retries: 3
- Start period: 10-15s

**Production:**
- Interval: 15s
- Timeout: 5s
- Retries: 5
- Start period: 30s

## Restart Policy

- Production: always
- Development: unless-stopped

## Отладка

```bash
# Логи сервиса
docker-compose logs -f <service>

# Статус контейнеров
docker-compose ps

# Выполнить команду в контейнере
docker-compose exec <service> <command>

# Остановить
docker-compose down

# Полная очистка (удаляет контейнеры и volumes)
docker-compose down -v
```

## Директории монтирования

Убедитесь, что созданы необходимые директории (для production):

```bash
sudo mkdir -p /var/lib/aidialogs/data
sudo mkdir -p /var/log/aidialogs
sudo chown -R $(id -u):$(id -g) /var/lib/aidialogs /var/log/aidialogs
```


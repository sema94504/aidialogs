# Docker Compose Reference

Полная справка по файлам и конфигурации Docker Compose.

## Файлы конфигурации

### docker-compose.yml
Основная конфигурация с 4 сервисами:

- **sqlite** - volume container для SQLite БД
- **bot** - Telegram bot (ghcr.io/sema94504/bot:latest)
- **api** - REST API (ghcr.io/sema94504/api:latest, порт 8063:8000)
- **frontend** - Web UI (ghcr.io/sema94504/frontend:latest, порт 3063:3000)

**Resource limits (development):**
- Bot: 256M RAM, 0.5 CPU
- API: 512M RAM, 1 CPU  
- Frontend: 256M RAM, 0.5 CPU

**Features:**
- Healthchecks для API и Frontend (30s interval)
- Dedicated network (aidialogs_network)
- Named volumes (db_volume, logs_volume)
- JSON file logging с rotation (10m size, 3 files max)

### docker-compose.prod.yml
Production overrides для mejor производительности и надёжности:

- Restart policy: always (вместо unless-stopped)
- Более строгие resource limits:
  - Bot: 384M, 0.75 CPU
  - API: 768M, 1.5 CPU
  - Frontend: 384M, 0.75 CPU
- Более частые healthchecks (15s interval вместо 30s)
- Большая ротация логов (50m size, 5 files max)
- Bind mount volumes в /var/lib/aidialogs и /var/log/aidialogs

**Использование:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### docker-compose.dev.yml
Для локальной разработки:

- Сборка образов из Dockerfile вместо pre-built
- Volume binds для hot-reload:
  - ./bot:/app (Bot)
  - ./api:/app (API)
  - ./frontend:/app (Frontend)
- PYTHONUNBUFFERED=1 для прямого вывода логов
- Отключены healthchecks
- Маленькие лимиты логирования

**Использование:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

## Environment files

### .env.example
Пример переменных окружения для разработки. Скопируйте как .env:
```bash
cp .env.example .env
```

### .env.prod
Шаблон для production (переименуйте в .env перед production deploy)

## Networks

- **aidialogs_network** - bridge network для всех сервисов
  - Позволяет сервисам общаться между собой по имени
  - Изолирует от других контейнеров

## Volumes

- **db_volume** - SQLite БД
  - Монтируется в /data для bot и api
  - Production: bind mount в /var/lib/aidialogs/data

- **logs_volume** - Логи сервисов
  - /var/log/bot (bot logs)
  - /var/log/api (api logs)
  - Production: bind mount в /var/log/aidialogs

## Порты

- **3063:3000** - Frontend (host:container)
- **8063:8000** - API (host:container)

Изменить порты можно в docker-compose.yml

## Environment variables

### Bot сервис
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (REQUIRED)
- `LLM_BASE_URL` - LLM API base URL (REQUIRED)
- `LLM_MODEL` - LLM model name (REQUIRED)
- `SYSTEM_PROMPT_FILE` - Путь к system prompt (REQUIRED)
- `LOG_LEVEL` - Logging level (default: info)

### API сервис
- `LOG_LEVEL` - Logging level (default: info)
- `API_WORKERS` - Worker processes (default: 4)

### Frontend сервис
- `API_URL` - Backend API URL (default: http://localhost:8063)
- `NODE_ENV` - Environment (default: production)

## Healthchecks

### API (/health)
- **Development:** 30s interval, 10s timeout, 3 retries, 10s start_period
- **Production:** 15s interval, 5s timeout, 5 retries, 30s start_period

### Frontend (/)
- **Development:** 30s interval, 10s timeout, 3 retries, 15s start_period
- **Production:** 15s interval, 5s timeout, 5 retries, 30s start_period

## Logging

Все сервисы используют json-file логирования:

**Development:**
- max-size: 10m
- max-file: 3

**Production:**
- max-size: 50m
- max-file: 5
- labels: service=<name>

Просмотр логов:
```bash
docker-compose logs -f <service>
docker-compose logs --tail 100 api
```

## Команды управления

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Полная очистка (удаляет volumes)
docker-compose down -v

# Проверка статуса
docker-compose ps

# Перезапуск сервиса
docker-compose restart <service>

# Выполнение команды в контейнере
docker-compose exec <service> <command>

# Просмотр логов
docker-compose logs -f <service>

# Сборка образов (для dev)
docker-compose build
```

## Зависимости между сервисами

```
sqlite
  ↓
bot (depends_on sqlite)

sqlite
  ↓
api (depends_on sqlite)
  ↓
frontend (depends_on api)
```

- Bot и API ждут SQLite перед запуском
- Frontend ждёт API перед запуском

## Troubleshooting

### Контейнер перезагружается

```bash
# Проверьте логи
docker-compose logs <service>

# Проверьте resource limits
docker stats
```

### Healthcheck не работает

```bash
# Проверьте, что URL доступен
docker-compose exec api curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000/
```

### Нет доступа между контейнерами

```bash
# Проверьте network
docker network ls
docker network inspect aidialogs_aidialogs_network

# Протестируйте ping между сервисами
docker-compose exec api ping bot
```

### Медленная работа на слабом CPU

Увеличьте cpu reservation в docker-compose.yml или используйте более мощный хост.

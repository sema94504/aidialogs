# Docker Quick Start

## Быстрый старт

### 1. Подготовка

Скопируйте шаблон конфигурации и настройте переменные окружения:

```bash
cp env.docker.template .env.docker
```

Отредактируйте `.env.docker`:
- Укажите реальный `TELEGRAM_BOT_TOKEN`
- При необходимости измените `LLM_BASE_URL` (по умолчанию: `http://host.docker.internal:3000/v1`)

### 2. Запуск

```bash
# Сборка образов
make docker-build

# Запуск всех сервисов
make docker-up

# Проверка статуса
make docker-status
```

### 3. Доступные сервисы

После запуска доступны:

- **Frontend**: http://localhost:3000 - веб-интерфейс
- **API**: http://localhost:8000 - REST API
- **API Docs**: http://localhost:8000/docs - документация API
- **Health Check**: http://localhost:8000/health - проверка работоспособности

### 4. Просмотр логов

```bash
# Все сервисы
make docker-logs

# Отдельные сервисы
make docker-logs-bot
make docker-logs-api
make docker-logs-frontend
```

### 5. Управление

```bash
# Остановка
make docker-down

# Перезапуск
make docker-down && make docker-up

# Пересборка после изменений
make docker-build
make docker-up

# Полная очистка (удаляет контейнеры и volumes)
make docker-clean
```

## Архитектура

```
Frontend (3000) → API (8000) → Bot → SQLite DB (./data/)
```

- **Bot** и **API** используют общий volume `./data/` для доступа к SQLite БД
- **Frontend** подключается к API через прокси Next.js
- Все сервисы в одной сети `aidialogs-network`

## База данных

SQLite БД (`aidialogs.db`) хранится в `./data/` на хосте.

**Важно**: Перед первым запуском выполните миграции Alembic:

```bash
# Если БД еще не создана
uv run alembic upgrade head
```

Или создайте пустую БД вручную и запустите контейнеры - bot выполнит миграции автоматически.

## Устранение проблем

### Контейнеры не запускаются

```bash
# Проверьте логи
make docker-logs

# Проверьте, что порты 3000 и 8000 свободны
netstat -tuln | grep -E ':(3000|8000)'
```

### БД не создается

```bash
# Проверьте права на директорию data
ls -la ./data/

# Убедитесь, что DATABASE_PATH в .env.docker указывает на /app/data/aidialogs.db
```

### LLM не отвечает

```bash
# Проверьте LLM_BASE_URL в .env.docker
# Для доступа к локальному сервису на хосте используйте:
LLM_BASE_URL=http://host.docker.internal:3000/v1
```

## Разработка

Для разработки с hot-reload используйте отдельные команды:

```bash
# Bot (локально)
make run

# API (локально)
make run-api

# Frontend (локально)
make frontend-dev
```

Это позволит быстрее итерироваться без пересборки Docker образов.


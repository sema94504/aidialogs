# Спринт D0: Basic Docker Setup - План реализации

**Дата:** 2025-10-18  
**Статус:** ✅ Completed

## Цель

Запустить все сервисы локально через `docker-compose up` одной командой.

## Реализованные компоненты

### 1. Docker-файлы

#### Dockerfile.bot
- Base image: `python:3.11-slim`
- Установка UV для управления зависимостями
- Копирование необходимых файлов: src/, prompts/, alembic/, pyproject.toml
- Команда запуска: `uv run python -m src.main`

#### Dockerfile.api
- Base image: `python:3.11-slim`
- Установка UV для управления зависимостями
- Копирование необходимых файлов: src/, prompts/, alembic/, pyproject.toml
- Команда запуска: `uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
- Открытый порт: 8000

#### Dockerfile.frontend
- Base image: `node:23-slim`
- Установка pnpm
- Копирование frontend/package.json и frontend/pnpm-lock.yaml
- Установка зависимостей: `pnpm install --frozen-lockfile`
- Сборка приложения: `pnpm build`
- Команда запуска: `pnpm start`
- Открытый порт: 3000

### 2. Docker Compose

Файл `docker-compose.yml` содержит 3 сервиса:

- **bot**: Telegram бот с SQLite БД
  - Volumes: ./data:/app/data (для хранения aidialogs.db)
  - Restart policy: unless-stopped
  
- **api**: FastAPI сервер
  - Порт: 8000
  - Volumes: ./data:/app/data (shared с bot)
  - Depends on: bot
  - Restart policy: unless-stopped
  
- **frontend**: Next.js приложение
  - Порт: 3000
  - Depends on: api
  - Restart policy: unless-stopped

Все сервисы подключены к сети `aidialogs-network`.

### 3. Конфигурация

**env.docker.template** - шаблон переменных окружения:
- TELEGRAM_BOT_TOKEN
- LLM_BASE_URL (с использованием host.docker.internal)
- LLM_MODEL
- SYSTEM_PROMPT_FILE
- DATABASE_PATH=/app/data/aidialogs.db
- USE_MOCK_STATS=true

**.dockerignore** - исключает из сборки:
- node_modules/, __pycache__/
- .pytest_cache/, htmlcov/
- *.db, .env*
- .git/, .cursor/
- Документацию и тесты

### 4. Makefile команды

Добавлены новые команды для управления Docker:

```bash
make docker-up           # Запуск всех сервисов
make docker-down         # Остановка всех сервисов
make docker-logs         # Просмотр логов всех сервисов
make docker-logs-bot     # Просмотр логов bot
make docker-logs-api     # Просмотр логов api
make docker-logs-frontend # Просмотр логов frontend
make docker-status       # Статус сервисов
make docker-build        # Сборка образов
make docker-clean        # Полная очистка (down -v)
```

### 5. Документация

README.md обновлен с разделом "Docker (рекомендуется)":
- Инструкция по первому запуску
- Список доступных сервисов и их URL
- Команды управления

## Архитектура

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   Port: 3000    │
└────────┬────────┘
         │
         │ depends_on
         ▼
┌─────────────────┐
│      API        │
│   (FastAPI)     │
│   Port: 8000    │
└────────┬────────┘
         │
         │ depends_on + shared volume
         ▼
┌─────────────────┐      ┌──────────────┐
│      Bot        │◄────►│   SQLite DB  │
│   (aiogram)     │      │ ./data/      │
└─────────────────┘      └──────────────┘
```

## База данных

SQLite (aidialogs.db) хранится в `./data/` и монтируется как volume в контейнеры bot и api.

## Проверка работоспособности

```bash
# Сборка образов
make docker-build

# Запуск сервисов
make docker-up

# Проверка статуса
make docker-status

# Проверка логов
make docker-logs
```

Доступные URL:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## MVP подход

Реализация следует принципу MVP:
- ✅ Без multi-stage builds
- ✅ Простые Dockerfile (~20 строк)
- ✅ Slim образы для минимального размера
- ✅ Фокус на работоспособности, не на оптимизации
- ✅ Одна команда для запуска: `make docker-up`

## Следующие шаги

Спринт **D1: Build & Publish** - автоматическая сборка и публикация образов в GitHub Container Registry через GitHub Actions.


<!-- e3f8f22c-3801-4239-9517-730c8f837d67 e2cf9b14-8388-4210-9490-380c4b574eea -->
# Спринт D0: Basic Docker Setup - План реализации

## Цель

Запустить все сервисы локально через `docker-compose up` одной командой.

## Сервисы (3 шт)

1. **Bot** - Python 3.11 + UV (Telegram бот) + SQLite
2. **API** - Python 3.11 + UV (FastAPI, порт 8000) + SQLite
3. **Frontend** - Next.js 15 (порт 3000)

**База данных:** SQLite (aidialogs.db) - монтируется как volume в bot и api контейнеры

## Стратегия (MVP)

### Простота и скорость:

- Без multi-stage builds
- Минимальные Dockerfile (~20 строк каждый)
- Используем slim образы для Python/Node
- Фокус на работоспособности, не на оптимизации
- Все конфиги в одном docker-compose.yml

### Структура файлов

```
/root/work/aidialogs/
├── Dockerfile.bot
├── Dockerfile.api
├── Dockerfile.frontend
├── docker-compose.yml
├── .dockerignore
├── Makefile (обновить)
└── README.md (обновить)
```

## Этапы реализации

### 1. Создать `.dockerignore` (универсальный)

Один `.dockerignore` в корне проекта для исключения общих файлов:

- node_modules/
- **pycache**/
- .pytest_cache/
- .git/
- .env (не копируем в образ)
- *.db (базы данных)
- htmlcov/, .coverage (тесты)
- .cursor/

### 2. Dockerfile.bot

Требования:

- Base image: `python:3.11-slim`
- WORKDIR: /app
- Копирование только необходимых файлов (src/, pyproject.toml, uv.lock, prompts/, alembic/)
- Установка UV и зависимостей
- CMD: `uv run python -m src.main`
- Переменные окружения для БД и LLM будут из docker-compose.yml

### 3. Dockerfile.api

Требования:

- Base image: `python:3.11-slim`
- WORKDIR: /app
- CMD: `uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
- EXPOSE 8000
- Те же зависимости что и Bot

### 4. Dockerfile.frontend

Требования:

- Base image: `node:23-slim` (для Next.js)
- WORKDIR: /app
- Копирование frontend/* в /app
- Установка pnpm
- `pnpm install`
- `pnpm build` при создании образа
- CMD: `pnpm start`
- EXPOSE 3000
- ENV NEXT_PUBLIC_API_URL=http://localhost:8000

### 5. docker-compose.yml

Сервисы (3 шт):

- **bot**: 
  - build: context: . / dockerfile: Dockerfile.bot
  - environment: все из .env
  - volumes: ./data:/app/data (для aidialogs.db)
  - restart: unless-stopped

- **api**: 
  - build: context: . / dockerfile: Dockerfile.api
  - PORT: 8000
  - depends_on: [bot]
  - environment: все из .env
  - volumes: ./data:/app/data (shared SQLite БД с bot)
  - restart: unless-stopped

- **frontend**: 
  - build: context: . / dockerfile: Dockerfile.frontend
  - PORT: 3000
  - depends_on: [api]
  - environment: NEXT_PUBLIC_API_URL=http://localhost:8000
  - restart: unless-stopped

**Важно:** SQLite БД монтируется в ./data/aidialogs.db и шарится между bot и api контейнерами.

### 6. .env файл (создать шаблон .env.docker для dev)

Переменные для docker-compose:

```
TELEGRAM_BOT_TOKEN=test_token_for_dev
LLM_BASE_URL=http://localhost:3000/v1
LLM_MODEL=gpt-oss:latest
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
DATABASE_PATH=/app/data/aidialogs.db
USE_MOCK_STATS=true
```

### 7. Обновить Makefile

Добавить docker команды:

```
make docker-up          # docker-compose up -d
make docker-down        # docker-compose down
make docker-logs        # docker-compose logs -f
make docker-logs-bot    # docker-compose logs -f bot
make docker-logs-api    # docker-compose logs -f api
make docker-logs-frontend # docker-compose logs -f frontend
make docker-status      # docker-compose ps
make docker-build       # docker-compose build
make docker-clean       # docker-compose down -v (удалить volumes)
```

### 8. Обновить README.md

Добавить новый раздел "Docker локальный запуск":

- Требования: Docker + Docker Compose
- Команда: `make docker-up`
- Доступные сервисы и URL:
  - Frontend: http://localhost:3000
  - API: http://localhost:8000
  - API docs: http://localhost:8000/docs
- Остановка: `make docker-down`
- Просмотр логов: `make docker-logs`
- Очистка: `make docker-clean`

## Ожидаемые файлы

1. ✓ `/root/work/aidialogs/Dockerfile.bot`
2. ✓ `/root/work/aidialogs/Dockerfile.api`
3. ✓ `/root/work/aidialogs/Dockerfile.frontend`
4. ✓ `/root/work/aidialogs/.dockerignore`
5. ✓ `/root/work/aidialogs/docker-compose.yml`
6. ✓ `/root/work/aidialogs/.env.docker` (шаблон)
7. ✓ `/root/work/aidialogs/Makefile` (обновленный)
8. ✓ `/root/work/aidialogs/README.md` (обновленный)

## Проверка работоспособности (финальный тест)

После создания всех файлов:

```bash
make docker-build   # Сборка образов
make docker-up      # Запуск
make docker-logs    # Проверить логи (нет критических ошибок)
make docker-status  # Все контейнеры должны быть UP
```

Затем проверить:

- Frontend доступен: http://localhost:3000
- API доступен: http://localhost:8000/health (должен вернуть {"status": "ok"})

## Заметки для реализации

- SQLite БД (aidialogs.db) монтируется как shared volume между bot и api контейнерами через ./data:/app/data
- DATABASE_PATH в .env должен быть /app/data/aidialogs.db для контейнеров
- Frontend нужно собирать в образе (pnpm build), так как next build требуется для production
- Для development можно позже добавить volumes с hot-reload
- LLM_BASE_URL может быть localhost:3000 (снаружи контейнера) или требует реального сервера
- Все контейнеры имеют `restart: unless-stopped` для автоматического перезапуска
- API зависит от bot (depends_on), чтобы БД была инициализирована
- Alembic миграции должны быть выполнены до первого запуска (в будущем автоматизируем)

### To-dos

- [ ] Создать .dockerignore с общими исключениями для всех сервисов
- [ ] Создать Dockerfile.bot с Python 3.11-slim, UV и установкой зависимостей
- [ ] Создать Dockerfile.api с FastAPI и uvicorn
- [ ] Создать Dockerfile.frontend с Node 23, pnpm и Next.js build
- [ ] Создать docker-compose.yml с 4 сервисами (postgres, api, bot, frontend)
- [ ] Создать .env.docker шаблон для docker-compose переменных окружения
- [ ] Обновить Makefile с docker командами (docker-up, docker-down, docker-logs, etc)
- [ ] Обновить README.md с разделом про Docker локальный запуск и URL сервисов
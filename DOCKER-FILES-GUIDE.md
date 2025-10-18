# Docker Files Guide

Краткое описание всех созданных Docker Compose файлов и конфигураций.

## 📁 Структура файлов

### Основные конфигурации

#### **docker-compose.yml** (2557 bytes)
Основная конфигурация с 4 сервисами для production.

**Сервисы:**
- `sqlite` - Volume container для SQLite БД
- `bot` - Telegram bot (ghcr.io/sema94504/bot:latest)
- `api` - REST API (ghcr.io/sema94504/api:latest, порт 8063:8000)
- `frontend` - Web UI (ghcr.io/sema94504/frontend:latest, порт 3063:3000)

**Включает:**
- Healthchecks для API и Frontend
- Dedicated network (aidialogs_network)
- Named volumes для persistence
- Resource limits для development
- JSON-file logging с rotation

#### **docker-compose.prod.yml** (1539 bytes)
Production overrides - применяется совместно с основным файлом.

**Включает:**
- Restart policy: always
- Оптимизированные resource limits
- Более частые healthchecks
- Усиленная ротация логов
- Bind mounts для persistence

**Использование:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### **docker-compose.dev.yml** (1112 bytes)
Конфигурация для локальной разработки.

**Особенности:**
- Сборка образов из Dockerfile
- Volume binds для hot-reload
- PYTHONUNBUFFERED=1 для логов
- Отключены healthchecks
- Минимальное логирование

**Использование:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Environment переменные

#### **.env.example** (383 bytes)
Пример переменных окружения для разработки.

**Содержит:**
- TELEGRAM_BOT_TOKEN
- LLM_BASE_URL
- LLM_MODEL
- SYSTEM_PROMPT_FILE
- DATABASE_URL
- API_WORKERS
- API_URL
- NODE_ENV
- LOG_LEVEL

**Копирование:**
```bash
cp .env.example .env
```

#### **.env.prod** (403 bytes)
Шаблон для production среды.

**Отличия от .env.example:**
- LLM_BASE_URL может быть другой
- API_WORKERS оптимизирован для production (8)
- API_URL содержит публичный домен
- LOG_LEVEL установлен в warning

### Документация

#### **DOCKER.md** (3041 bytes)
Полная документация Docker Compose.

**Содержит:**
- Описание всех сервисов
- Инструкции по использованию
- Конфигурация network и volumes
- Настройка логирования
- Healthchecks параметры
- Команды отладки

#### **QUICKSTART-PROD.md** (3008 bytes)
Быстрый старт для production.

**Содержит:**
- 5-минутный гайд по развёртыванию
- Требования (Docker, оперативная память, диск)
- Пошаговая установка
- Проверка сервисов
- Управление контейнерами
- Troubleshooting

#### **DOCKER-COMPOSE-REFERENCE.md** (5903 bytes)
Подробная справка по всем параметрам.

**Содержит:**
- Детальное описание каждого файла
- Resource limits для dev и prod
- Networking информация
- Volumes структура
- Environment переменные для каждого сервиса
- Команды управления
- Troubleshooting гайды

#### **DOCKER-FILES-GUIDE.md** (этот файл)
Навигация по всем файлам Docker Compose конфигурации.

## 🚀 Быстрый старт

### Production (рекомендуется)
```bash
cp .env.example .env
nano .env                    # Отредактируйте с реальными значениями
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Development
```bash
cp .env.example .env
docker-compose -f docker-compose.dev.yml up -d
```

### Traditional (через Makefile)
```bash
cp env.docker.template .env.docker
make docker-build
make docker-up
```

## 📋 Проверка списка

✓ docker-compose.yml (основной конфиг)
✓ docker-compose.prod.yml (production overrides)
✓ docker-compose.dev.yml (разработка)
✓ .env.example (пример переменных для разработки)
✓ .env.prod (пример переменных для production)
✓ DOCKER.md (основная документация)
✓ QUICKSTART-PROD.md (быстрый старт production)
✓ DOCKER-COMPOSE-REFERENCE.md (подробная справка)

## 📚 Рекомендуемый порядок чтения

1. **QUICKSTART-PROD.md** - первый старт за 5 минут
2. **DOCKER.md** - полное понимание конфигурации
3. **DOCKER-COMPOSE-REFERENCE.md** - детальная справка для troubleshooting
4. **Конфиги** (docker-compose.*.yml) - при необходимости редактирования

## ⚙️ Основные команды

```bash
# Запуск
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose ps

# Логи
docker-compose logs -f api
docker-compose logs -f bot
docker-compose logs -f frontend

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
```

## 🔧 Структура сервисов

```
┌─────────────────────────────────────────┐
│        Frontend (3063:3000)             │
│   ghcr.io/sema94504/frontend:latest     │
└─────────────────┬───────────────────────┘
                  │ depends_on
                  ↓
┌─────────────────────────────────────────┐
│         API (8063:8000)                 │
│   ghcr.io/sema94504/api:latest          │
│   Healthcheck: /health                  │
└──────────────┬──────────────────────────┘
               │ depends_on
               ↓
       ┌───────┴────────┐
       ↓                ↓
   ┌────────┐      ┌──────────┐
   │  Bot   │      │ SQLite   │
   │ (ghcr) │      │ (volume) │
   └────────┘      └──────────┘
```

## 🔐 Security

- Используются pre-built образы из GitHub Container Registry
- Database в named volume (можно backup)
- Logs в отдельный volume
- Dedicated network для изоляции
- Resource limits для защиты от runaway processes

## 💾 Persistence

- **db_volume** - SQLite БД (не удаляется при `docker-compose down`)
- **logs_volume** - Логи сервисов

Production: bind mounts в `/var/lib/aidialogs/data` и `/var/log/aidialogs`

## 🎯 Следующие шаги

1. Скопируйте `.env.example` в `.env`
2. Отредактируйте `.env` с реальными значениями
3. Запустите `docker-compose up -d`
4. Проверьте статус: `docker-compose ps`
5. Просмотрите логи: `docker-compose logs -f`

Для деталей см. **QUICKSTART-PROD.md** или **DOCKER.md**

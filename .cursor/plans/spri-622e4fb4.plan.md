<!-- 622e4fb4-4e02-4984-8ee1-3c5a30295db2 5a99a9e6-6d7a-4b8d-9aa8-6f02cdd93ff5 -->
# Sprint D1: Build & Publish - План выполнения

## 1. Введение в GitHub Actions и планирование (документирование)

### Создать `docs/github-actions-guide.md`

Краткий гайд с разделами:

- Что такое GitHub Actions и workflow
- Основные события (push, pull_request, release)
- Структура workflow файлов
- Варианты публикации образов (public/private registry)
- Матрица сборки для нескольких сервисов
- Кэширование слоев Docker

Цель: убедиться, что спринт хорошо задокументирован для понимания подхода.

## 2. Подготовка репозитория

### 2.1 Создать ветку тестирования

- Создать ветку `workflow/gh-actions-build` от `main`
- Использовать для разработки и тестирования workflow

### 2.2 Создать структуру `.github/`

```
.github/
├── workflows/
│   └── build.yml
└── REGISTRY.md
```

## 3. Создание GitHub Actions Workflow

### Файл `.github/workflows/build.yml`

Параметры workflow:

- **Trigger**: `push` на main, develop и tags (v*.*.*), `pull_request` на main
- **Matrix strategy**: сборка 3 образов параллельно (bot, api, frontend)
- **Образы**: `ghcr.io/username/aidialogs-{service}`
- **Теги**: `latest` для main/develop, commit SHA для всех, версионные теги для releases

Ключевые шаги:

1. Checkout кода
2. Set up Docker Buildx (для расширенного build с кэшем)
3. Login to GHCR
4. Build and push образов с использованием cache layers
5. Publish metadata (артефакты)

Особенности:

- Использовать `docker/build-push-action@v6` для оптимизации
- Кэширование через `type=gha` (GitHub Actions cache)
- Теги строятся динамически через `docker/metadata-action`
- Секреты: используется `github.token` (встроенный)

### Тегирование образов

- **Для push на main**: `ghcr.io/user/aidialogs-service:latest`, `ghcr.io/user/aidialogs-service:sha-xxxxx`
- **Для push на develop**: `ghcr.io/user/aidialogs-service:dev`, `ghcr.io/user/aidialogs-service:sha-xxxxx`
- **Для tags (v1.0.0)**: `ghcr.io/user/aidialogs-service:v1.0.0`, `ghcr.io/user/aidialogs-service:latest`

## 4. Интеграция docker-compose

### 4.1 Создать `docker-compose.registry.yml`

Альтернативный compose для работы с образами из registry:

- Замена `build:` на `image: ghcr.io/...`
- Те же environment переменные и volumes
- Комментарии о local vs registry образах
```yaml
services:
  bot:
    image: ghcr.io/username/aidialogs-bot:latest
    # ... rest same as docker-compose.yml
  api:
    image: ghcr.io/username/aidialogs-api:latest
    # ... rest same as docker-compose.yml
  frontend:
    image: ghcr.io/username/aidialogs-frontend:latest
    # ... rest same as docker-compose.yml
```


### 4.2 Обновить `docker-compose.yml`

- Оставить как есть для локальной разработки (с `build:`)
- Добавить комментарий о `docker-compose.registry.yml`

### 4.3 Создать script для управления образами

`scripts/registry-pull.sh` - скрипт для pull образов из registry и запуска через compose

```bash
#!/bin/bash
# Pull latest images from registry
docker pull ghcr.io/user/aidialogs-bot:latest
docker pull ghcr.io/user/aidialogs-api:latest
docker pull ghcr.io/user/aidialogs-frontend:latest

# Start with registry images
docker-compose -f docker-compose.registry.yml up -d

# Stop
docker-compose -f docker-compose.registry.yml down
```

## 5. Тестирование и проверка (на ветке workflow/gh-actions-build)

### 5.1 Локальное тестирование сборки

- Убедиться, что Dockerfile'ы компилируются корректно
- Проверить что образы собираются локально через docker-compose

### 5.2 Проверка GitHub Actions

- Создать pull request с изменениями workflow
- Дождаться выполнения workflow в CI
- Проверить что образы успешно собраны и опубликованы в ghcr.io

### 5.3 Проверка публичного доступа

- Скачать образы без авторизации: `docker pull ghcr.io/username/aidialogs-bot:latest`
- Запустить через `docker-compose.registry.yml`
- Убедиться, что приложение работает

## 6. Документация

### 6.1 Обновить `README.md`

Добавить секции:

- Badge статуса сборки (Build Status)
- Раздел "Использование образов из GitHub Container Registry"
- Команды для pull/push образов
- Различие между локальной сборкой и registry образами

### 6.2 Создать `docs/REGISTRY.md`

Полная инструкция:

- Как использовать образы из ghcr.io
- Команды docker pull и docker run
- Использование docker-compose.registry.yml
- Управление версионированием образов
- Public vs Private образы

### 6.3 Обновить `DOCKER.md`

- Добавить про registry образы и workflows
- Ссылка на новую документацию

### 6.4 Обновить `Makefile`

Добавить команды:

- `make registry-pull` - скачать образы из registry
- `make registry-up` - запустить с образами из registry
- `make registry-down` - остановить registry контейнеры
```makefile
registry-pull:
	@echo "Pulling images from GitHub Container Registry..."
	docker pull ghcr.io/$$(git config --get user.name)/aidialogs-bot:latest
	docker pull ghcr.io/$$(git config --get user.name)/aidialogs-api:latest
	docker pull ghcr.io/$$(git config --get user.name)/aidialogs-frontend:latest

registry-up:
	docker-compose -f docker-compose.registry.yml up -d

registry-down:
	docker-compose -f docker-compose.registry.yml down
```


## 7. Финальные шаги

### 7.1 Мерж ветки в main

После успешного тестирования слить workflow/gh-actions-build в main

### 7.2 Первый запуск на main

- Push в main должен автоматически собрать и опубликовать образы
- Проверить статус workflow в GitHub
- Проверить что образы доступны в ghcr.io

### 7.3 Подготовка к D2

Убедиться что все готово для спринта D2 (ручной deploy):

- Образы легко скачиваются из registry
- docker-compose.registry.yml работает корректно
- Документация полная для использования при развертывании

## Ключевые файлы для создания/изменения

**Новые файлы:**

- `.github/workflows/build.yml` - основной CI/CD workflow (~150-200 строк)
- `docker-compose.registry.yml` - compose для registry образов (~40 строк)
- `scripts/registry-pull.sh` - скрипт для работы с registry (~20 строк)
- `docs/github-actions-guide.md` - гайд по GitHub Actions (~100 строк)
- `docs/REGISTRY.md` - полная инструкция по registry (~150 строк)

**Измененные файлы:**

- `README.md` - добавить badge и секции про registry (~30 строк)
- `DOCKER.md` - добавить про registry образы (~20 строк)
- `Makefile` - добавить команды для registry (~15 строк)
- `docker-compose.yml` - добавить комментарии (~5 строк)

## Требования к workflow (MVP)

✓ Автоматическая сборка при push на main/develop/tags

✓ Matrix strategy для 3 сервисов (bot, api, frontend)

✓ Публикация в ghcr.io

✓ Теги: latest, commit SHA, версионные теги

✓ Кэширование для скорости

✓ Публичный доступ (без авторизации)

✓ Совместимость с docker-compose

✓ Готовность к D2 (ручной deploy)

✓ Готовность к D3 (авто deploy)

## Не включаем (пока)

✗ Lint checks

✗ Unit/Integration тесты

✗ Security scanning

✗ Multi-platform builds (arm64, amd64)

✗ Notifications/Slack alerts

## Сроки реализации (примерно)

- Этап 1 (документация GitHub Actions): 20 мин
- Этап 2 (подготовка структуры): 10 мин
- Этап 3 (workflow): 1 час
- Этап 4 (docker-compose.registry): 20 мин
- Этап 5 (тестирование): 1 час
- Этап 6 (документация проекта): 1 час
- Этап 7 (финализация): 15 мин

**Итого**: ~4-4.5 часа

## Зависимости между этапами

- Этап 1 (документация) → независимо
- Этап 2 (подготовка) → базис для всех остальных
- Этап 3 (workflow) → требует этап 2
- Этап 4 (compose) → независимо от 3, но нужно до 5
- Этап 5 (тестирование) → требует этапы 3-4
- Этап 6 (документация) → независимо, но нужно до 7
- Этап 7 (финализация) → требует этап 5

### To-dos

- [ ] Создать docs/github-actions-guide.md с объяснением GitHub Actions, workflow, matrix strategy, кэширования
- [ ] Создать структуру .github/workflows/ и .github/REGISTRY.md
- [ ] Реализовать .github/workflows/build.yml с matrix для bot/api/frontend, кэшированием, публикацией в ghcr.io
- [ ] Создать docker-compose.registry.yml для использования образов из registry
- [ ] Создать scripts/registry-pull.sh для управления образами из registry
- [ ] Добавить команды в Makefile: registry-pull, registry-up, registry-down
- [ ] Создать PR с workflow на ветку workflow/gh-actions-build и проверить его выполнение в GitHub Actions
- [ ] Локально скачать образы из ghcr.io без авторизации и запустить через docker-compose.registry.yml
- [ ] Обновить README.md: добавить badge статуса, секции про registry образы и команды
- [ ] Создать docs/REGISTRY.md с полной инструкцией по использованию образов из registry
- [ ] Обновить DOCKER.md с упоминанием registry образов и ссылкой на новую документацию
- [ ] Слить ветку workflow/gh-actions-build в main и запустить первый workflow на main
# Использование образов из GitHub Container Registry

## Обзор

Этот проект публикует Docker образы в GitHub Container Registry (GHCR) через GitHub Actions workflow.

Образы доступны по адресам:
- `ghcr.io/<owner>/aidialogs-bot`
- `ghcr.io/<owner>/aidialogs-api`
- `ghcr.io/<owner>/aidialogs-frontend`

Где `<owner>` - владелец репозитория (пользователь или организация).

## Сделать образы публичными

По умолчанию образы в GHCR приватные. Чтобы сделать их публичными:

### Вариант 1: GitHub UI

1. Перейти на `github.com/<owner>/packages`
2. Кликнуть на пакет образа (например, `aidialogs-bot`)
3. Перейти в Package settings
4. Нажать "Manage repository access"
5. Установить visibility = "Public"
6. Повторить для каждого образа (bot, api, frontend)

### Вариант 2: GitHub CLI

```bash
gh api repos/<owner>/aidialogs/packages -X PATCH -f visibility=public
```

## Загрузка образов

После того как образы сделаны публичными, их можно загружать без авторизации:

### Загрузить последнюю версию

```bash
docker pull ghcr.io/<owner>/aidialogs-bot:latest
docker pull ghcr.io/<owner>/aidialogs-api:latest
docker pull ghcr.io/<owner>/aidialogs-frontend:latest
```

### Загрузить конкретную версию

```bash
docker pull ghcr.io/<owner>/aidialogs-bot:v1.0.0
docker pull ghcr.io/<owner>/aidialogs-api:v1.0.0
docker pull ghcr.io/<owner>/aidialogs-frontend:v1.0.0
```

### Загрузить конкретный коммит

```bash
docker pull ghcr.io/<owner>/aidialogs-bot:main-sha-abc123def
```

## Запуск через docker-compose

### С помощью Makefile

Самый простой способ:

```bash
# Загрузить образы
make registry-pull GITHUB_USER=<owner>

# Запустить сервисы
make registry-up GITHUB_USER=<owner>

# Остановить сервисы
make registry-down GITHUB_USER=<owner>

# Показать логи
make registry-logs
```

### Напрямую через docker-compose

1. Установить переменную окружения:
```bash
export GITHUB_USERNAME=<owner>
```

2. Запустить:
```bash
docker-compose -f docker-compose.registry.yml up -d
```

3. Остановить:
```bash
docker-compose -f docker-compose.registry.yml down
```

### Через скрипт

```bash
# Загрузить образы (по умолчанию latest)
./scripts/registry-pull.sh <owner> latest pull

# Запустить сервисы
./scripts/registry-pull.sh <owner> latest up

# Остановить сервисы
./scripts/registry-pull.sh <owner> latest down

# Показать логи
./scripts/registry-pull.sh <owner> latest logs
```

## Доступные сервисы

После запуска сервисы будут доступны по адресам:

- **Frontend**: http://localhost:3000 - веб-интерфейс
- **API**: http://localhost:8000 - REST API
- **API Docs**: http://localhost:8000/docs - документация API
- **Health Check**: http://localhost:8000/health - проверка работоспособности

## Запуск отдельных образов

### Запустить только API

```bash
docker run -it \
  --env-file .env.docker \
  -p 8000:8000 \
  -v ./data:/app/data \
  ghcr.io/<owner>/aidialogs-api:latest
```

### Запустить бота

```bash
docker run -it \
  --env-file .env.docker \
  -v ./data:/app/data \
  ghcr.io/<owner>/aidialogs-bot:latest
```

## Управление версионированием образов

### Теги, которые автоматически создаются

При push на `main` ветку:
```
ghcr.io/<owner>/aidialogs-bot:latest
ghcr.io/<owner>/aidialogs-bot:main-sha-abc123def
```

При push на `develop` ветку:
```
ghcr.io/<owner>/aidialogs-bot:dev
ghcr.io/<owner>/aidialogs-bot:develop-sha-abc123def
```

При создании тега релиза `v1.0.0`:
```
ghcr.io/<owner>/aidialogs-bot:v1.0.0
ghcr.io/<owner>/aidialogs-bot:1.0
ghcr.io/<owner>/aidialogs-bot:latest
```

## Проверка статуса workflow

Посмотреть статус сборки образов:

1. Перейти на GitHub репозиторий
2. Кликнуть на вкладку "Actions"
3. Выбрать workflow "Build & Publish Docker Images"
4. Видны все завершенные и текущие сборки

## Troubleshooting

### Образы не загружаются (pull failed)

**Проблема:** `Error response from daemon: unauthorized`

**Решение:** Образ приватный. Убедитесь что он сделан публичным (см. "Сделать образы публичными").

### Образ не найден (no such image)

**Проблема:** `pull access denied, repository does not exist or may require 'docker login'`

**Решение:** Проверьте:
- Правильность имени образа (`<owner>` - это ваш GitHub username)
- Правильность тега (latest, v1.0.0, и т.д.)
- Что workflow завершился успешно (проверьте Actions)

### Сервисы не запускаются

**Проблема:** Ошибки при старте через docker-compose

**Решение:**
1. Убедитесь что .env.docker существует и заполнен: `cp env.docker.template .env.docker`
2. Проверьте что образы загружены: `docker images | grep aidialogs`
3. Проверьте логи: `docker compose -f docker-compose.registry.yml logs`

### Port already in use

**Проблема:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Решение:**
1. Остановите старые контейнеры: `make registry-down`
2. Или используйте другие порты в docker-compose.registry.yml

## Локальная разработка vs Registry

### Локальная разработка

```bash
# Используется docker-compose.yml с build:
make docker-build
make docker-up
```

Преимущества:
- Быстрая итерация при изменении кода
- Работает без интернета
- Изменения видны сразу

### Deployment с registry образами

```bash
# Используется docker-compose.registry.yml с image:
make registry-pull
make registry-up
```

Преимущества:
- Образы уже собраны и протестированы
- Не нужно собирать на production
- Гарантия что используется нужная версия
- Быстрый deploy

## Интеграция с D2 и D3

### D2: Ручной deploy

Используйте registry образы для развертывания на server:

```bash
# На production server
ssh user@server
cd /opt/aidialogs
export GITHUB_USERNAME=<owner>
docker-compose -f docker-compose.registry.yml pull
docker-compose -f docker-compose.registry.yml up -d
```

### D3: Автоматический deploy

GitHub Actions workflow может автоматически:
1. Собрать и опубликовать образы
2. Развернуть на server через SSH или API
3. Перезапустить сервисы

Смотрите документацию спринта D3 для настройки автодеплоя.

## GitHub Actions Workflow

Workflow `.github/workflows/build.yml`:
- Автоматически запускается на `push` в main/develop
- Автоматически запускается при создании release tags
- Собирает 3 образа параллельно (matrix strategy)
- Использует кэширование для скорости
- Публикует в GHCR

Подробнее: `docs/github-actions-guide.md`

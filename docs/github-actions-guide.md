# GitHub Actions и CI/CD для Docker образов

## Что такое GitHub Actions

GitHub Actions - это встроенная система автоматизации GitHub, позволяющая запускать рабочие процессы при различных событиях в репозитории (push, pull request, release и т.д.).

## Основные концепции

### Workflow
Файл YAML в `.github/workflows/` определяет последовательность шагов для автоматизации задач.

### Trigger (события)
События, вызывающие запуск workflow:
- `push` - коммит в ветку
- `pull_request` - создание/обновление PR
- `release` - создание релиза
- `schedule` - расписание (cron)
- `workflow_dispatch` - ручной запуск

### Jobs (задачи)
Набор шагов (steps), выполняемых параллельно или последовательно.

### Steps (шаги)
Отдельные команды или actions, выполняемые по очереди.

### Actions
Готовые переиспользуемые блоки кода из GitHub Marketplace.

## Matrix Strategy (матричная сборка)

Матричная стратегия позволяет запускать одну job с разными комбинациями параметров.

### Пример: сборка нескольких Docker образов

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    
steps:
  - name: Build ${{ matrix.service }}
    run: docker build -t aidialogs-${{ matrix.service }} -f Dockerfile.${{ matrix.service }} .
```

**Результат:** 3 параллельных job'а для каждого сервиса.

### Преимущества
- Параллельное выполнение
- DRY (не повторяем код для каждого сервиса)
- Легко добавить новый сервис

## Публикация Docker образов

### Варианты registry

#### GitHub Container Registry (GHCR) - публичный
```bash
ghcr.io/username/image-name:tag
```
- Встроенный, бесплатный
- Образы могут быть публичными (без авторизации)
- Аутентификация через `github.token`

#### Docker Hub - публичный
```bash
docker.io/username/image-name:tag
```
- Требует отдельной регистрации
- Свободные паблик образы
- Аутентификация через Docker Hub token

#### Private registry
- AWS ECR, Google Cloud Artifact Registry и т.д.
- Требует платных сервисов или собственного сервера

### Для MVP используем: GitHub Container Registry (ghcr.io)
- Встроенный в GitHub
- Публичный доступ без авторизации
- Интеграция с `github.token`

## Кэширование Docker layers

### Проблема
- Первая сборка: долгая (установка зависимостей, загрузка пакетов)
- Повторная сборка без кэша: снова долгая

### Решение: Docker layer caching

Docker кэширует слои (layers) образа. Если исходный код не изменился, слой переиспользуется.

#### Типы кэша в GitHub Actions

**1. type=gha (GitHub Actions cache)**
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```
- Встроенный, автоматический
- Хранится в GitHub Actions storage
- Бесплатный, но с лимитом (~5-10 GB per repo)
- Быстро

**2. type=registry (кэш в registry)**
```yaml
cache-from: type=registry,ref=ghcr.io/user/image:buildcache
cache-to: type=registry,ref=ghcr.io/user/image:buildcache
```
- Кэш хранится как отдельный образ в registry
- Требует push прав
- Медленнее чем GHA
- Экономит место в GHA cache

**3. type=local (локальный кэш)**
```yaml
cache-from: type=local,src=/path/to/cache
```
- Для локальной разработки
- На CI может быть недоступен

### Для MVP используем: type=gha
- Встроенный, не требует настройки
- Достаточно быстро
- Автоматическое управление

## Структура build.yml workflow

```yaml
name: Build & Publish Docker Images
on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, api, frontend]
    steps:
      # 1. Checkout кода
      - uses: actions/checkout@v4
      
      # 2. Setup Docker Buildx (для расширенных возможностей)
      - uses: docker/setup-buildx-action@v3
      
      # 3. Login к GHCR
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      # 4. Extract metadata (теги, labels)
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ghcr.io/${{ github.repository_owner }}/aidialogs-${{ matrix.service }}
      
      # 5. Build and Push
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile.${{ matrix.service }}
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Теги образов

### Для main branch
```
ghcr.io/user/aidialogs-bot:latest
ghcr.io/user/aidialogs-bot:sha-abc123
```

### Для develop branch
```
ghcr.io/user/aidialogs-bot:dev
ghcr.io/user/aidialogs-bot:sha-abc123
```

### Для release tag (v1.0.0)
```
ghcr.io/user/aidialogs-bot:v1.0.0
ghcr.io/user/aidialogs-bot:latest
```

Динамическое тегирование через `docker/metadata-action` автоматически генерирует теги на основе:
- Ветки (main → latest, develop → dev)
- Тега в git (v1.0.0 → v1.0.0, latest)
- SHA коммита (всегда)

## Публичный доступ к образам

### GitHub Container Registry visibility

По умолчанию образы в GHCR приватные. Чтобы сделать публичными:

**Вариант 1: Через GitHub UI**
1. Перейти на package страницу: `github.com/user/aidialogs`
2. Package settings → Manage repository access
3. Change visibility → Public

**Вариант 2: Через workflow**
```yaml
# После push образа
- name: Make image public
  run: |
    gh api repos/${{ github.repository }}/package-settings \
      -X PATCH \
      -f visibility=public
```

## Интеграция с docker-compose

### Локальная разработка: используем build
```yaml
# docker-compose.yml
services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
```

### Deployment: используем образы из registry
```yaml
# docker-compose.registry.yml
services:
  bot:
    image: ghcr.io/user/aidialogs-bot:latest
```

### Переключение
```bash
# Локальная сборка
docker-compose up -d

# Запуск из registry
docker-compose -f docker-compose.registry.yml up -d
```

## Проверка в CI

### On push to main/develop
✓ Workflow автоматически запускается  
✓ Образы собираются и публикуются  
✓ Видны в GitHub Actions → Workflow runs  

### On pull_request
✓ Workflow запускается для проверки  
✓ Образы НЕ публикуются (push: false)  
✓ Проверяется что сборка работает  

### On release tag
✓ Образы публикуются с версионным тегом  
✓ И с тегом `latest`  

## Troubleshooting

### Workflow не запускается
- Проверить что файл в `.github/workflows/`
- Проверить синтаксис YAML
- Проверить triggers в `on:`

### Образы не публикуются
- Проверить что `push: true` или `push: ${{ github.event_name != 'pull_request' }}`
- Проверить логин к registry
- Проверить `github.token` имеет права

### Кэш не работает
- Кэш в GHA хранится 7 дней
- После этого кэш удаляется
- Первая сборка после очистки кэша будет медленной

### Образы не доступны публично
- Проверить visibility на странице package
- Убедиться что package visibility = public

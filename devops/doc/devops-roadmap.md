# DevOps Roadmap

Развитие DevOps процессов для проекта по MVP подходу. Путь от локального отдельного запуска до удаленного сервера с автоматическим развертыванием.

## Спринты

| Спринт | Описание | Статус | План |
|--------|---------|--------|------|
| **D0** | Basic Docker Setup | ✅ Completed | [План D0](plans/D0-basic-docker-setup.md) |
| **D1** | Build & Publish | 🔴 Pending | - |
| **D2** | Развертывание на сервер | 🔴 Pending | - |
| **D3** | Auto Deploy | 🔴 Pending | - |

---

## Спринт D0: Basic Docker Setup

**Цель:** Запустить все сервисы локально через docker-compose одной командой.

**Состав работ:**
- Dockerfile для Bot (Python + UV)
- Dockerfile для API (FastAPI + UV)
- Dockerfile для Frontend (Next.js + pnpm)
- docker-compose.yml с 4 сервисами (PostgreSQL, Bot, API, Frontend)
- .dockerignore для каждого сервиса
- Проверка: `docker-compose up` работает локально
- Обновление README.md с инструкциями

---

## Спринт D1: Build & Publish

**Цель:** Автоматическая сборка и публикация Docker образов в GitHub Container Registry.

**Состав работ:**
- GitHub Actions workflow `.github/workflows/build.yml`
- Сборка 3 образов (bot, api, frontend) при push в main
- Публикация в ghcr.io с тегом latest
- Инструкция по настройке GitHub Actions permissions
- Обновление README.md с badges статуса

---

## Спринт D2: Развертывание на сервер

**Цель:** Развернуть приложение на удаленном сервере вручную.

**Состав работ:**
- Пошаговая инструкция для ручного деплоя
- SSH подключение, копирование конфигов
- docker login к ghcr.io
- docker-compose pull и docker-compose up -d
- Запуск миграций БД
- Проверка работоспособности

---

## Спринт D3: Auto Deploy

**Цель:** Автоматическое развертывание на сервер через GitHub Actions.

**Состав работ:**
- GitHub Actions workflow `.github/workflows/deploy.yml`
- Trigger: ручной запуск (workflow_dispatch)
- SSH подключение и перезапуск сервисов
- Инструкция по настройке GitHub secrets
- Уведомления о статусе деплоя
- Кнопка "Deploy" в README.md

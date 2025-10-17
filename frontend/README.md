# AIDialogs Frontend

Веб-интерфейс для администрирования и мониторинга Telegram бота AIDialogs.

## Технологический стек

- **Framework:** Next.js 15 (App Router)
- **Язык:** TypeScript
- **UI Library:** shadcn/ui
- **Styling:** Tailwind CSS
- **Пакетный менеджер:** pnpm

## Структура проекта

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Главная страница
│   └── test-api/           # Тестовая страница API
├── components/             # React компоненты
│   └── ui/                 # shadcn/ui компоненты
├── lib/                    # Утилиты и API
│   ├── api-client.ts       # API клиент
│   ├── types.ts            # TypeScript типы
│   └── utils.ts            # Утилиты (cn)
├── public/                 # Статические файлы
├── doc/                    # Документация
└── components.json         # shadcn/ui конфигурация
```

## Команды

### Разработка

```bash
# Запуск dev-сервера
pnpm dev

# Линтинг
pnpm lint

# Проверка типов
pnpm typecheck

# Production build
pnpm build

# Запуск production сервера
pnpm start
```

### Через Makefile (из корня проекта)

```bash
# Запуск frontend dev-сервера
make frontend-dev

# Линтинг frontend
make frontend-lint

# Проверка типов frontend
make frontend-typecheck

# Production build frontend
make frontend-build
```

## API

Frontend подключается к Mock API на `http://localhost:8000`.

Для запуска Mock API:

```bash
make run-api
```

### Endpoints

- `GET /api/stats` - получение статистики для дашборда

## Тестирование

Тестовая страница доступна по адресу: http://localhost:3000/test-api

## Переменные окружения

Создайте `.env.local` файл:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Разработка

1. Установите зависимости: `pnpm install`
2. Запустите Mock API: `make run-api`
3. Запустите dev-сервер: `pnpm dev`
4. Откройте http://localhost:3000

## Документация

- [Frontend Roadmap](doc/frontend-roadmap.md)
- [API Requirements](doc/api-requirements.md)
- [API Examples](doc/api-examples.md)

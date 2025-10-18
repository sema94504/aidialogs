# План: Спринт FS2 - Инициализация Frontend проекта

## Технологический стек

- **Framework:** Next.js 15 (App Router)
- **Язык:** TypeScript
- **UI Library:** shadcn/ui
- **Styling:** Tailwind CSS
- **Пакетный менеджер:** pnpm

## Итерации

### Итерация 1: Инициализация Next.js проекта

1. Создать Next.js проект в `frontend/` с помощью `pnpm create next-app`

   - TypeScript: да
   - App Router: да
   - Tailwind CSS: да
   - ESLint: да
   - src/ directory: нет (использовать app/)

2. Настроить `package.json` с основными scripts
3. Проверить запуск dev-сервера

**Файлы:**

- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/next.config.ts`
- `frontend/tailwind.config.ts`
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`

### Итерация 2: Установка и настройка shadcn/ui

1. Инициализировать shadcn/ui через `pnpm dlx shadcn@latest init`
2. Настроить `components.json` с правильными путями
3. Установить базовые компоненты: Button, Card
4. Создать структуру `components/ui/`

**Файлы:**

- `frontend/components.json`
- `frontend/components/ui/button.tsx`
- `frontend/components/ui/card.tsx`
- `frontend/lib/utils.ts`

### Итерация 3: API клиент и типы

1. Создать типы данных на основе контракта API из `api-requirements.md`
2. Реализовать API клиент в `lib/api-client.ts`

   - Базовый URL: `http://localhost:8000`
   - Метод `getStats()` для GET /api/stats
   - Обработка ошибок

3. Создать тестовую страницу с запросом к API

**Файлы:**

- `frontend/lib/types.ts` (копия моделей из Python API)
- `frontend/lib/api-client.ts`
- `frontend/app/test-api/page.tsx` (тестовая страница)

### Итерация 4: Базовая структура и документация

1. Создать базовую структуру директорий

   - `app/` - страницы (App Router)
   - `components/` - компоненты
   - `lib/` - утилиты и API
   - `public/` - статика

2. Настроить `.gitignore` для frontend
3. Добавить `frontend/README.md` с командами запуска
4. Обновить корневой Makefile с командами frontend
5. Создать `make help` команду для отображения всех доступных команд проекта

**Файлы:**

- `frontend/.gitignore`
- `frontend/README.md`
- `Makefile` (обновление с help и frontend командами)

### Итерация 5: Линтинг и проверка качества

1. Настроить ESLint конфигурацию
2. Добавить scripts для проверки:

   - `pnpm lint` - ESLint
   - `pnpm typecheck` - TypeScript
   - `pnpm build` - production build

3. Проверить все команды в `package.json` работают корректно

**Конфигурация:**

- `frontend/.eslintrc.json`
- `frontend/package.json` (scripts)

### Итерация 6: Финализация и документация

1. Проверить работу dev-сервера на `localhost:3000`
2. Проверить тестовую страницу успешно подключается к Mock API
3. Проверить все команды Makefile работают
4. Обновить `frontend/doc/frontend-roadmap.md`:

   - Изменить статус FS2 с "⏳ Запланирован" на "✅ Завершен"
   - Добавить ссылку на план в таблицу спринтов

5. Создать отчет о завершении: `frontend/doc/plans/fs2-completion-report.md`

**Файлы:**

- `frontend/doc/frontend-roadmap.md` (обновление)
- `frontend/doc/plans/fs2-completion-report.md` (новый)

## Критерии готовности

- ✅ Next.js проект инициализирован с TypeScript и App Router
- ✅ Tailwind CSS настроен и работает
- ✅ shadcn/ui установлен, базовые компоненты доступны
- ✅ API клиент создан и работает с Mock API
- ✅ Тестовая страница успешно получает данные от API
- ✅ Dev-сервер запускается на `localhost:3000`
- ✅ Все команды в `package.json` работают (lint, typecheck, build)
- ✅ Все команды в Makefile работают (frontend-dev, frontend-lint и т.д.)
- ✅ `make help` отображает все доступные команды
- ✅ `frontend-roadmap.md` обновлен: статус FS2 = ✅, ссылка на план добавлена
- ✅ Отчет о завершении создан
- ✅ Структура проекта соответствует best practices

## Команды

```bash
# Помощь по командам
make help

# Запуск frontend dev-сервера
make frontend-dev

# Линтинг frontend
make frontend-lint

# Проверка типов frontend
make frontend-typecheck

# Production build frontend
make frontend-build

# Запуск Mock API (для тестирования)
make run-api
```

## Структура проекта

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout (App Router)
│   ├── page.tsx            # Главная страница
│   └── test-api/
│       └── page.tsx        # Тестовая страница API
├── components/
│   └── ui/                 # shadcn/ui компоненты
│       ├── button.tsx
│       └── card.tsx
├── lib/
│   ├── api-client.ts       # API клиент
│   ├── types.ts            # TypeScript типы
│   └── utils.ts            # Утилиты (cn и др.)
├── public/                 # Статические файлы
├── components.json         # shadcn/ui конфигурация
├── next.config.ts          # Next.js конфигурация
├── tailwind.config.ts      # Tailwind конфигурация
├── tsconfig.json           # TypeScript конфигурация
├── package.json            # Зависимости и scripts
└── README.md               # Документация
```


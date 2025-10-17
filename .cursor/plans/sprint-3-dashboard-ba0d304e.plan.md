<!-- ba0d304e-be3e-4761-9375-9ccec1c607f8 477afd81-274f-474b-8dbf-8484ae9a48e2 -->
# Спринт FS3: Dashboard статистики диалогов

## Технический стек

- **UI Компоненты:** shadcn/ui (Card, Table, Badge, Select)
- **Графики:** Recharts (стандарт для shadcn/ui)
- **Иконки:** lucide-react
- **Референс:** https://ui.shadcn.com/blocks#dashboard-01

## Ключевые возможности

- Responsive дизайн с адаптацией под mobile/tablet/desktop/wide
- Фильтр периода данных: 7, 14, 30, 90 дней
- Real-time обновление при смене периода

## Итерации

### Итерация 1: Установка зависимостей

Установить недостающие компоненты shadcn/ui и библиотеки для графиков:

```bash
cd frontend
pnpm dlx shadcn@latest add table badge select
pnpm add recharts date-fns
pnpm add -D @types/recharts
```

**Файлы:**

- `components/ui/table.tsx`
- `components/ui/badge.tsx`
- `components/ui/select.tsx`
- `package.json` (обновление)

### Итерация 2: Обновление API клиента

Расширить `lib/api-client.ts`:

- Добавить параметр `days` в `getStats(days?: number)`
- Обновить URL: `/api/stats?days={days}`
- Дефолтное значение: 7 дней

**Файлы:**

- `lib/api-client.ts` (обновление)

### Итерация 3: Period Filter компонент

Создать `components/dashboard/period-filter.tsx`:

- Select с опциями: "7 дней", "14 дней", "30 дней", "90 дней"
- Callback для изменения периода
- Адаптивная ширина: full-width на mobile, auto на desktop

**Файлы:**

- `components/dashboard/period-filter.tsx`

### Итерация 4: Metrics Cards (адаптивные)

Создать `components/dashboard/metrics-cards.tsx`:

- 4 карточки: Total Users, Total Messages, Active Today, Avg Message Length
- Иконки: `Users`, `MessageSquare`, `Activity`, `MessageCircle` из lucide-react
- **Адаптивность:**
  - Mobile (320-768px): 1 колонка, компактные карточки
  - Tablet (768-1024px): 2 колонки в grid
  - Desktop (1024+): 4 колонки
  - Wide (1536+): 4 колонки с увеличенным padding
- Hover эффект (scale на desktop, без эффекта на mobile)

**Файлы:**

- `components/dashboard/metrics-cards.tsx`

### Итерация 5: Activity Chart (адаптивный)

Создать `components/dashboard/activity-chart.tsx`:

- Line Chart на базе Recharts с ResponsiveContainer
- X-axis: даты (формат DD MMM)
- Y-axis: количество сообщений
- Tooltip с деталями
- **Адаптивность:**
  - Mobile: высота 250px, упрощенные метки осей (каждая 2-я дата)
  - Tablet: высота 300px, все метки
  - Desktop: высота 400px, полная версия с Grid
- Auto-resize при изменении окна

**Файлы:**

- `components/dashboard/activity-chart.tsx`

### Итерация 6: Recent Messages Table (адаптивная)

Создать `components/dashboard/recent-messages.tsx`:

- **Адаптивность:**
  - Mobile: карточки вместо таблицы (Card layout)
  - Tablet/Desktop: Table с колонками User ID, Role, Preview, Timestamp
- Badge для роли (user: синий, assistant: зеленый)
- Preview обрезается: 50 символов (mobile), 100 (desktop)
- Timestamp форматирование с date-fns (относительное время)

**Файлы:**

- `components/dashboard/recent-messages.tsx`

### Итерация 7: Dashboard страница с фильтром

Создать `app/dashboard/page.tsx`:

- Client Component для динамического обновления
- State для выбранного периода
- Интеграция PeriodFilter с callback
- Загрузка данных через `getStats(period)`
- Layout с заголовком "Dashboard" и Period Filter в header
- Loading/Error состояния

**Файлы:**

- `app/dashboard/page.tsx`

### Итерация 8: Навигация и Layout

1. Обновить `app/layout.tsx`:

   - Navigation Bar (адаптивный):
     - Mobile: hamburger menu или compact nav
     - Desktop: full nav с Logo, Links (Dashboard, Chat)
   - Footer с версией

2. Обновить `app/page.tsx`:

   - Редирект на `/dashboard`

**Файлы:**

- `app/layout.tsx`
- `app/page.tsx`

### Итерация 9: Стилизация и платформенная адаптация

- Применить цветовую палитру из `front-vision.md`
- Breakpoints (из front-vision.md):
  - Mobile: 320px - 768px
  - Tablet: 769px - 1024px (md)
  - Desktop: 1025px+ (lg)
  - Wide: 1536px+ (2xl)
- Touch-friendly элементы на mobile (min 44x44px)
- Оптимизация spacing для разных экранов
- Loading состояния (skeleton)
- Error boundaries
- Accessibility (ARIA labels, keyboard navigation, screen reader)

### Итерация 10: Тестирование и документация

1. Проверить на разных разрешениях:

   - Mobile: 375x667 (iPhone SE), 390x844 (iPhone 13)
   - Tablet: 768x1024 (iPad)
   - Desktop: 1920x1080
   - Wide: 2560x1440

2. Проверить работу с Mock API для всех периодов

3. Создать отчет: `doc/plans/fs3-completion-report.md`

4. Обновить roadmap: статус FS3 = "✅ Завершен"

**Файлы:**

- `doc/plans/fs3-completion-report.md`
- `doc/frontend-roadmap.md` (обновление)

## Структура файлов

```
frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx              # Dashboard с фильтром периода
│   ├── layout.tsx                # Root layout с навигацией
│   └── page.tsx                  # Редирект на /dashboard
├── components/
│   ├── dashboard/
│   │   ├── period-filter.tsx     # Фильтр периода
│   │   ├── metrics-cards.tsx     # Адаптивные карточки метрик
│   │   ├── activity-chart.tsx    # Адаптивный график
│   │   └── recent-messages.tsx   # Адаптивная таблица/карточки
│   └── ui/
│       ├── card.tsx
│       ├── button.tsx
│       ├── table.tsx             # Новый
│       ├── badge.tsx             # Новый
│       └── select.tsx            # Новый
└── lib/
    └── api-client.ts             # Обновлен с параметром days
```

## Критерии готовности

- ✅ Dashboard страница доступна на `/dashboard`
- ✅ Period Filter работает: 7, 14, 30, 90 дней
- ✅ API клиент поддерживает параметр `days`
- ✅ Metrics Cards адаптивные: 1→2→4 колонки
- ✅ Activity Chart адаптивный: высота и метки меняются
- ✅ Recent Messages: карточки на mobile, таблица на desktop
- ✅ Навигация адаптивная (hamburger на mobile)
- ✅ Responsive design протестирован на всех breakpoints
- ✅ Touch-friendly на mobile (44x44px минимум)
- ✅ Данные загружаются из API клиента с выбранным периодом
- ✅ Обработка loading и error состояний
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ Документация и отчет созданы

### To-dos

- [ ] Установить shadcn/ui компоненты (table, badge) и recharts с типами
- [ ] Создать страницу app/dashboard/page.tsx с основной структурой
- [ ] Реализовать компонент MetricsCards с 4 карточками и иконками
- [ ] Создать ActivityChart компонент с Line Chart на Recharts
- [ ] Создать RecentMessages таблицу с Badge для ролей
- [ ] Обновить layout.tsx с навигацией и footer
- [ ] Стилизация, loading/error состояния, accessibility
- [ ] Создать отчет о завершении и обновить roadmap
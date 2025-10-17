# Dashboard Components

Набор адаптивных компонентов для отображения статистики диалогов.

## Компоненты

### PeriodFilter

Фильтр для выбора периода отображения данных.

```tsx
import { PeriodFilter } from "@/components/dashboard/period-filter";

<PeriodFilter value={7} onChange={(days) => console.log(days)} />
```

**Props:**
- `value: number` - текущий выбранный период (7, 14, 30, 90)
- `onChange: (value: number) => void` - callback при изменении

**Особенности:**
- Адаптивная ширина: full на mobile, 180px на desktop
- Label и ARIA атрибуты

### MetricsCards

Карточки с ключевыми метриками.

```tsx
import { MetricsCards } from "@/components/dashboard/metrics-cards";

<MetricsCards metrics={data.metrics} />
```

**Props:**
- `metrics: Metrics` - объект с метриками

**Структура Metrics:**
```ts
interface Metrics {
  total_users: number;
  total_messages: number;
  active_today: number;
  avg_message_length: number;
}
```

**Адаптивность:**
- Mobile: 1 колонка
- Tablet: 2 колонки
- Desktop: 4 колонки

### ActivityChart

График активности по дням.

```tsx
import { ActivityChart } from "@/components/dashboard/activity-chart";

<ActivityChart data={data.activity_chart} />
```

**Props:**
- `data: ActivityDataPoint[]` - массив точек графика

**Структура ActivityDataPoint:**
```ts
interface ActivityDataPoint {
  date: string;      // ISO формат YYYY-MM-DD
  count: number;     // количество сообщений
}
```

**Адаптивность:**
- Mobile: высота 300px
- Desktop: высота 400px

### RecentMessages

Список последних сообщений.

```tsx
import { RecentMessages } from "@/components/dashboard/recent-messages";

<RecentMessages messages={data.recent_messages} />
```

**Props:**
- `messages: RecentMessage[]` - массив сообщений

**Структура RecentMessage:**
```ts
interface RecentMessage {
  telegram_id: number;
  role: "user" | "assistant";
  preview: string;
  created_at: string;  // ISO datetime
}
```

**Адаптивность:**
- Mobile: карточки, preview до 50 символов
- Desktop: таблица, preview до 100 символов

## Accessibility

Все компоненты соответствуют WCAG 2.1 AA:
- ARIA labels
- Keyboard navigation
- Screen reader support
- Семантический HTML
- Touch-friendly (min 44x44px)

## Примеры использования

### Полный Dashboard

```tsx
"use client";

import { useState, useEffect } from "react";
import { getStats } from "@/lib/api-client";
import { PeriodFilter } from "@/components/dashboard/period-filter";
import { MetricsCards } from "@/components/dashboard/metrics-cards";
import { ActivityChart } from "@/components/dashboard/activity-chart";
import { RecentMessages } from "@/components/dashboard/recent-messages";

export default function DashboardPage() {
  const [period, setPeriod] = useState(7);
  const [data, setData] = useState(null);

  useEffect(() => {
    getStats(period).then(setData);
  }, [period]);

  if (!data) return <div>Загрузка...</div>;

  return (
    <div className="space-y-6">
      <PeriodFilter value={period} onChange={setPeriod} />
      <MetricsCards metrics={data.metrics} />
      <ActivityChart data={data.activity_chart} />
      <RecentMessages messages={data.recent_messages} />
    </div>
  );
}
```


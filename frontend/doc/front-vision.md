# 🎨 Техническое видение UI - AIDialogs Dashboard

**Версия:** 1.0  
**Дата:** 2025-10-17  
**Статус:** Утверждено

---

## 📋 Обзор

AIDialogs Dashboard — веб-приложение для администраторов и аналитиков Telegram бота. Основное назначение: мониторинг активности пользователей, анализ статистики диалогов и взаимодействие с ботом через интерфейс.

**Целевая аудитория:**
- Администраторы системы
- Аналитики
- Разработчики

---

## 🎯 Принципы проектирования

1. **Простота и ясность** - интуитивный интерфейс без лишних элементов
2. **Производительность** - быстрая загрузка и отзывчивость
3. **Масштабируемость** - архитектура готова к расширению функционала
4. **Доступность** - соответствие WCAG 2.1 AA
5. **Темизация** - поддержка светлой и темной темы (future)

---

## 🏗️ Структура приложения

```
App Root Layout
├── Navigation Bar
│   ├── Logo
│   ├── Links (Dashboard, Chat, Settings)
│   └── User Menu
│
├── Main Content Area
│   ├── /                    # Главная страница
│   ├── /dashboard          # Dashboard (FS3)
│   ├── /chat              # AI Chat (FS4)
│   └── /settings          # Settings (future)
│
└── Footer
    └── Version, Links
```

---

## 📊 Dashboard (FS3)

### Назначение
Отображение ключевых метрик и анализ активности диалогов.

### Компоненты

#### 1. Metrics Cards (Верхняя часть)
Четыре карточки с ключевыми метриками:
- **Total Users** - всего пользователей
- **Total Messages** - всего сообщений
- **Active Today** - активных пользователей сегодня
- **Avg Message Length** - средняя длина сообщения

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total Users │Tot Messages │ Active Today│ Avg Msg Len │
│     42      │    1337     │      5      │    87.5     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Стиль:**
- Фон: gradient или solid color
- Иконка: lucide-react (Users, MessageSquare, Activity, MessageCircle)
- Текст: метрика + number + description
- Hover: scale эффект
- Responsive: 1 column (mobile) → 4 columns (desktop)

#### 2. Activity Chart (График)
Визуализация активности за последние 7 дней.

**Тип графика:** Line Chart (или Bar Chart)
**X-axis:** Даты (YYYY-MM-DD)
**Y-axis:** Количество сообщений
**Интерактивность:** Tooltip при наведении

#### 3. Recent Messages (Таблица/Список)
Последние 10 сообщений с деталями.

**Поля:**
- User ID (telegram_id)
- Role (user/assistant) - с цветовой кодировкой
- Preview (первые 100 символов)
- Timestamp (дата и время создания)

---

## 💬 AI Chat Interface (FS4)

### Назначение
Взаимодействие администратора с ботом через естественный язык.

### Компоненты

1. **Chat Header**
2. **Messages Area** - с разными стилями для user/assistant
3. **Input Area** - text input с send button

---

## 🎨 Design System

### Цветовая палитра

**Светлая тема (default):**
- Primary: #0EA5E9 (blue)
- Secondary: #F3F4F6 (gray-100)
- Success: #10B981 (green)
- Warning: #F59E0B (amber)
- Error: #EF4444 (red)

**Темная тема (future):**
- Primary: #0EA5E9 (blue)
- Secondary: #1F2937 (gray-800)
- Text: #F3F4F6 (gray-100)
- Background: #111827 (gray-950)

### Typography

```
Heading 1 (H1): 36px, bold, line-height: 1.2
Heading 2 (H2): 28px, bold, line-height: 1.3
Heading 3 (H3): 24px, semibold, line-height: 1.4
Body:           16px, regular, line-height: 1.6
Caption:        14px, regular, line-height: 1.5
```

### Spacing & Border Radius

```
Spacing: xs(4px) sm(8px) md(16px) lg(24px) xl(32px) 2xl(48px)
Radius:  sm(4px) md(8px) lg(16px) full(9999px)
```

---

## 📱 Responsive Design

### Breakpoints (Tailwind CSS)

```
Mobile:    320px - 768px   (default)
Tablet:    769px - 1024px  (md)
Desktop:   1025px+         (lg)
Wide:      1536px+         (2xl)
```

---

## ♿ Accessibility

- WCAG 2.1 AA Compliance
- Keyboard navigation (Tab, Enter, Esc)
- Screen reader support (ARIA labels)
- Color contrast ratio ≥ 4.5:1

---

## 🚀 Performance Target

- **First Contentful Paint:** < 1.5s
- **Largest Contentful Paint:** < 2.5s
- **Cumulative Layout Shift:** < 0.1
- **Time to Interactive:** < 3.5s

---

## 📈 Roadmap

### Phase 1 (FS2 - ✅ Завершено)
- Инициализация проекта
- Setup компонентной библиотеки

### Phase 2 (FS3 - Запланировано)
- Dashboard с метриками
- Activity chart
- Recent messages список

### Phase 3 (FS4 - Запланировано)
- AI Chat interface
- Message history
- Text2SQL pipeline

### Phase 4 (Future)
- Темная тема
- Экспорт данных
- Расширенная аналитика
- Кастомизация dashboard

---

## 📝 История изменений

| Версия | Дата | Описание |
|--------|------|---------|
| 1.0 | 2025-10-17 | Инициальная версия |

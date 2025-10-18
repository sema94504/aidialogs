# ADR: Выбор технологического стека для Frontend

**Status:** Approved  
**Date:** 2025-10-17  
**Context:** FS2 - Инициализация Frontend проекта  
**Decision Maker:** Development Team

---

## 📌 Проблема

Необходимо выбрать технологический стек для разработки веб-интерфейса администратора AIDialogs Dashboard.

**Требования:**
- Быстрая разработка с хорошей DX
- Полнотекстовая типизация
- Компонентная архитектура
- Высокая производительность
- Готовность к масштабированию
- Активное сообщество

---

## 🎯 Альтернативы

### Option 1: Next.js + React ✅ **Выбрано**

**Преимущества:**
- App Router - современный подход (Server Components)
- Built-in оптимизация (Image, Font, Code splitting)
- API Routes - backend на том же сервере
- Excellent DX с turbopack
- Простая деплойка

**Недостатки:**
- Learning curve для новичков

**Версия:** 15.5.6 (Turbopack, latest)

---

### Option 2: Vite + React

**Преимущества:**
- Очень быстрый dev server (~100ms)
- Простота конфигурации

**Недостатки:**
- Нет встроенной оптимизации для production
- Нет API Routes
- Нужен отдельный бэкенд-фреймворк

---

### Option 3: Vue + Nuxt

**Преимущества:**
- Быстрый dev server
- Изящный синтаксис

**Недостатки:**
- Меньше сообщества чем React
- UI библиотеки не развиты как в React

---

## 🏆 Выбранное решение: Next.js 15 + React 19

### Стек

| Компонент | Выбор | Версия | Причина |
|-----------|-------|--------|---------|
| Framework | **Next.js** | 15.5.6 | Server Components, встроенная оптимизация |
| Runtime | React | 19.1.0 | Новейшие hooks и features |
| Language | TypeScript | 5.9.3 | Type safety, лучший DX |
| Styling | Tailwind CSS | 4.1.14 | Utility-first, быстрая разработка |
| UI Components | shadcn/ui | latest | Customizable, accessible, no lock-in |
| Icons | Lucide React | (included) | Beautiful, consistent icons |
| Package Manager | pnpm | 10.18.1 | Быстро, экономно по диску |
| Build Tool | Turbopack | (integrated) | Быстрый dev/build |

---

## ✅ Justification по критериям

### 1. Производительность

**Turbopack (Next.js 15):**
```
Dev startup:      ~1.5s
Hot reload:       <100ms
Production build: ~3s for demo app
```

### 2. Type Safety

**TypeScript 5.9.3:**
- Strict mode по умолчанию
- Отличная интеграция с React 19
- Compiler performance улучшен в 5.x

### 3. Компоненты и Styling

**shadcn/ui + Tailwind CSS:**

Преимущества:
- Компоненты - это копируемый код (не node_modules)
- Полная кастомизация
- Темизация встроена (CSS переменные)
- Accessibility из коробки

### 4. API Integration

**Next.js API Routes:**
- Proxy для Mock API
- WebSocket для real-time (future)
- Middleware для CORS

### 5. Developer Experience

**Инструменты включены из коробки:**
- ESLint (с Next.js конфигом)
- TypeScript (strict mode)
- Hot reload (Turbopack)
- Testing (jest - optional)

### 6. Масштабируемость

**Архитектура готова к:**
- Множественным страницам (App Router)
- Сложным компонентам (Context API, TanStack Query, Zustand)
- Пользовательской аутентификации (NextAuth.js)
- Интеграции (API routes, webhooks)

---

## 💰 Cost Analysis

| Компонент | Стоимость | Примечание |
|-----------|-----------|-----------|
| Next.js | FREE | Open source |
| React | FREE | Open source |
| TypeScript | FREE | Open source |
| Tailwind CSS | FREE | Open source |
| shadcn/ui | FREE | Open source |
| pnpm | FREE | Open source |
| **Total** | **$0** | Полностью бесплатно |

**Хостинг (future):**
- Vercel: Free tier
- Self-hosted: ~$5-10/mo

---

## 🚀 Implementation Plan

### Phase 1: Setup (✅ Завершено - FS2)
- [x] Next.js инициализация
- [x] TypeScript конфигурация
- [x] Tailwind CSS setup
- [x] ESLint конфигурация
- [x] shadcn/ui инициализация

### Phase 2: Components (FS3)
- [ ] Dashboard компоненты
- [ ] Реusable UI components
- [ ] Layouts

### Phase 3: Features (FS4+)
- [ ] API интеграция
- [ ] State management
- [ ] Error handling

---

## 📊 Metrics to Track

```
Development Metrics:
- Build time (target: <5s)
- Dev server startup (target: <2s)
- Bundle size (target: <150kB gzipped)
- Lighthouse score (target: >90)

Runtime Metrics:
- First Contentful Paint: <1.5s
- Time to Interactive: <3.5s
- Core Web Vitals: passing
```

---

## ⚠️ Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Turbopack нестабилен | Medium | Fallback на webpack |
| React 19 новая | Low | Стабильна, production ready |
| shadcn/ui git-based | Low | Компоненты копируются |
| TypeScript learning curve | Low | Команда имеет опыт |

---

## 📚 Learning Resources

### Must Read
- [Next.js Docs](https://nextjs.org/docs)
- [React 19 Blog](https://react.dev/blog)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Components](https://ui.shadcn.com)

### Recommended
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Web Vitals Guide](https://web.dev/vitals/)

---

## ✅ Decision

**Status:** ✅ **APPROVED** for FS2 implementation

**Reasons:**
1. Next.js 15 обеспечивает best-in-class DX с Turbopack
2. React 19 дает современные features
3. TypeScript обеспечивает type safety
4. Tailwind + shadcn/ui оптимальна для быстрой разработки UI
5. pnpm экономит диск и дает правильный lock-file
6. Полностью бесплатный стек
7. Готово к масштабированию

---

## 📝 History

| Версия | Дата | Статус | Примечание |
|--------|------|--------|-----------|
| 1.0 | 2025-10-17 | Approved | Initial ADR for FS2 |

---

## 📎 Related Documents

- [Frontend Roadmap](frontend-roadmap.md)
- [Front Vision](front-vision.md)
- [API Requirements](api-requirements.md)
- [FS2 Sprint Plan](plans/s2-init-plan.md)
- [FS2 Completion Report](plans/fs2-completion-report.md)

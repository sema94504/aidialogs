# Спринт FS1: Mock API для дашборда статистики

## Цель
Создать Mock API для получения статистики по диалогам, определить функциональные требования к дашборду на основе референса shadcn dashboard-01, спроектировать контракт API и реализовать mock-реализацию с автоматической документацией.

## Контекст
- **Референс UI:** shadcn dashboard-01 (https://ui.shadcn.com/blocks#dashboard-01)
- **БД схема:** users (telegram_id), messages (user_id, role, content, length, created_at)
- **Стек backend:** Python 3.11+, FastAPI, Pydantic, uv
- **Архитектура:** Интерфейс StatCollector с двумя реализациями (Mock, Real)

## Функциональные требования к дашборду

На основе анализа существующей БД и референса dashboard-01:

### Ключевые метрики (карточки)
1. **Всего пользователей** - количество уникальных пользователей
2. **Всего сообщений** - общее количество сообщений
3. **Активных сегодня** - пользователи с сообщениями за последние 24ч
4. **Средняя длина сообщения** - средний размер сообщения пользователя

### График активности
- Количество сообщений по дням (последние 7 дней)
- По осям: дата / количество сообщений

### Таблица последних диалогов
- Последние 5-10 сообщений пользователей
- Колонки: telegram_id, роль (user/assistant), превью текста, дата

## API Контракт

### Endpoint: GET /api/stats
Единственный метод для получения всей статистики дашборда (KISS).

**Response Schema:**
```python
{
  "metrics": {
    "total_users": int,
    "total_messages": int,
    "active_today": int,
    "avg_message_length": float
  },
  "activity_chart": [
    {"date": "2025-10-17", "count": 42},
    ...
  ],
  "recent_messages": [
    {
      "telegram_id": int,
      "role": "user" | "assistant",
      "preview": str,  # первые 100 символов
      "created_at": str  # ISO format
    },
    ...
  ]
}
```

## Архитектура

### 1. Интерфейс StatCollector
`src/api/stat_collector.py` - протокол для реализаций:
```python
class StatCollector(Protocol):
    async def get_stats(self) -> DashboardStats: ...
```

### 2. Mock реализация
`src/api/mock_stat_collector.py` - генерация синтетических данных

### 3. API сервер
`src/api/main.py` - FastAPI приложение с единственным endpoint

### 4. Модели данных
`src/api/models.py` - Pydantic модели для request/response

## Структура файлов

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, endpoint /api/stats
│   ├── models.py               # Pydantic модели
│   ├── stat_collector.py       # Protocol интерфейс
│   └── mock_stat_collector.py  # Mock реализация
tests/
├── api/
│   ├── __init__.py
│   ├── test_models.py          # Тесты моделей
│   ├── test_mock_collector.py  # Тесты Mock реализации
│   └── test_api.py              # Тесты API endpoint
frontend/
└── doc/
    ├── api-requirements.md      # Требования к дашборду
    └── api-examples.md          # Примеры использования API
```

## Итерации

### Итерация 1: Требования и модели данных
- Создать `frontend/doc/api-requirements.md` с функциональными требованиями
- Создать `src/api/__init__.py`
- Создать `src/api/models.py` с Pydantic моделями
- Создать `tests/api/__init__.py`
- Создать `tests/api/test_models.py` - тесты для валидации моделей

### Итерация 2: Интерфейс StatCollector
- Создать `src/api/stat_collector.py` с Protocol
- Документация интерфейса (docstrings)

### Итерация 3: Mock реализация
- Создать `src/api/mock_stat_collector.py`
- Генерация реалистичных данных (random, без faker)
- Создать `tests/api/test_mock_collector.py` - тесты Mock реализации

### Итерация 4: FastAPI сервер
- Обновить `pyproject.toml` - добавить fastapi, uvicorn
- Создать `src/api/main.py` с FastAPI приложением
- Endpoint GET /api/stats с dependency injection
- Создать `tests/api/test_api.py` - тесты endpoint
- Автогенерация OpenAPI документации (/docs, /redoc)

### Итерация 5: Команды и примеры использования
- Добавить в `Makefile`: `run-api`, `test-api`
- Создать `frontend/doc/api-examples.md` с примерами запросов
- Финальное тестирование: запуск API, проверка /docs, curl тесты
- Запуск всех тестов: `make test`, проверка покрытия

### Итерация 6: Документация и финализация
- Обновить `frontend/doc/frontend-roadmap.md` - статус FS1: ✅ Завершен
- Добавить ссылку на план в таблицу спринтов
- Проверка всех критериев готовности

## Зависимости

Добавить в `pyproject.toml`:
```toml
dependencies = [
    # ... existing
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
]
```

## Критерии готовности

- ✅ Документ с требованиями к дашборду создан
- ✅ API контракт спроектирован и задокументирован
- ✅ Интерфейс StatCollector реализован
- ✅ Mock реализация работает и протестирована
- ✅ FastAPI сервер запускается и отдает корректные данные
- ✅ OpenAPI документация автоматически генерируется (доступна на /docs)
- ✅ Команды `make run-api` и `make test-api` работают
- ✅ Примеры запросов к API созданы в api-examples.md
- ✅ Frontend roadmap обновлен со ссылкой на план
- ✅ Покрытие тестами > 80%
- ✅ Все линтеры и typecheck проходят

## Команды

```bash
# Запуск API сервера
make run-api
# или
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Тестирование API
make test-api
# или
curl http://localhost:8000/api/stats

# OpenAPI документация
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/redoc      # ReDoc

# Запуск всех тестов
make test

# Проверка покрытия
make coverage
```

## Примечания

- Mock реализация генерирует случайные данные без внешних зависимостей
- API разрабатывается с учетом будущей замены Mock на Real реализацию
- Используется dependency injection для гибкости переключения реализаций
- Все endpoint асинхронные для соответствия архитектуре проекта


# Примеры использования Dashboard API

## Запуск API сервера

```bash
# Через Makefile
make run-api

# Напрямую через uvicorn
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Доступ к документации
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Примеры запросов

### 1. Получение статистики (curl)

```bash
# Базовый запрос
curl http://localhost:8000/api/stats

# С форматированием JSON
curl -s http://localhost:8000/api/stats | python -m json.tool

# Через Makefile
make test-api
```

### 2. Получение статистики (httpie)

```bash
# Установка httpie (опционально)
pip install httpie

# Запрос с автоматическим форматированием
http GET http://localhost:8000/api/stats
```

### 3. Получение статистики (Python)

```python
import httpx
import asyncio

async def get_stats():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/stats")
        return response.json()

# Запуск
stats = asyncio.run(get_stats())
print(f"Всего пользователей: {stats['metrics']['total_users']}")
print(f"Всего сообщений: {stats['metrics']['total_messages']}")
```

### 4. Получение статистики (JavaScript/TypeScript)

```javascript
// Fetch API
async function getStats() {
  const response = await fetch('http://localhost:8000/api/stats');
  const stats = await response.json();
  return stats;
}

// Использование
getStats().then(stats => {
  console.log('Метрики:', stats.metrics);
  console.log('График:', stats.activity_chart);
  console.log('Сообщения:', stats.recent_messages);
});
```

```typescript
// TypeScript с типизацией
interface Metrics {
  total_users: number;
  total_messages: number;
  active_today: number;
  avg_message_length: number;
}

interface ActivityPoint {
  date: string;
  count: number;
}

interface RecentMessage {
  telegram_id: number;
  role: 'user' | 'assistant';
  preview: string;
  created_at: string;
}

interface DashboardStats {
  metrics: Metrics;
  activity_chart: ActivityPoint[];
  recent_messages: RecentMessage[];
}

async function getStats(): Promise<DashboardStats> {
  const response = await fetch('http://localhost:8000/api/stats');
  return await response.json();
}
```

### 5. Health Check

```bash
# Проверка работоспособности API
curl http://localhost:8000/health

# Ответ: {"status":"ok"}
```

### 6. Root Endpoint

```bash
# Информация об API
curl http://localhost:8000/

# Ответ:
# {
#   "name": "AI Dialogs Dashboard API",
#   "version": "1.0.0",
#   "docs": "/docs",
#   "redoc": "/redoc"
# }
```

## Структура ответа

### GET /api/stats

```json
{
  "metrics": {
    "total_users": 142,
    "total_messages": 2456,
    "active_today": 12,
    "avg_message_length": 87.3
  },
  "activity_chart": [
    {
      "date": "2025-10-11",
      "count": 234
    },
    {
      "date": "2025-10-12",
      "count": 198
    },
    {
      "date": "2025-10-13",
      "count": 267
    },
    {
      "date": "2025-10-14",
      "count": 289
    },
    {
      "date": "2025-10-15",
      "count": 245
    },
    {
      "date": "2025-10-16",
      "count": 312
    },
    {
      "date": "2025-10-17",
      "count": 278
    }
  ],
  "recent_messages": [
    {
      "telegram_id": 123456789,
      "role": "user",
      "preview": "Как настроить систему?",
      "created_at": "2025-10-17T14:35:00Z"
    },
    {
      "telegram_id": 123456789,
      "role": "assistant",
      "preview": "Для настройки системы выполните следующие шаги: откройте конфигурацию...",
      "created_at": "2025-10-17T14:35:05Z"
    }
  ]
}
```

## Интеграция в Frontend

### React пример

```typescript
import React, { useEffect, useState } from 'react';

interface DashboardStats {
  metrics: {
    total_users: number;
    total_messages: number;
    active_today: number;
    avg_message_length: number;
  };
  activity_chart: { date: string; count: number }[];
  recent_messages: {
    telegram_id: number;
    role: string;
    preview: string;
    created_at: string;
  }[];
}

function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/stats')
      .then(response => response.json())
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching stats:', error);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!stats) return <div>No data</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <div className="metrics">
        <MetricCard title="Всего пользователей" value={stats.metrics.total_users} />
        <MetricCard title="Всего сообщений" value={stats.metrics.total_messages} />
        <MetricCard title="Активных сегодня" value={stats.metrics.active_today} />
        <MetricCard 
          title="Средняя длина" 
          value={stats.metrics.avg_message_length.toFixed(1)} 
        />
      </div>
      {/* Chart and Messages components */}
    </div>
  );
}
```

## Тестирование

```bash
# Запуск всех тестов API
make test

# Только API тесты
pytest tests/api/ -v

# С покрытием
pytest tests/api/ --cov=src/api --cov-report=term-missing
```

## Troubleshooting

### API не запускается

```bash
# Проверка порта
lsof -i :8000

# Запуск на другом порту
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001
```

### CORS ошибки в браузере

API уже настроен с CORS middleware, разрешающим все origins. Если возникают проблемы:

```python
# src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Конкретный origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Данные не обновляются

Mock API генерирует случайные данные при каждом запросе. Для фиксированных данных:

```python
# Использование seed для воспроизводимости
collector = MockStatCollector(seed=42)
```

## Полезные ссылки

- OpenAPI Spec: http://localhost:8000/openapi.json
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health


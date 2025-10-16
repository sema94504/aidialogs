<!-- 12085af5-331b-4032-9276-03b806ac2f82 7cee93f3-6e11-404e-bfba-4cf37842344c -->
# S1: Персистентное хранение данных

## Технологии

- SQLite + FTS5 (полнотекстовый поиск)
- aiosqlite (асинхронная работа с БД)
- Alembic (система миграций)

## Схема БД

**Таблица users:**

- id INTEGER PRIMARY KEY AUTOINCREMENT
- telegram_id INTEGER UNIQUE NOT NULL
- created_at TEXT NOT NULL
- deleted_at TEXT NULL

**Таблица messages:**

- id INTEGER PRIMARY KEY AUTOINCREMENT
- user_id INTEGER NOT NULL (FK -> users.id)
- role TEXT NOT NULL (user/assistant)
- content TEXT NOT NULL
- length INTEGER NOT NULL
- created_at TEXT NOT NULL
- deleted_at TEXT NULL
- INDEX idx_user_messages (user_id, deleted_at)

**FTS5 таблица messages_fts:**

- content TEXT (виртуальная таблица для поиска)

## Файловая структура

Новые файлы:

- `src/database.py` - DatabaseManager (подключение, выполнение запросов)
- `alembic/versions/001_initial_schema.py` - первая миграция
- `alembic.ini` - конфигурация Alembic
- `alembic/env.py` - Alembic environment

Изменяемые:

- `src/session_manager.py` - рефакторинг для работы с БД через DatabaseManager
- `src/config.py` - добавить database_path
- `src/bot.py` - инициализация DatabaseManager, передача в SessionManager
- `pyproject.toml` - добавить aiosqlite, alembic

## Реализация

### 1. Зависимости

```toml
dependencies = [
    "aiogram>=3.0.0",
    "openai>=1.0.0",
    "pydantic-settings>=2.0.0",
    "aiosqlite>=0.19.0",
    "alembic>=1.13.0",
]
```

### 2. DatabaseManager

```python
class DatabaseManager:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection = None
    
    async def connect(self) -> None
    async def close(self) -> None
    async def execute(self, query: str, params: tuple) -> None
    async def fetchone(self, query: str, params: tuple) -> dict | None
    async def fetchall(self, query: str, params: tuple) -> list[dict]
```

### 3. SessionManager с БД

Методы (интерфейс остается прежним):

- `get_session(user_id)` - выбирает messages WHERE user_id AND deleted_at IS NULL
- `add_message(user_id, role, content)` - INSERT с length=len(content), created_at=now()
- `clear_session(user_id)` - UPDATE messages SET deleted_at=now() WHERE user_id

### 4. Alembic миграция

Команды:

```bash
alembic init alembic
alembic revision -m "Initial schema"
alembic upgrade head
```

Миграция создает:

- Таблицы users, messages
- Индексы
- FTS5 виртуальную таблицу
- Триггеры для синхронизации FTS5

### 5. Config

```python
class Config(BaseSettings):
    ...
    database_path: str = "aidialogs.db"
```

### 6. Тесты

- `tests/test_database.py` - CRUD операции, подключение
- `tests/test_session_manager.py` - обновить для работы с БД (in-memory SQLite)
- `tests/test_integration.py` - проверка сохранения между "перезапусками"

### To-dos

- [ ] Итерация 1: Схема БД и инициализация (sql/init.sql, src/database.py, config)
- [ ] Итерация 2: Базовые операции (add_message, get_messages)
- [ ] Итерация 3: Soft delete (clear_session с is_deleted)
- [ ] Итерация 4: Полнотекстовый поиск (search_messages через FTS5)
- [ ] Итерация 5: Рефакторинг SessionManager для работы с Database
- [ ] Итерация 6: Интеграция в TelegramBot и main.py
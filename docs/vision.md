# Техническое видение

## 1. Технологии

**Основные:**
- Python 3.11+
- uv - управление зависимостями и виртуальным окружением
- aiogram 3.x - Telegram Bot API (polling)
- openai - клиент для работы с OpenAI-совместимым сервером (http://polen.keenetic.pro:3000/v1)
- python-dotenv или pydantic-settings - управление .env конфигом
- make - автоматизация команд

**Качество кода:**
- ruff - линтер и форматтер (заменяет black, isort, flake8)
- mypy - статическая проверка типов
- pytest - фреймворк тестирования
- pytest-cov - покрытие кода тестами
- pytest-asyncio - поддержка async тестов

## 2. Принципы разработки

- KISS (Keep It Simple, Stupid) - максимальная простота
- MVP подход - только необходимый функционал
- ООП: 1 класс = 1 файл
- Без абстракций и паттернов без необходимости
- Линейный код, прямые зависимости

## 3. Структура проекта

```
aidialogs/
├── .env                 # конфигурация
├── .gitignore
├── README.md
├── Makefile             # команды: format, lint, test, coverage
├── pyproject.toml       # uv config + ruff/mypy настройки
├── pytest.ini           # настройки pytest
├── docs/
│   ├── idea.md
│   ├── vision.md
│   ├── conventions.md
│   ├── tasklist.md
│   └── tasklist_tech_debt.md
├── src/
│   ├── __init__.py
│   ├── main.py          # точка входа
│   ├── bot.py           # TelegramBot
│   ├── llm_client.py    # LLMClient
│   ├── config.py        # Config
│   └── session_manager.py # SessionManager (после рефакторинга)
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_llm_client.py
    ├── test_bot.py
    ├── test_session_manager.py
    └── test_integration.py
```

Компоненты:
- `main.py` - запуск приложения
- `Bot` - обработка Telegram событий
- `LLMClient` - работа с LLM
- `Config` - загрузка конфига
- `SessionManager` - управление сессиями пользователей (SRP)

## 4. Архитектура

```
main.py -> Config -> Bot -> SessionManager
                      ↓
                  LLMClient -> OpenAI API
```

Поток работы:
1. `main.py` создает `Config`, `LLMClient`, `Bot`
2. `Bot` создает `SessionManager` для управления сессиями
3. `Bot` запускает polling
4. Пользователь отправляет сообщение
5. `Bot` получает сообщение, добавляет в `SessionManager`
6. `Bot` вызывает `LLMClient` с историей из `SessionManager`
7. `LLMClient` отправляет запрос в OpenAI API с системным промптом
8. `LLMClient` возвращает ответ
9. `Bot` сохраняет ответ в `SessionManager`
10. `Bot` отправляет ответ пользователю

**Принципы:**
- Разделение ответственностей (SRP)
- Зависимость от абстракций при необходимости (DIP)
- Простота и линейность кода (KISS)

## 5. Модель данных

Для MVP - никакой базы данных, все в памяти:

```python
# В SessionManager классе
class SessionManager:
    def __init__(self):
        self._sessions: dict[int, list[dict]] = {}
    
    def get_session(self, user_id: int) -> list[dict]:
        ...
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        ...
    
    def clear_session(self, user_id: int) -> None:
        ...
```

Структура сессии:
- Ключ: `user_id` (Telegram ID)
- Значение: список сообщений `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`

История диалога:
- Хранится только в памяти процесса
- При перезапуске - история теряется
- Без персистентности
- Управляется отдельным классом для соблюдения SRP

## 6. Работа с LLM

```python
# LLMClient
- base_url: http://polen.keenetic.pro:3000/v1
- api_key: не требуется
- model: из конфига (например, "gpt-oss:latest")
- system_prompt: из конфига
```

Метод:
```python
def get_response(self, messages: list[dict]) -> str:
    # Добавляем system prompt в начало
    # Отправляем через openai.ChatCompletion.create()
    # Возвращаем text ответа
```

## 7. Сценарии работы

1. **Старт бота**
   - Пользователь: `/start`
   - Бот: Приветственное сообщение

2. **Диалог**
   - Пользователь: любое текстовое сообщение
   - Бот: добавляет в историю, вызывает LLM, сохраняет ответ, отправляет пользователю

3. **Сброс контекста**
   - Пользователь: `/reset`
   - Бот: очищает историю диалога для этого пользователя

## 8. Конфигурирование

Только `.env` файл с переменными:

```env
TELEGRAM_BOT_TOKEN=<token>
LLM_BASE_URL=http://polen.keenetic.pro:3000/v1
LLM_MODEL=gpt-oss:latest
SYSTEM_PROMPT=Ты полезный ассистент.
```

`Config` класс:
- **Вариант 1:** Через `python-dotenv` + ручная валидация
- **Вариант 2:** Через `pydantic-settings` (упрощает валидацию, следует DRY)

```python
# С pydantic-settings (рекомендуется после рефакторинга)
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    telegram_bot_token: str
    llm_base_url: str
    llm_model: str
    system_prompt: str
    
    class Config:
        env_file = ".env"
```

## 9. Логгирование

Встроенный `logging`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
```

Логгируем:
- Старт/стоп бота
- Входящие сообщения (user_id, текст)
- Отправка в LLM
- Ошибки

Вывод в консоль и `bot.log`.

## 10. Тестирование

Автоматизированное тестирование с контролем качества:

**Инструменты:**
- pytest - фреймворк для тестов
- pytest-asyncio - поддержка async тестов
- pytest-cov - измерение покрытия кода

**Структура:**
```
tests/
├── test_config.py          # тесты Config
├── test_llm_client.py      # тесты LLMClient
├── test_bot.py             # тесты Bot
├── test_session_manager.py # тесты SessionManager
└── test_integration.py     # базовые интеграционные тесты
```

**Стандарты тестирования:**
- Покрытие кода >80%
- Тест на каждую публичную функцию/метод
- Тесты на edge cases и error handling
- Используй моки для внешних зависимостей
- Arrange-Act-Assert паттерн

**Что тестируем:**
- `Config` - валидация обязательных полей, корректная загрузка .env
- `LLMClient` - формирование запроса, обработка ответа, ошибки API (моки)
- `Bot` - обработка команд /start, /reset, текстовых сообщений, error handling (моки aiogram)
- `SessionManager` - создание сессий, добавление сообщений, очистка
- Интеграция - взаимодействие компонентов (базовые проверки)

**Что НЕ тестируем:**
- Реальные API вызовы
- E2E сценарии в Telegram
- UI/UX тестирование

**Запуск:**
```bash
make test       # все тесты
make coverage   # тесты + покрытие
```

## 11. Контроль качества кода

**Автоматизированные проверки:**

```bash
make format     # Ruff - форматирование кода
make lint       # Ruff - проверка стиля и ошибок
make typecheck  # Mypy - проверка типов
make test       # Pytest - запуск тестов
make coverage   # Pytest - покрытие кода
```

**Конфигурация в `pyproject.toml`:**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B"]  # Базовые правила
ignore = ["N802", "N803"]                 # Исключения

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

**Workflow перед коммитом:**
1. Пиши код
2. `make format` - отформатируй
3. `make lint` - проверь и исправь ошибки
4. `make typecheck` - проверь типы
5. `make coverage` - убедись в покрытии >80%
6. Коммит

**Принципы:**
- Zero warnings policy - исправляй все предупреждения
- Type hints везде - улучшает читаемость и предотвращает ошибки
- Покрытие >80% - критичный код должен быть протестирован
- Простота - инструменты не должны усложнять разработку

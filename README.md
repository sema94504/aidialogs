# AI Dialogs Bot

Telegram бот для диалогов с AI-ассистентом на основе OpenAI-совместимого API.

## Возможности

- 🤖 Диалоги с AI через OpenAI-совместимый API
- 💾 Сохранение истории диалога в памяти
- 🔄 Команда `/reset` для очистки истории
- 📝 Логирование всех событий в консоль и файл
- ✅ Покрытие тестами >80%
- 🛡️ Проверка типов и контроль качества кода

## Технологии

**Основные:**
- Python 3.11+
- aiogram 3.x (Telegram Bot API)
- openai (клиент для LLM API)
- pydantic-settings (управление конфигурацией)
- uv (управление зависимостями)

**Качество кода:**
- ruff - линтер и форматтер (заменяет black, isort, flake8)
- mypy - статическая проверка типов
- pytest - фреймворк тестирования
- pytest-cov - покрытие кода тестами
- pytest-asyncio - поддержка async тестов

## Установка

### 1. Установка uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Клонирование репозитория

```bash
git clone <repository-url>
cd aidialogs
```

### 3. Установка зависимостей

```bash
uv sync --extra dev
```

### 4. Конфигурация

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
LLM_BASE_URL=http://your-llm-server:3000/v1
LLM_MODEL=gpt-oss:latest
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
```

## Запуск

### Запуск бота

```bash
make run
```

или

```bash
uv run python -m src.main
```

### Остановка бота

Нажмите `Ctrl+C` для остановки бота.

## Использование

### Команды бота

- `/start` - Начать диалог, очистить историю
- `/reset` - Очистить историю текущего диалога

### Пример диалога

```
Пользователь: /start
Бот: Привет! Я AI-ассистент. Задай мне любой вопрос.

Пользователь: Как дела?
Бот: [ответ от LLM]

Пользователь: /reset
Бот: История диалога очищена. Начнём сначала!
```

## Качество кода

### Инструменты

Проект использует современные инструменты контроля качества:

- **Ruff** - быстрый линтер и форматтер (заменяет black, isort, flake8)
- **Mypy** - статическая проверка типов
- **pytest-cov** - измерение покрытия кода тестами

### Команды

```bash
# Форматирование кода
make format

# Проверка стиля
make lint

# Проверка типов
make typecheck

# Запуск тестов
make test

# Покрытие тестами
make coverage

# Очистка временных файлов
make clean
```

### Порядок проверки перед коммитом

```bash
make format     # 1. Отформатировать код
make lint       # 2. Проверить стиль
make typecheck  # 3. Проверить типы
make test       # 4. Запустить тесты
make coverage   # 5. Проверить покрытие
```

## Структура проекта

```
aidialogs/
├── src/
│   ├── main.py              # точка входа
│   ├── bot.py               # TelegramBot класс
│   ├── llm_client.py        # LLMClient класс
│   ├── config.py            # Config класс (pydantic-settings)
│   └── session_manager.py   # SessionManager класс
├── tests/
│   ├── test_bot.py              # тесты Bot
│   ├── test_llm_client.py       # тесты LLMClient
│   ├── test_config.py           # тесты Config
│   ├── test_session_manager.py  # тесты SessionManager
│   └── test_integration.py      # интеграционные тесты
├── docs/
│   ├── idea.md              # описание идеи
│   ├── vision.md            # техническое видение
│   └── archive/             # завершенные документы
├── .cursor/rules/
│   ├── conventions.mdc      # соглашения по коду
│   └── workflow.mdc         # процесс разработки
├── .env                     # конфигурация (не в git)
├── .env.example             # пример конфигурации
├── Makefile                 # команды для запуска
├── pyproject.toml           # зависимости и настройки
└── pytest.ini               # настройки pytest
```

## Архитектура

```
main.py -> Config -> Bot -> SessionManager
                  -> Bot -> LLMClient -> OpenAI API
```

### Поток обработки сообщения

1. Пользователь отправляет сообщение
2. `TelegramBot` получает сообщение через aiogram
3. `SessionManager` добавляет сообщение в историю пользователя
4. `TelegramBot` вызывает `LLMClient.get_response()` с историей
5. `LLMClient` добавляет system prompt и отправляет в API
6. Ответ сохраняется в историю через `SessionManager`
7. `TelegramBot` отправляет ответ пользователю

### Компоненты

- **Config** - управление конфигурацией через pydantic-settings
- **TelegramBot** - обработка команд и сообщений
- **SessionManager** - управление историей диалогов пользователей
- **LLMClient** - взаимодействие с LLM API

## Тестирование

### Структура тестов

```
tests/
├── test_config.py          # валидация конфигурации
├── test_llm_client.py      # формирование запросов к LLM
├── test_bot.py             # обработка команд и сообщений
├── test_session_manager.py # управление сессиями
└── test_integration.py     # базовая интеграция компонентов
```

### Стандарты тестирования

- Покрытие кода >80%
- Тест на каждую публичную функцию/метод
- Тестирование error handling и edge cases
- Моки для внешних зависимостей (Telegram API, LLM API)
- AAA паттерн (Arrange-Act-Assert)

### Запуск тестов

```bash
# Все тесты
make test

# С покрытием
make coverage

# Конкретный файл
uv run pytest tests/test_bot.py -v

# Конкретный тест
uv run pytest tests/test_bot.py::test_start_handler -v
```

### Покрытие тестами

Текущее покрытие: **>80%**

HTML отчет покрытия генерируется в `htmlcov/index.html` после запуска `make coverage`.

## Логирование

Логи пишутся в:
- Консоль (stdout)
- Файл `bot.log`

Формат логов:
```
2025-10-11 12:00:00 - bot - INFO - Команда /start от пользователя 123456
2025-10-11 12:00:05 - bot - INFO - Сообщение от пользователя 123456: Привет
2025-10-11 12:00:05 - bot - INFO - Отправка запроса в LLM для пользователя 123456
2025-10-11 12:00:08 - bot - INFO - Получен ответ от LLM для пользователя 123456
```

Логируются события:
- Старт/стоп бота
- Входящие команды и сообщения (user_id, текст)
- Отправка запросов в LLM
- Получение ответов от LLM
- Ошибки с подробным контекстом

## Хранение данных

- История диалогов управляется через `SessionManager`
- Хранение в памяти процесса: `dict[int, list[dict]]`
- При перезапуске бота история теряется
- Для MVP не используется база данных

## Разработка

### Принципы

- **KISS** (Keep It Simple, Stupid) - максимальная простота
- **MVP** подход - только необходимый функционал
- **SOLID** принципы: SRP, DIP
- **DRY** (Don't Repeat Yourself) - не дублируй код
- **1 класс = 1 файл** - строго
- **Типизация везде** - type hints для всех функций
- **Самодокументируемый код** - без docstrings

### Стиль кода

- Длина строки: 100 символов
- Python 3.11+ синтаксис: `list[dict]`, `dict[int, str]`
- PascalCase для классов: `TelegramBot`, `SessionManager`
- snake_case для функций: `get_response`, `add_message`
- Приватные методы: `_start_handler`, `_validate`

### Workflow

1. Прочитай итерацию из tasklist
2. Предложи решение
3. Получи согласование
4. Реализуй с проверкой качества
5. Запусти тесты
6. Обнови tasklist
7. Сделай коммит

Подробнее: `.cursor/rules/workflow.mdc`

## Лицензия

MIT

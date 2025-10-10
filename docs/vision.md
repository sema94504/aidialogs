# Техническое видение

## 1. Технологии

- Python 3.11+
- uv - управление зависимостями и виртуальным окружением
- aiogram 3.x - Telegram Bot API (polling)
- openai - клиент для работы с OpenAI-совместимым сервером (http://polen.keenetic.pro:3000/v1)
- python-dotenv - управление .env конфигом
- pytest - тестирование
- make - автоматизация команд

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
├── Makefile
├── pyproject.toml       # uv config
├── docs/
│   ├── idea.md
│   ├── vision.md
│   └── conventions.md
├── src/
│   ├── main.py          # точка входа
│   ├── bot.py           # TelegramBot
│   ├── llm_client.py    # LLMClient
│   └── config.py        # Config
└── tests/
    ├── test_config.py
    ├── test_llm_client.py
    └── test_bot.py
```

Компоненты:
- `main.py` - запуск приложения
- `Bot` - обработка Telegram событий
- `LLMClient` - работа с LLM
- `Config` - загрузка конфига

## 4. Архитектура

```
main.py -> Config -> Bot -> LLMClient -> OpenAI API
```

Поток работы:
1. `main.py` создает `Config`, `LLMClient`, `Bot`
2. `Bot` запускает polling
3. Пользователь отправляет сообщение
4. `Bot` получает сообщение, вызывает `LLMClient`
5. `LLMClient` отправляет запрос в OpenAI API с системным промптом
6. `LLMClient` возвращает ответ
7. `Bot` отправляет ответ пользователю

## 5. Модель данных

Для MVP - никакой базы данных, все в памяти:

```python
# В Bot классе
user_sessions = {}  # dict[int, list[dict]]
```

Структура:
- Ключ: `user_id` (Telegram ID)
- Значение: список сообщений `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`

История диалога:
- Хранится только в памяти процесса
- При перезапуске - история теряется
- Без персистентности

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
- Загружает через `python-dotenv`
- Валидирует обязательные поля
- Предоставляет атрибуты

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

Минимальное тестирование для MVP:

**Инструменты:**
- pytest - фреймворк для тестов

**Структура:**
```
tests/
├── test_config.py      # тесты Config
├── test_llm_client.py  # тесты LLMClient
└── test_bot.py         # тесты Bot
```

**Что тестируем:**
- `Config` - валидация обязательных полей, корректная загрузка .env
- `LLMClient` - формирование запроса, обработка ответа (моки API)
- `Bot` - обработка команд /start, /reset, текстовых сообщений (моки aiogram)

**Что НЕ тестируем:**
- Интеграции с реальными API
- E2E сценарии
- Покрытие кода

**Запуск:**
- `make test` - запуск всех тестов


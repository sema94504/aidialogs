# Getting Started

Быстрый старт AI Dialogs Bot за 5 минут.

## Предварительные требования

- Python 3.11+
- uv (менеджер зависимостей)
- Telegram Bot Token
- Доступ к OpenAI-совместимому API

## 1. Установка uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Клонирование репозитория

```bash
git clone <repository-url>
cd aidialogs
```

## 3. Установка зависимостей

```bash
uv sync --extra dev
```

Устанавливает:
- Основные: aiogram, openai, pydantic-settings
- Dev: pytest, ruff, mypy

## 4. Конфигурация

Создайте `.env` файл в корне проекта:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
LLM_BASE_URL=http://your-llm-server:3000/v1
LLM_MODEL=gpt-oss:latest
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
```

**Получить Telegram Bot Token:**
1. Откройте [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

## 5. Запуск бота

```bash
make run
```

Или напрямую:

```bash
uv run python -m src.main
```

## 6. Проверка работы

Откройте бота в Telegram:

1. **Старт диалога:**
   ```
   Вы: /start
   Бот: Привет! Я AI-ассистент. Задай мне любой вопрос.
   ```

2. **Отправка сообщения:**
   ```
   Вы: Привет!
   Бот: [ответ от LLM согласно роли]
   ```

3. **Просмотр роли:**
   ```
   Вы: /role
   Бот: [содержимое системного промпта]
   ```

4. **Сброс истории:**
   ```
   Вы: /reset
   Бот: История диалога очищена. Начнём сначала!
   ```

## 7. Остановка бота

Нажмите `Ctrl+C` в терминале.

## Что дальше?

- [Архитектура](architecture.md) - понять устройство проекта
- [Конфигурация](configuration.md) - детали настройки
- [Разработка](development.md) - начать разработку
- [Тестирование](testing.md) - запустить тесты

## Troubleshooting

**Ошибка: `TELEGRAM_BOT_TOKEN not found`**
- Проверьте `.env` файл в корне проекта
- Убедитесь что переменная называется именно `TELEGRAM_BOT_TOKEN`

**Ошибка: `FileNotFoundError: prompts/system_prompt.txt`**
- Убедитесь что файл существует
- Проверьте путь в `.env`: `SYSTEM_PROMPT_FILE`

**Бот не отвечает:**
- Проверьте доступность LLM API: `curl http://your-llm-server:3000/v1/models`
- Проверьте логи в `bot.log`

**Проверка установки:**
```bash
# Тесты
make test

# Все инструменты качества
make format && make lint && make typecheck && make test
```



# Конфигурация

Управление конфигурацией AI Dialogs Bot.

## Обзор

Конфигурация через `.env` файл с валидацией через pydantic-settings.

## Файл .env

Создайте `.env` в корне проекта:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEFghIJKlmNOPQRstuVWXyz
LLM_BASE_URL=http://polen.keenetic.pro:3000/v1
LLM_MODEL=gpt-oss:latest
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
```

**Важно:** `.env` в `.gitignore` и никогда не коммитится.

## Переменные окружения

### TELEGRAM_BOT_TOKEN (обязательно)

**Назначение:** Токен Telegram бота.

**Получение:**
1. Откройте [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot`
3. Выберите имя и username
4. Скопируйте токен

**Формат:** `123456:ABC-DEF...` (около 45 символов)

**Пример:**
```env
TELEGRAM_BOT_TOKEN=5424172488:AAHmN8yKCXLqj9O0IQV8RZtV8P5cT3tS1eQ
```

### LLM_BASE_URL (обязательно)

**Назначение:** Адрес OpenAI-совместимого API сервера.

**Формат:** `http://host:port/v1`

**Примеры:**
```env
# Локальный сервер
LLM_BASE_URL=http://localhost:3000/v1

# Удаленный сервер
LLM_BASE_URL=http://polen.keenetic.pro:3000/v1

# OpenAI (настоящий)
LLM_BASE_URL=https://api.openai.com/v1
```

**Проверка доступности:**
```bash
curl http://your-server:3000/v1/models
```

### LLM_MODEL (обязательно)

**Назначение:** Название модели для генерации ответов.

**Формат:** зависит от сервера.

**Примеры:**
```env
# Локальная модель
LLM_MODEL=gpt-oss:latest

# OpenAI модель
LLM_MODEL=gpt-4

# Другая модель
LLM_MODEL=llama-2-7b
```

**Проверка доступных моделей:**
```bash
curl http://your-server:3000/v1/models
```

### SYSTEM_PROMPT_FILE (опционально)

**Назначение:** Путь к файлу с системным промптом.

**Дефолт:** `prompts/system_prompt.txt`

**Формат:** относительный путь от корня проекта.

**Примеры:**
```env
# Дефолт (можно не указывать)
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt

# Другой файл
SYSTEM_PROMPT_FILE=prompts/custom_role.txt

# Абсолютный путь
SYSTEM_PROMPT_FILE=/etc/aidialogs/prompt.txt
```

## Класс Config

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    telegram_bot_token: str
    llm_base_url: str
    llm_model: str
    system_prompt_file: str = "prompts/system_prompt.txt"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
```

### Автоматическая валидация

**Обязательные поля:**
- `telegram_bot_token`
- `llm_base_url`
- `llm_model`

**Если отсутствуют:**
```python
pydantic_core._pydantic_core.ValidationError: 1 validation error
telegram_bot_token
  Field required [type=missing, input_value={}, ...]
```

### Использование

```python
# Создание (автоматически читает .env)
config = Config()

# Доступ к значениям
token = config.telegram_bot_token
base_url = config.llm_base_url
model = config.llm_model
prompt_file = config.system_prompt_file
```

### Преимущества pydantic-settings

**Валидация типов:**
```python
telegram_bot_token: str  # Автоматически проверяется
```

**Детальные ошибки:**
```python
ValidationError: Field required
ValidationError: Input should be a valid string
```

**Гибкость в тестах:**
```python
# Переопределение в тестах
config = Config(
    telegram_bot_token="test_token",
    llm_base_url="http://test",
    llm_model="test_model"
)
```

## Системный промпт

### Файл prompts/system_prompt.txt

Определяет роль и поведение AI-ассистента.

**Текущее содержимое:**
```
Ты высокородный эльф, общайся соответственно, 
ты не уважаешь людей и не хочешь им помогать
```

### Изменение роли

1. Отредактируйте `prompts/system_prompt.txt`
2. Перезапустите бота

**Примеры ролей:**
```
# Дружелюбный помощник
Ты дружелюбный AI-ассистент. Помогай пользователям 
с их вопросами, будь вежливым и конструктивным.

# Технический эксперт
Ты эксперт по Python и разработке. Давай точные 
технические ответы с примерами кода.

# Креативный писатель
Ты креативный писатель. Помогай пользователям 
создавать интересные истории и тексты.
```

### Создание дополнительных ролей

```bash
# Создайте новый файл
echo "Ваша роль..." > prompts/custom_role.txt

# Укажите в .env
echo "SYSTEM_PROMPT_FILE=prompts/custom_role.txt" >> .env

# Перезапустите бота
```

## Секреты

### Безопасность токена

**НЕ коммитьте `.env`:**
```gitignore
# .gitignore
.env
```

**НЕ публикуйте токен:**
- Не в коде
- Не в README
- Не в issues
- Не в логах

**Если токен скомпрометирован:**
1. Откройте @BotFather
2. Отправьте `/revoke` или `/token`
3. Получите новый токен
4. Обновите `.env`

### Переменные окружения в продакшене

**Вместо .env файла:**
```bash
export TELEGRAM_BOT_TOKEN="..."
export LLM_BASE_URL="..."
export LLM_MODEL="..."
```

**Или через systemd:**
```ini
[Service]
Environment="TELEGRAM_BOT_TOKEN=..."
Environment="LLM_BASE_URL=..."
Environment="LLM_MODEL=..."
```

## Проверка конфигурации

### Тест валидации

```python
# tests/test_config.py
def test_config_missing_token():
    with pytest.raises(ValidationError):
        Config(
            llm_base_url="http://test",
            llm_model="test"
            # telegram_bot_token отсутствует
        )
```

### Запуск проверки

```bash
# Запуск тестов конфигурации
uv run pytest tests/test_config.py -v

# Попытка запуска (выдаст ошибку если что-то не так)
make run
```

## Примеры конфигураций

### Разработка (локально)

```env
TELEGRAM_BOT_TOKEN=your_dev_bot_token
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
```

### Продакшн

```env
TELEGRAM_BOT_TOKEN=your_prod_bot_token
LLM_BASE_URL=http://production-server:3000/v1
LLM_MODEL=gpt-oss:latest
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
```

### Тестирование OpenAI API

```env
TELEGRAM_BOT_TOKEN=your_bot_token
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
SYSTEM_PROMPT_FILE=prompts/system_prompt.txt
```

**Важно:** для настоящего OpenAI нужен API ключ:
```python
client = OpenAI(
    base_url=config.llm_base_url,
    api_key=config.openai_api_key  # Добавить в Config
)
```

## Следующие шаги

- [Разработка](development.md) - процесс разработки
- [Тестирование](testing.md) - тестирование конфигурации
- [Troubleshooting](troubleshooting.md) - решение проблем


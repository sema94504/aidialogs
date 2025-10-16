# Troubleshooting

Решение типичных проблем AI Dialogs Bot.

## Проблемы запуска

### Ошибка: TELEGRAM_BOT_TOKEN not found

```
pydantic_core._pydantic_core.ValidationError: 1 validation error
telegram_bot_token
  Field required
```

**Причина:** Отсутствует `.env` файл или переменная не задана.

**Решение:**
```bash
# Создайте .env файл
echo "TELEGRAM_BOT_TOKEN=your_token" > .env
echo "LLM_BASE_URL=http://localhost:3000/v1" >> .env
echo "LLM_MODEL=gpt-oss:latest" >> .env

# Проверьте содержимое
cat .env
```

### Ошибка: FileNotFoundError: prompts/system_prompt.txt

```
FileNotFoundError: [Errno 2] No such file or directory: 'prompts/system_prompt.txt'
```

**Причина:** Отсутствует файл системного промпта.

**Решение:**
```bash
# Создайте директорию
mkdir -p prompts

# Создайте файл промпта
echo "Ты дружелюбный AI-ассистент" > prompts/system_prompt.txt

# Или укажите другой файл в .env
echo "SYSTEM_PROMPT_FILE=prompts/my_prompt.txt" >> .env
```

### Ошибка: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'aiogram'
```

**Причина:** Зависимости не установлены.

**Решение:**
```bash
# Установка зависимостей
uv sync --extra dev

# Проверка
uv run python -c "import aiogram; print('OK')"
```

## Проблемы работы бота

### Бот не отвечает на сообщения

**Проверка 1: Бот запущен?**
```bash
ps aux | grep "src.main"
```

Если нет:
```bash
make run
```

**Проверка 2: Токен правильный?**
```bash
# Проверьте токен через API
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Должно вернуть JSON с информацией о боте
```

Если ошибка 401:
```bash
# Обновите токен в .env
# Получите новый токен в @BotFather
```

**Проверка 3: Есть ошибки в логах?**
```bash
tail -f bot.log
```

### Ошибка: LLM API недоступен

```
ERROR - Ошибка LLM API: Connection refused
```

**Причина:** LLM сервер не запущен или неправильный URL.

**Решение:**
```bash
# Проверьте доступность сервера
curl http://your-server:3000/v1/models

# Если недоступен, проверьте LLM_BASE_URL в .env
cat .env | grep LLM_BASE_URL

# Убедитесь что сервер запущен
# Для ollama:
ollama serve

# Для других серверов - смотрите их документацию
```

### Бот отвечает "Извините, произошла ошибка"

**Причина:** Ошибка при обращении к LLM API.

**Диагностика:**
```bash
# Смотрите логи
tail -n 50 bot.log | grep ERROR

# Проверьте API вручную
curl -X POST http://your-server:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:latest",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

**Возможные причины:**
- Модель не существует (проверьте LLM_MODEL)
- Таймаут (сервер медленный)
- Неверный формат запроса

### Бот "забывает" контекст после перезапуска

**Это не баг, а особенность.**

**Причина:** История хранится в памяти процесса.

**Решение:** Это MVP ограничение. История теряется при перезапуске.

Для сохранения контекста нужна база данных (будущая фича).

## Проблемы тестирования

### Тест падает: FileNotFoundError в test_llm_client

```
FileNotFoundError: prompts/system_prompt.txt
```

**Причина:** Тест ожидает реальный файл.

**Решение:** Используется `tmp_path` фикстура:
```python
def test_llm_client(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Тест")
    client = LLMClient("http://test", "test", str(prompt_file))
```

### Тест падает: asyncio event loop closed

```
RuntimeError: Event loop is closed
```

**Причина:** Неправильная настройка async тестов.

**Решение:** Проверьте `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

Используйте `@pytest.mark.asyncio`:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
```

### Покрытие ниже ожидаемого

```
TOTAL      121      15    88%
```

**Диагностика:**
```bash
# Смотрите детальный отчет
make coverage

# Откройте HTML отчет
open htmlcov/index.html
```

**Решение:**
- Добавьте тесты для непокрытого кода
- Или игнорируйте тривиальный код (это нормально для >80%)

## Проблемы качества кода

### Ruff lint: ошибки импортов

```
F401 [*] `logging` imported but unused
I001 [*] Import block is un-sorted or un-formatted
```

**Решение:**
```bash
# Автоматическое исправление
make format

# Проверка
make lint
```

### Mypy: ошибки типизации

```
error: Incompatible return value type (got "None", expected "str")
```

**Решение:**
```python
# ❌ Плохо
def get_response(self, messages: list[dict]) -> str:
    content = response.choices[0].message.content
    return content  # может быть None

# ✅ Хорошо
def get_response(self, messages: list[dict]) -> str:
    content = response.choices[0].message.content
    return content if content is not None else ""
```

### Длина строки >100 символов

```
E501 Line too long (120 > 100)
```

**Решение:**
```python
# ❌ Плохо (120 символов)
logger.error(f"Ошибка при получении ответа LLM для пользователя {user_id} с сообщением {text}: {e}")

# ✅ Хорошо (разбить на строки)
logger.error(
    f"Ошибка при получении ответа LLM для пользователя {user_id}: {e}"
)
```

## Проблемы с uv

### uv команда не найдена

```
bash: uv: command not found
```

**Решение:**
```bash
# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Добавьте в PATH (если нужно)
export PATH="$HOME/.local/bin:$PATH"

# Проверка
uv --version
```

### uv sync не работает

```
error: Failed to download dependencies
```

**Решение:**
```bash
# Очистка кэша
rm -rf .venv uv.lock

# Переустановка
uv sync --extra dev

# Если проблема с сетью, проверьте прокси
# export HTTP_PROXY=http://proxy:port
```

## Проблемы в продакшене

### Высокое потребление памяти

**Причина:** История диалогов растет бесконечно для каждого пользователя.

**Решение:**
```bash
# Временно: перезапуск бота (история очищается)
sudo systemctl restart aidialogs

# Долгосрочно: пользователи делают /reset
# Или ограничение длины истории (будущая фича)
```

### Логи растут слишком быстро

**Решение:** Настройте logrotate (см. [Deployment](deployment.md)).

```bash
# Ручная очистка
> bot.log

# Или удаление старых логов
find . -name "bot.log.*" -mtime +7 -delete
```

### Бот падает при большой нагрузке

**Причина:** Polling режим - однопоточный.

**Решение:**
- Для MVP это нормально
- Для высокой нагрузки: webhook + несколько инстансов (будущее)

## Отладка

### Включение debug логирования

```python
# src/main.py
logging.basicConfig(
    level=logging.DEBUG,  # Вместо INFO
    ...
)
```

**Внимание:** Много вывода, только для отладки.

### Добавление временного логирования

```python
# В любом месте
logger.debug(f"Переменная x = {x}")
logger.debug(f"Состояние sessions: {self._sessions}")
```

### Запуск с выводом в консоль

```python
# Отключить запись в файл временно
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Только консоль
)
```

## Получение помощи

### Проверка версий

```bash
# Python
python --version  # Должен быть 3.11+

# uv
uv --version

# Зависимости
uv pip list

# Git
git --version
```

### Сбор информации для отчета

```bash
# Версия Python
python --version

# Версия зависимостей
uv pip list | grep -E "aiogram|openai|pydantic"

# Последние строки логов
tail -n 50 bot.log

# Переменные окружения (без секретов!)
echo "LLM_BASE_URL: $LLM_BASE_URL"
echo "LLM_MODEL: $LLM_MODEL"
```

### Ошибки в tests

```bash
# Запуск с полным выводом
uv run pytest tests/ -v -s

# Конкретный упавший тест
uv run pytest tests/test_bot.py::test_start_command -v -s

# С отладкой
uv run pytest tests/ --pdb
```

## Частые вопросы (FAQ)

**Q: История теряется при перезапуске?**
A: Да, это MVP ограничение. История в памяти, без БД.

**Q: Можно ли использовать OpenAI вместо локального LLM?**
A: Да, укажите `LLM_BASE_URL=https://api.openai.com/v1` и добавьте API ключ.

**Q: Как изменить роль бота?**
A: Отредактируйте `prompts/system_prompt.txt` и перезапустите бота.

**Q: Бот медленно отвечает?**
A: Проверьте скорость LLM сервера. Возможно нужна более мощная модель или железо.

**Q: Можно ли запустить несколько ботов?**
A: Да, с разными токенами и `.env` файлами в разных директориях.

**Q: Как ограничить длину истории?**
A: Пока никак (MVP). Пользователи могут делать `/reset`.

## Следующие шаги

- [Getting Started](getting-started.md) - если нужно переустановить
- [Configuration](configuration.md) - настройка конфигурации
- [Development](development.md) - процесс разработки
- [Deployment](deployment.md) - деплой в продакшен


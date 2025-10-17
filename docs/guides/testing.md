# Тестирование

Стандарты и практики тестирования AI Dialogs Bot.

## Обзор

Проект использует TDD подход с целевым покрытием >80%.

**Текущее состояние:**
- 28 тестов
- 98% покрытие кода
- Все тесты проходят

## Структура тестов

```
tests/
├── test_config.py          # Config валидация
├── test_session_manager.py # SessionManager
├── test_llm_client.py      # LLMClient
├── test_bot.py             # TelegramBot
├── test_main.py            # main.py точка входа
└── test_integration.py     # Базовая интеграция
```

**Принцип:** 1 тестовый файл на 1 модуль.

## Запуск тестов

```bash
# Все тесты
make test

# С покрытием
make coverage

# Конкретный файл
uv run pytest tests/test_bot.py -v

# Конкретный тест
uv run pytest tests/test_bot.py::test_start_command -v

# С выводом print
uv run pytest tests/test_bot.py -v -s
```

## AAA паттерн

Arrange-Act-Assert для структуры тестов.

```python
def test_add_message():
    # Arrange - подготовка
    manager = SessionManager()
    
    # Act - действие
    manager.add_message(123, "user", "Привет")
    
    # Assert - проверка
    assert manager.get_session(123)[0] == {
        "role": "user", 
        "content": "Привет"
    }
```

## Что тестируем

### Публичные методы

```python
# ✅ Тестируем
def get_session(self, user_id: int) -> list[dict]:
def add_message(self, user_id: int, role: str, content: str):

# ❌ НЕ тестируем приватные напрямую
def _read_prompt_file(self, file_path: str):
```

### Валидация данных

```python
def test_config_missing_token():
    with pytest.raises(ValidationError):
        Config(
            llm_base_url="http://test",
            llm_model="test"
            # telegram_bot_token отсутствует -> ошибка
        )
```

### Error handling

```python
def test_llm_client_file_not_found():
    with pytest.raises(FileNotFoundError):
        LLMClient(
            base_url="http://test",
            model="test",
            system_prompt_file="non_existent.txt"
        )
```

### Edge cases

```python
def test_message_handler_no_text(bot):
    message = MagicMock()
    message.text = None  # Edge case
    message.from_user = None
    
    await bot._message_handler(message)
    # Ничего не должно упасть
```

## Что НЕ тестируем

### Тривиальный код

```python
# ❌ Бессмысленный тест
def test_session_manager_init():
    manager = SessionManager()
    assert manager is not None

# ❌ Геттер без логики
def test_get_token():
    config = Config(...)
    assert config.telegram_bot_token == "token"
```

### Реальные API

Используй моки вместо реальных вызовов.

```python
# ❌ Реальный API в тестах
def test_real_openai():
    client = OpenAI(base_url="https://api.openai.com/v1")
    response = client.chat.completions.create(...)  # $$$

# ✅ Моки
def test_get_response():
    with patch.object(client.chat.completions, "create") as mock:
        mock.return_value = mock_response
        result = llm_client.get_response(messages)
```

## Примеры тестов

### test_config.py

```python
def test_config_valid():
    config = Config(
        telegram_bot_token="test_token",
        llm_base_url="http://test",
        llm_model="test_model"
    )
    assert config.telegram_bot_token == "test_token"
    assert config.system_prompt_file == "prompts/system_prompt.txt"

def test_config_missing_token():
    with pytest.raises(ValidationError):
        Config(llm_base_url="http://test", llm_model="test")
```

### test_session_manager.py

```python
def test_get_session_creates_new():
    manager = SessionManager()
    session = manager.get_session(123)
    assert session == []

def test_add_message():
    manager = SessionManager()
    manager.add_message(123, "user", "Привет")
    assert manager.get_session(123)[0] == {
        "role": "user",
        "content": "Привет"
    }

def test_clear_session():
    manager = SessionManager()
    manager.add_message(123, "user", "Привет")
    manager.clear_session(123)
    assert manager.get_session(123) == []
```

### test_llm_client.py

```python
def test_get_response(tmp_path):
    # Arrange
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Ты ассистент")
    
    client = LLMClient(
        base_url="http://test",
        model="test",
        system_prompt_file=str(prompt_file)
    )
    
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Ответ"
    
    # Act
    with patch.object(client.client.chat.completions, "create") as mock:
        mock.return_value = mock_response
        result = client.get_response([{"role": "user", "content": "Привет"}])
    
    # Assert
    assert result == "Ответ"
    mock.assert_called_once()
```

### test_bot.py

```python
@pytest.mark.asyncio
async def test_start_command(bot):
    # Arrange
    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()
    
    # Act
    await bot._start_handler(message)
    
    # Assert
    message.answer.assert_called_once()
    assert "Привет" in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_message_handler(bot):
    message = MagicMock()
    message.from_user.id = 123
    message.text = "Привет"
    message.answer = AsyncMock()
    
    bot.llm_client.get_response.return_value = "Здравствуй"
    
    await bot._message_handler(message)
    
    bot.llm_client.get_response.assert_called_once()
    message.answer.assert_called_once_with("Здравствуй")
```

## Фикстуры

Переиспользуемая подготовка для тестов.

```python
@pytest.fixture
def llm_client(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Ты эльф")
    return MagicMock(
        spec=LLMClient,
        system_prompt="Ты эльф"
    )

@pytest.fixture
def bot(llm_client):
    return TelegramBot("test_token", llm_client, "prompts/system_prompt.txt")

# Использование
def test_start_command(bot):
    # bot уже готов к использованию
    ...
```

## Моки

### MagicMock для sync кода

```python
from unittest.mock import MagicMock

llm_client = MagicMock(spec=LLMClient)
llm_client.get_response.return_value = "Ответ"
```

### AsyncMock для async кода

```python
from unittest.mock import AsyncMock

message.answer = AsyncMock()
await message.answer("Текст")
message.answer.assert_called_once_with("Текст")
```

### patch для временной подмены

```python
from unittest.mock import patch

with patch.object(client.chat.completions, "create") as mock:
    mock.return_value = mock_response
    result = llm_client.get_response(messages)
```

## Async тесты

Используй `@pytest.mark.asyncio` для async функций.

```python
@pytest.mark.asyncio
async def test_start_command(bot):
    message = MagicMock()
    message.answer = AsyncMock()
    await bot._start_handler(message)
    message.answer.assert_called_once()
```

**Настройка (pytest.ini):**
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

## Покрытие кода

### Запуск

```bash
make coverage
```

**Вывод:**
```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
src/bot.py                  57      1    98%   73
src/config.py                7      0   100%
src/llm_client.py           24      0   100%
src/main.py                 21      1    95%   37
src/session_manager.py      12      0   100%
------------------------------------------------------
TOTAL                      121      2    98%
```

### HTML отчет

Генерируется в `htmlcov/index.html`:

```bash
make coverage
# Открой htmlcov/index.html в браузере
```

### Целевое покрытие

**>80%** для критичного кода.

**100% НЕ обязательно:**
- Тривиальный код можно пропустить
- Некоторые edge cases не покрываются

## Именование тестов

**Формат:** `test_<что_тестируется>_<сценарий>`

```python
# ✅ Хорошо
def test_get_response()
def test_get_response_error()
def test_message_handler_with_history()
def test_config_missing_token()

# ❌ Плохо
def test_should_return_response()
def test_check_error_handling()
def test_1()
def test_everything()
```

## Проверка assertions

```python
# Точные проверки
assert result == "expected"
assert len(session) == 2

# Вхождение
assert "Привет" in response

# Типы
assert isinstance(config, Config)

# Исключения
with pytest.raises(ValidationError):
    Config()

# Вызовы моков
mock.assert_called_once()
mock.assert_called_once_with(123, "user", "text")
mock.assert_not_called()
```

## Временные файлы

Используй `tmp_path` фикстуру pytest.

```python
def test_read_prompt(tmp_path):
    # Создание временного файла
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Тест")
    
    # Использование
    client = LLMClient(
        base_url="http://test",
        model="test",
        system_prompt_file=str(prompt_file)
    )
    
    assert client.system_prompt == "Тест"
    # tmp_path автоматически удаляется после теста
```

## Интеграционные тесты

Базовая проверка взаимодействия компонентов.

```python
def test_full_integration(tmp_path):
    # Arrange
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Ты эльф")
    
    llm_client = MagicMock(spec=LLMClient)
    llm_client.system_prompt = "Ты эльф"
    llm_client.get_response.return_value = "Не твоё дело, смертный"
    
    bot = TelegramBot("token", llm_client, str(prompt_file))
    
    message = MagicMock()
    message.from_user.id = 123
    message.text = "Привет"
    message.answer = AsyncMock()
    
    # Act
    await bot._message_handler(message)
    
    # Assert
    session = bot.session_manager.get_session(123)
    assert len(session) == 2
    assert session[0]["role"] == "user"
    assert session[1]["role"] == "assistant"
    message.answer.assert_called_once()
```

## Перед коммитом

**Обязательно:**
```bash
# Все тесты зеленые
make test

# Покрытие >80%
make coverage
```

## Добавление нового теста

### 1. Определи что тестировать

```python
# Новый метод в SessionManager
def get_message_count(self, user_id: int) -> int:
    return len(self.get_session(user_id))
```

### 2. Напиши тест (RED)

```python
def test_get_message_count():
    manager = SessionManager()
    manager.add_message(123, "user", "1")
    manager.add_message(123, "assistant", "2")
    assert manager.get_message_count(123) == 2
```

### 3. Реализуй метод (GREEN)

```python
def get_message_count(self, user_id: int) -> int:
    return len(self.get_session(user_id))
```

### 4. Запусти тесты

```bash
make test  # ✅ Все зеленые
```

## Следующие шаги

- [Разработка](development.md) - TDD workflow
- [Deployment](deployment.md) - подготовка к продакшену
- [Troubleshooting](troubleshooting.md) - отладка тестов



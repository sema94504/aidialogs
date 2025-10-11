# План устранения технического долга

## 📊 Прогресс

| Итерация | Компонент | Статус | Дата | Заметки |
|----------|-----------|--------|------|---------|
| 1 | Инструменты качества | ✅ Готово | 2025-10-11 | Ruff, pytest-cov, Makefile |
| 2 | Тестирование | ✅ Готово | 2025-10-11 | Error handling, integration |
| 3 | SessionManager | ✅ Готово | 2025-10-11 | Рефакторинг Bot |
| 4 | Type Safety | ✅ Готово | 2025-10-11 | Mypy, type hints |
| 5 | Pydantic Config | ✅ Готово | 2025-10-11 | Упрощение Config |

**Легенда:** ⏳ Ожидание | 🔄 В работе | ✅ Готово | ❌ Ошибка

---

## Итерации

### Итерация 1: Инструменты качества кода

**Цель:** Добавить автоматизированные инструменты контроля качества.

**Задачи:**
- [x] Добавить Ruff в `pyproject.toml` (линтер + форматтер)
  ```toml
  [project.optional-dependencies]
  dev = [
      "pytest>=7.0.0",
      "pytest-asyncio>=0.21.0",
      "pytest-cov>=4.0.0",
      "ruff>=0.1.0",
  ]
  
  [tool.ruff]
  line-length = 100
  target-version = "py311"
  
  [tool.ruff.lint]
  select = ["E", "F", "I", "N", "W", "B"]
  ignore = ["N802", "N803"]
  ```

- [x] Добавить pytest-cov в зависимости (см. выше)

- [x] Обновить `Makefile` с новыми командами:
  ```makefile
  .PHONY: lint format test coverage clean
  
  lint:
  	uv run ruff check src/ tests/
  
  format:
  	uv run ruff format src/ tests/
  
  test:
  	uv run pytest tests/ -v
  
  coverage:
  	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
  
  clean:
  	rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
  	rm -rf htmlcov .coverage
  	rm -f bot.log
  ```

- [x] Обновить `pytest.ini`:
  ```ini
  [pytest]
  pythonpath = .
  testpaths = tests
  addopts = --cov=src --cov-report=term-missing:skip-covered
  ```

- [x] Запустить `make format` для форматирования кода
- [x] Запустить `make lint` для проверки кода

**Проверка vision.md:**
- ✓ Соответствует KISS - стандартные, простые инструменты
- ✓ Минимум зависимостей - только необходимые dev-инструменты
- ✓ Не усложняет архитектуру

**Тест:** Выполнить `make lint`, `make format`, `make coverage` - все команды работают без ошибок.

---

### Итерация 2: Расширение тестирования

**Цель:** Добавить недостающие тесты для критических сценариев.

**Задачи:**
- [x] Добавить тест error handling в `tests/test_bot.py`:
  ```python
  @pytest.mark.asyncio
  async def test_message_handler_llm_error(bot, llm_client):
      llm_client.get_response.side_effect = Exception("LLM Error")
      
      message = MagicMock()
      message.from_user.id = 123
      message.text = 'Тест'
      message.answer = AsyncMock()
      
      await bot._message_handler(message)
      
      message.answer.assert_called_once_with("Извините, произошла ошибка. Попробуйте позже.")
  ```

- [x] Добавить тест для message без текста в `tests/test_bot.py`:
  ```python
  @pytest.mark.asyncio
  async def test_message_handler_no_text(bot, llm_client):
      message = MagicMock()
      message.from_user.id = 123
      message.text = None
      message.answer = AsyncMock()
      
      await bot._message_handler(message)
      
      message.answer.assert_not_called()
      llm_client.get_response.assert_not_called()
  ```

- [x] Создать `tests/test_integration.py`:
  ```python
  import pytest
  from unittest.mock import patch, MagicMock
  from src.config import Config
  from src.llm_client import LLMClient
  from src.bot import TelegramBot
  
  def test_full_integration():
      env_vars = {
          'TELEGRAM_BOT_TOKEN': 'test_token',
          'LLM_BASE_URL': 'http://test.api/v1',
          'LLM_MODEL': 'test-model',
          'SYSTEM_PROMPT': 'Test prompt'
      }
      
      with patch('src.config.load_dotenv'), patch.dict('os.environ', env_vars):
          config = Config()
          llm_client = LLMClient(
              base_url=config.llm_base_url,
              model=config.llm_model,
              system_prompt=config.system_prompt
          )
          
          with patch('src.bot.Bot'):
              bot = TelegramBot(config.telegram_bot_token, llm_client)
              
              assert bot.llm_client == llm_client
              assert bot.user_sessions == {}
  ```

- [x] Запустить `make coverage` - проверить покрытие >80%

**Проверка vision.md:**
- ✓ Минимальное тестирование - только критические сценарии
- ✓ Моки для внешних зависимостей
- ✓ Без E2E тестов (соответствует vision.md)

**Тест:** Выполнить `make test` - все тесты проходят. Выполнить `make coverage` - покрытие >80%.

---

### Итерация 3: Рефакторинг SessionManager (SOLID: SRP)

**Цель:** Вынести управление сессиями в отдельный класс.

**Задачи:**
- [x] Создать `src/session_manager.py`:
  ```python
  class SessionManager:
      def __init__(self):
          self._sessions: dict[int, list[dict]] = {}
      
      def get_session(self, user_id: int) -> list[dict]:
          if user_id not in self._sessions:
              self._sessions[user_id] = []
          return self._sessions[user_id]
      
      def add_message(self, user_id: int, role: str, content: str) -> None:
          session = self.get_session(user_id)
          session.append({"role": role, "content": content})
      
      def clear_session(self, user_id: int) -> None:
          self._sessions[user_id] = []
  ```

- [x] Обновить `src/bot.py` - заменить `self.user_sessions` на `self.session_manager`:
  - В `__init__`: `self.session_manager = SessionManager()`
  - В `_start_handler`: `self.session_manager.clear_session(user_id)`
  - В `_reset_handler`: `self.session_manager.clear_session(user_id)`
  - В `_message_handler`: использовать `add_message()` и `get_session()`

- [x] Создать `tests/test_session_manager.py`:
  ```python
  import pytest
  from src.session_manager import SessionManager
  
  def test_get_session_creates_new():
      manager = SessionManager()
      session = manager.get_session(123)
      assert session == []
  
  def test_add_message():
      manager = SessionManager()
      manager.add_message(123, "user", "Привет")
      session = manager.get_session(123)
      assert len(session) == 1
      assert session[0] == {"role": "user", "content": "Привет"}
  
  def test_clear_session():
      manager = SessionManager()
      manager.add_message(123, "user", "Привет")
      manager.clear_session(123)
      assert manager.get_session(123) == []
  ```

- [x] Обновить `tests/test_bot.py` - заменить проверки `bot.user_sessions` на `bot.session_manager`

- [x] Запустить `make test` - все тесты проходят

**Проверка vision.md:**
- ✓ 1 класс = 1 файл (SessionManager в session_manager.py)
- ✓ Линейный код, прямые зависимости
- ✓ Без абстракций без необходимости (конкретный класс, не интерфейс)

**Тест:** Выполнить `make test` - все тесты проходят. Бот работает корректно.

---

### Итерация 4: Type Safety с Mypy

**Цель:** Добавить статическую типизацию для предотвращения ошибок.

**Задачи:**
- [x] Добавить mypy в `pyproject.toml`:
  ```toml
  [project.optional-dependencies]
  dev = [
      "pytest>=7.0.0",
      "pytest-asyncio>=0.21.0",
      "pytest-cov>=4.0.0",
      "ruff>=0.1.0",
      "mypy>=1.0.0",
  ]
  
  [tool.mypy]
  python_version = "3.11"
  warn_return_any = true
  warn_unused_configs = true
  disallow_untyped_defs = false
  ```

- [x] Обновить `Makefile` - добавить команду typecheck:
  ```makefile
  typecheck:
  	uv run mypy src/
  ```

- [x] Убрать try/except хак с импортами в `src/bot.py`:
  ```python
  # Было:
  try:
      from .llm_client import LLMClient
  except ImportError:
      from llm_client import LLMClient
  
  # Стало:
  from .llm_client import LLMClient
  ```

- [x] Добавить type hints в `src/bot.py` (если отсутствуют):
  - Уже есть: `user_sessions: dict[int, list[dict]]`
  - Проверить все методы

- [x] Добавить type hints в `src/llm_client.py` (если отсутствуют):
  - Уже есть в сигнатурах

- [x] Запустить `make typecheck` - исправить ошибки типов

**Проверка vision.md:**
- ✓ Не усложняет код - type hints опциональны в Python
- ✓ Улучшает читаемость
- ⚠️ Проверить: не стало ли сложнее для понимания

**Тест:** Выполнить `make typecheck` - mypy не находит ошибок. Выполнить `make test` - тесты проходят.

---

### Итерация 5: Упрощение Config через Pydantic

**Цель:** Упростить Config, убрать повторяющуюся валидацию.

**Задачи:**
- [x] Добавить pydantic-settings в `pyproject.toml`:
  ```toml
  [project]
  dependencies = [
      "aiogram>=3.0.0",
      "python-dotenv>=1.0.0",
      "openai>=1.0.0",
      "pydantic-settings>=2.0.0",
  ]
  ```

- [x] Переписать `src/config.py`:
  ```python
  from pydantic_settings import BaseSettings
  
  class Config(BaseSettings):
      telegram_bot_token: str
      llm_base_url: str
      llm_model: str
      system_prompt: str
      
      class Config:
          env_file = ".env"
  ```

- [x] Обновить `tests/test_config.py`:
  ```python
  import pytest
  from pydantic import ValidationError
  from src.config import Config
  
  def test_config_missing_token():
      with pytest.raises(ValidationError):
          Config(_env_file=None, telegram_bot_token=None)
  
  def test_config_valid():
      config = Config(
          _env_file=None,
          telegram_bot_token='test_token',
          llm_base_url='http://test.api/v1',
          llm_model='test-model',
          system_prompt='Test prompt'
      )
      assert config.telegram_bot_token == 'test_token'
      assert config.llm_base_url == 'http://test.api/v1'
  ```

- [x] Запустить `make test` - все тесты проходят

**Проверка vision.md:**
- ✓ Линейный код - pydantic декларативный
- ✓ Убрана повторяющаяся валидация (DRY)
- ⚠️ Проверить: добавляется зависимость, но упрощается код

**Тест:** Выполнить `make test` - тесты проходят. Бот запускается корректно с .env файлом.

---

## Финальная проверка

После завершения всех итераций:

- [ ] `make format` - код отформатирован
- [ ] `make lint` - нет ошибок линтера
- [ ] `make typecheck` - нет ошибок типизации
- [ ] `make test` - все тесты проходят
- [ ] `make coverage` - покрытие >80%
- [ ] Бот работает в Telegram
- [ ] Все принципы из `vision.md` соблюдены:
  - [ ] KISS - код остался простым
  - [ ] MVP подход - не добавлено лишнего
  - [ ] 1 класс = 1 файл
  - [ ] Линейный код, прямые зависимости
  - [ ] Без абстракций без необходимости

## Исключения

**Не включено в план:**
- ❌ Pre-commit hooks - запускаем через Make вручную
- ❌ Protocol для LLMClient - оверинжиниринг для MVP
- ❌ Сложные паттерны проектирования
- ❌ Избыточная абстракция


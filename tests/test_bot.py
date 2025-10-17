import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from src.bot import TelegramBot
from src.database import DatabaseManager
from src.llm_client import LLMClient

TEST_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest.fixture
def llm_client():
    return MagicMock(spec=LLMClient)


@pytest_asyncio.fixture
async def db():
    db_manager = DatabaseManager(":memory:")
    await db_manager.connect()

    await db_manager.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            deleted_at TEXT NULL
        )
    """)

    await db_manager.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            length INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            deleted_at TEXT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    yield db_manager
    await db_manager.close()


@pytest_asyncio.fixture
async def bot(llm_client, db):
    with patch("src.bot.Bot"):
        return TelegramBot(
            "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            llm_client,
            "prompts/system_prompt.txt",
            db,
        )


@pytest.mark.asyncio
async def test_start_command(bot):
    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()

    await bot._start_handler(message)

    session = await bot.session_manager.get_session(123)
    assert session == []
    message.answer.assert_called_once_with("Привет! Я AI-ассистент. Задай мне любой вопрос.")


@pytest.mark.asyncio
async def test_message_handler(bot, llm_client):
    llm_client.get_response.return_value = "Это ответ от LLM"

    message = MagicMock()
    message.from_user.id = 123
    message.text = "Привет, как дела?"
    message.photo = None
    message.answer = AsyncMock()

    await bot._message_handler(message)

    session = await bot.session_manager.get_session(123)
    assert len(session) == 2
    assert session[0] == {"role": "user", "content": "Привет, как дела?"}
    assert session[1] == {"role": "assistant", "content": "Это ответ от LLM"}

    llm_client.get_response.assert_called_once()
    message.answer.assert_called_once_with("Это ответ от LLM")


@pytest.mark.asyncio
async def test_message_handler_with_history(bot, llm_client):
    await bot.session_manager.add_message(123, "user", "Первое сообщение")
    await bot.session_manager.add_message(123, "assistant", "Первый ответ")

    def check_history(messages):
        assert len(messages) == 3
        assert messages[0] == {"role": "user", "content": "Первое сообщение"}
        assert messages[1] == {"role": "assistant", "content": "Первый ответ"}
        assert messages[2] == {"role": "user", "content": "Второе сообщение"}
        return "Второй ответ"

    llm_client.get_response.side_effect = check_history

    message = MagicMock()
    message.from_user.id = 123
    message.text = "Второе сообщение"
    message.photo = None
    message.answer = AsyncMock()

    await bot._message_handler(message)

    session = await bot.session_manager.get_session(123)
    assert len(session) == 4
    llm_client.get_response.assert_called_once()


@pytest.mark.asyncio
async def test_reset_command(bot):
    await bot.session_manager.add_message(123, "user", "Старое сообщение")
    await bot.session_manager.add_message(123, "assistant", "Старый ответ")

    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()

    await bot._reset_handler(message)

    session = await bot.session_manager.get_session(123)
    assert session == []
    message.answer.assert_called_once_with("История диалога очищена. Начнём сначала!")


@pytest.mark.asyncio
async def test_message_handler_llm_error(bot, llm_client):
    llm_client.get_response.side_effect = Exception("LLM Error")

    message = MagicMock()
    message.from_user.id = 123
    message.text = "Тест"
    message.photo = None
    message.answer = AsyncMock()

    await bot._message_handler(message)

    message.answer.assert_called_once_with("Извините, произошла ошибка. Попробуйте позже.")


@pytest.mark.asyncio
async def test_message_handler_no_text(bot, llm_client):
    message = MagicMock()
    message.from_user.id = 123
    message.text = None
    message.photo = None
    message.answer = AsyncMock()

    await bot._message_handler(message)

    message.answer.assert_not_called()
    llm_client.get_response.assert_not_called()


@pytest.mark.asyncio
async def test_role_command(bot, llm_client):
    llm_client.system_prompt = "Я специализированный ассистент."

    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()

    await bot._role_handler(message)

    message.answer.assert_called_once_with("Я специализированный ассистент.")


@pytest.mark.asyncio
async def test_start_handler_no_user(bot):
    message = MagicMock()
    message.from_user = None
    message.answer = AsyncMock()

    await bot._start_handler(message)

    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_reset_handler_no_user(bot):
    message = MagicMock()
    message.from_user = None
    message.answer = AsyncMock()

    await bot._reset_handler(message)

    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_role_handler_no_user(bot):
    message = MagicMock()
    message.from_user = None
    message.answer = AsyncMock()

    await bot._role_handler(message)

    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_message_handler_with_photo(bot, llm_client):
    import base64

    llm_client.get_response.return_value = "На фото видна красная точка"

    message = MagicMock()
    message.from_user.id = 123
    message.text = None
    message.caption = "Что на этой картинке?"
    message.answer = AsyncMock()

    photo = MagicMock()
    photo.file_id = "test_file_id"
    message.photo = [photo]

    file_mock = MagicMock()
    file_mock.file_path = "photos/test.jpg"

    image_bytes = base64.b64decode(TEST_IMAGE_BASE64)
    download_mock = io.BytesIO(image_bytes)

    bot.bot.get_file = AsyncMock(return_value=file_mock)
    bot.bot.download_file = AsyncMock(return_value=download_mock)

    await bot._message_handler(message)

    session = await bot.session_manager.get_session(123)
    assert len(session) == 2
    assert session[0]["role"] == "user"
    assert isinstance(session[0]["content"], list)
    assert session[0]["content"][0] == {"type": "text", "text": "Что на этой картинке?"}

    bot.bot.get_file.assert_called_once_with("test_file_id")
    bot.bot.download_file.assert_called_once_with("photos/test.jpg")
    message.answer.assert_called_once_with("На фото видна красная точка")


@pytest.mark.asyncio
async def test_message_handler_with_photo_no_caption(bot, llm_client):
    import base64

    llm_client.get_response.return_value = "Я вижу изображение"

    message = MagicMock()
    message.from_user.id = 123
    message.text = None
    message.caption = None
    message.answer = AsyncMock()

    photo = MagicMock()
    photo.file_id = "test_file_id"
    message.photo = [photo]

    file_mock = MagicMock()
    file_mock.file_path = "photos/test.jpg"

    image_bytes = base64.b64decode(TEST_IMAGE_BASE64)
    download_mock = io.BytesIO(image_bytes)

    bot.bot.get_file = AsyncMock(return_value=file_mock)
    bot.bot.download_file = AsyncMock(return_value=download_mock)

    await bot._message_handler(message)

    session = await bot.session_manager.get_session(123)
    assert len(session) == 2
    assert session[0]["role"] == "user"
    assert isinstance(session[0]["content"], list)
    assert len(session[0]["content"]) == 1
    assert session[0]["content"][0]["type"] == "image_url"

    message.answer.assert_called_once_with("Я вижу изображение")


@pytest.mark.asyncio
async def test_message_handler_photo_with_multiple_sizes(bot, llm_client):
    import base64

    llm_client.get_response.return_value = "Описание фото"

    message = MagicMock()
    message.from_user.id = 123
    message.text = None
    message.caption = "Опиши"
    message.answer = AsyncMock()

    photo_small = MagicMock()
    photo_small.file_id = "small_id"
    photo_large = MagicMock()
    photo_large.file_id = "large_id"
    message.photo = [photo_small, photo_large]

    file_mock = MagicMock()
    file_mock.file_path = "photos/large.jpg"

    image_bytes = base64.b64decode(TEST_IMAGE_BASE64)
    download_mock = io.BytesIO(image_bytes)

    bot.bot.get_file = AsyncMock(return_value=file_mock)
    bot.bot.download_file = AsyncMock(return_value=download_mock)

    await bot._message_handler(message)

    bot.bot.get_file.assert_called_once_with("large_id")
    message.answer.assert_called_once_with("Описание фото")

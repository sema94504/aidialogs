import base64
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot import TelegramBot
from src.config import Config
from src.database import DatabaseManager
from src.llm_client import LLMClient

TEST_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest.mark.asyncio
async def test_full_integration(tmp_path):
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("Test prompt")

    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file=str(prompt_file),
    )
    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt_file=config.system_prompt_file,
    )

    db = DatabaseManager(":memory:")
    await db.connect()

    await db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            deleted_at TEXT NULL
        )
    """)

    await db.execute("""
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

    with patch("src.bot.Bot"):
        bot = TelegramBot(config.telegram_bot_token, llm_client, config.system_prompt_file, db)

        assert bot.llm_client == llm_client
        session = await bot.session_manager.get_session(999)
        assert session == []

    await db.close()


@pytest.mark.asyncio
async def test_smoke_initialization(tmp_path):
    prompt_file = tmp_path / "smoke_prompt.txt"
    prompt_file.write_text("Ты smoke test ассистент.")

    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file=str(prompt_file),
    )

    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt_file=config.system_prompt_file,
    )
    assert llm_client.system_prompt == "Ты smoke test ассистент."

    db = DatabaseManager(":memory:")
    await db.connect()

    await db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            deleted_at TEXT NULL
        )
    """)

    await db.execute("""
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

    with patch("src.bot.Bot"):
        bot = TelegramBot(config.telegram_bot_token, llm_client, config.system_prompt_file, db)

        assert bot.llm_client is not None
        assert bot.session_manager is not None
        assert bot.system_prompt_file == str(prompt_file)

    await db.close()


def test_smoke_prompt_file_not_found():
    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file="nonexistent.txt",
    )

    with pytest.raises(FileNotFoundError):
        LLMClient(
            base_url=config.llm_base_url,
            model=config.llm_model,
            system_prompt_file=config.system_prompt_file,
        )


@pytest.mark.asyncio
async def test_integration_with_image(tmp_path):
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("Ты ассистент для анализа изображений")

    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file=str(prompt_file),
    )
    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt_file=config.system_prompt_file,
    )

    db = DatabaseManager(":memory:")
    await db.connect()

    await db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            deleted_at TEXT NULL
        )
    """)

    await db.execute("""
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

    with patch("src.bot.Bot"), patch.object(llm_client, "get_response") as mock_response:
        mock_response.return_value = "На изображении красная точка"

        bot = TelegramBot(config.telegram_bot_token, llm_client, config.system_prompt_file, db)

        message = MagicMock()
        message.from_user.id = 555
        message.text = None
        message.caption = "Что на картинке?"
        message.photo = None
        message.answer = AsyncMock()

        photo = MagicMock()
        photo.file_id = "test_photo_id"
        message.photo = [photo]

        file_mock = MagicMock()
        file_mock.file_path = "photos/test.jpg"

        image_bytes = base64.b64decode(TEST_IMAGE_BASE64)
        download_mock = io.BytesIO(image_bytes)

        bot.bot.get_file = AsyncMock(return_value=file_mock)
        bot.bot.download_file = AsyncMock(return_value=download_mock)

        await bot._message_handler(message)

        session = await bot.session_manager.get_session(555)
        assert len(session) == 2
        assert session[0]["role"] == "user"
        assert isinstance(session[0]["content"], list)
        assert session[0]["content"][0] == {"type": "text", "text": "Что на картинке?"}
        assert session[0]["content"][1]["type"] == "image_url"
        assert session[1]["role"] == "assistant"
        assert session[1]["content"] == "На изображении красная точка"

        mock_response.assert_called_once()
        message.answer.assert_called_once_with("На изображении красная точка")

    await db.close()

import pytest
import pytest_asyncio

from src.database import DatabaseManager
from src.session_manager import SessionManager

TEST_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


@pytest_asyncio.fixture
async def manager():
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

    session_manager = SessionManager(db)
    yield session_manager
    await db.close()


@pytest.mark.asyncio
async def test_get_session_creates_new(manager):
    session = await manager.get_session(123)
    assert session == []


@pytest.mark.asyncio
async def test_add_message(manager):
    await manager.add_message(123, "user", "Привет")
    session = await manager.get_session(123)
    assert len(session) == 1
    assert session[0] == {"role": "user", "content": "Привет"}


@pytest.mark.asyncio
async def test_add_multiple_messages(manager):
    await manager.add_message(123, "user", "Привет")
    await manager.add_message(123, "assistant", "Здравствуйте")
    session = await manager.get_session(123)
    assert len(session) == 2
    assert session[0] == {"role": "user", "content": "Привет"}
    assert session[1] == {"role": "assistant", "content": "Здравствуйте"}


@pytest.mark.asyncio
async def test_clear_session(manager):
    await manager.add_message(123, "user", "Привет")
    await manager.clear_session(123)
    session = await manager.get_session(123)
    assert session == []


@pytest.mark.asyncio
async def test_multiple_users(manager):
    await manager.add_message(123, "user", "Сообщение 1")
    await manager.add_message(456, "user", "Сообщение 2")

    session_123 = await manager.get_session(123)
    session_456 = await manager.get_session(456)

    assert len(session_123) == 1
    assert len(session_456) == 1
    assert session_123[0]["content"] == "Сообщение 1"
    assert session_456[0]["content"] == "Сообщение 2"


@pytest.mark.asyncio
async def test_add_message_with_image(manager):
    await manager.add_message(123, "user", "Что на картинке?", TEST_IMAGE_BASE64)
    session = await manager.get_session(123)

    assert len(session) == 1
    assert session[0]["role"] == "user"
    assert isinstance(session[0]["content"], list)
    assert len(session[0]["content"]) == 2
    assert session[0]["content"][0] == {"type": "text", "text": "Что на картинке?"}
    assert session[0]["content"][1]["type"] == "image_url"
    expected_url = f"data:image/jpeg;base64,{TEST_IMAGE_BASE64}"
    assert session[0]["content"][1]["image_url"]["url"] == expected_url


@pytest.mark.asyncio
async def test_add_message_with_image_no_text(manager):
    await manager.add_message(123, "user", "", TEST_IMAGE_BASE64)
    session = await manager.get_session(123)

    assert len(session) == 1
    assert session[0]["role"] == "user"
    assert isinstance(session[0]["content"], list)
    assert len(session[0]["content"]) == 1
    assert session[0]["content"][0]["type"] == "image_url"
    expected_url = f"data:image/jpeg;base64,{TEST_IMAGE_BASE64}"
    assert session[0]["content"][0]["image_url"]["url"] == expected_url


@pytest.mark.asyncio
async def test_mixed_text_and_image_messages(manager):
    await manager.add_message(123, "user", "Текст")
    await manager.add_message(123, "assistant", "Ответ")
    await manager.add_message(123, "user", "Опиши фото", TEST_IMAGE_BASE64)

    session = await manager.get_session(123)

    assert len(session) == 3
    assert session[0]["content"] == "Текст"
    assert session[1]["content"] == "Ответ"
    assert isinstance(session[2]["content"], list)

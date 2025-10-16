import pytest
import pytest_asyncio

from src.database import DatabaseManager


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


@pytest.mark.asyncio
async def test_connect_and_close():
    db = DatabaseManager(":memory:")
    await db.connect()
    assert db.connection is not None
    await db.close()
    assert db.connection is None


@pytest.mark.asyncio
async def test_get_or_create_user_creates_new(db):
    user_id = await db.get_or_create_user(123)
    assert isinstance(user_id, int)
    assert user_id > 0


@pytest.mark.asyncio
async def test_get_or_create_user_returns_existing(db):
    user_id_1 = await db.get_or_create_user(123)
    user_id_2 = await db.get_or_create_user(123)
    assert user_id_1 == user_id_2


@pytest.mark.asyncio
async def test_add_message(db):
    user_id = await db.get_or_create_user(123)
    await db.add_message(user_id, "user", "Test message")
    messages = await db.get_messages(user_id)
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test message"


@pytest.mark.asyncio
async def test_get_messages_empty(db):
    user_id = await db.get_or_create_user(123)
    messages = await db.get_messages(user_id)
    assert messages == []


@pytest.mark.asyncio
async def test_clear_messages(db):
    user_id = await db.get_or_create_user(123)
    await db.add_message(user_id, "user", "Message 1")
    await db.add_message(user_id, "assistant", "Message 2")

    messages = await db.get_messages(user_id)
    assert len(messages) == 2

    await db.clear_messages(user_id)
    messages = await db.get_messages(user_id)
    assert messages == []


@pytest.mark.asyncio
async def test_multiple_users(db):
    user_id_1 = await db.get_or_create_user(123)
    user_id_2 = await db.get_or_create_user(456)

    await db.add_message(user_id_1, "user", "User 1 message")
    await db.add_message(user_id_2, "user", "User 2 message")

    messages_1 = await db.get_messages(user_id_1)
    messages_2 = await db.get_messages(user_id_2)

    assert len(messages_1) == 1
    assert len(messages_2) == 1
    assert messages_1[0]["content"] == "User 1 message"
    assert messages_2[0]["content"] == "User 2 message"


@pytest.mark.asyncio
async def test_message_length_stored(db):
    user_id = await db.get_or_create_user(123)
    content = "Test message"
    await db.add_message(user_id, "user", content)

    cursor = await db.connection.execute(
        "SELECT length FROM messages WHERE user_id = ?", (user_id,)
    )
    row = await cursor.fetchone()
    assert row[0] == len(content)

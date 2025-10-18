"""Тесты для RealStatCollector."""

from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from src.api.real_stat_collector import RealStatCollector
from src.database import DatabaseManager


@pytest_asyncio.fixture
async def db():
    """Тестовая БД в памяти."""
    db_manager = DatabaseManager(":memory:")
    await db_manager.connect()

    # Создаем схему
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
async def collector(db):
    """Экземпляр RealStatCollector."""
    return RealStatCollector(db)


@pytest.mark.asyncio
async def test_empty_database(collector):
    """Тест с пустой БД."""
    stats = await collector.get_stats(days=7)

    assert stats.metrics.total_users == 0
    assert stats.metrics.total_messages == 0
    assert stats.metrics.active_today == 0
    assert stats.metrics.avg_message_length == 0.0
    assert len(stats.activity_chart) == 0
    assert len(stats.chart_data) == 0
    assert len(stats.recent_messages) == 0


@pytest.mark.asyncio
async def test_single_user_single_message(db, collector):
    """Тест с одним пользователем и одним сообщением."""
    now = datetime.utcnow().isoformat()

    # Создаем пользователя
    await db.execute(
        "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
        (123456, now),
    )

    # Создаем сообщение
    await db.execute(
        "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
        (1, "user", "Hello world", 11, now),
    )

    stats = await collector.get_stats(days=7)

    assert stats.metrics.total_users == 1
    assert stats.metrics.total_messages == 1
    assert stats.metrics.active_today == 1
    assert stats.metrics.avg_message_length == 11.0
    assert len(stats.recent_messages) == 1
    assert stats.recent_messages[0].telegram_id == 123456
    assert stats.recent_messages[0].role == "user"
    assert stats.recent_messages[0].preview == "Hello world"


@pytest.mark.asyncio
async def test_multiple_users_and_messages(db, collector):
    """Тест с несколькими пользователями и сообщениями."""
    now = datetime.utcnow()

    # Создаем пользователей
    for i in range(3):
        await db.execute(
            "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
            (100000 + i, now.isoformat()),
        )

    # Создаем сообщения разных дней
    for day_offset in range(3):
        date = (now - timedelta(days=day_offset)).isoformat()
        for user_id in range(1, 4):
            await db.execute(
                "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, "user", f"Message {day_offset}", 10, date),
            )

    stats = await collector.get_stats(days=7)

    assert stats.metrics.total_users == 3
    assert stats.metrics.total_messages == 9
    assert stats.metrics.active_today == 3
    assert len(stats.activity_chart) == 3
    assert len(stats.chart_data) == 3


@pytest.mark.asyncio
async def test_soft_deleted_ignored(db, collector):
    """Тест что soft-deleted записи игнорируются."""
    now = datetime.utcnow().isoformat()

    # Создаем активного пользователя
    await db.execute(
        "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
        (111111, now),
    )

    # Создаем удаленного пользователя
    await db.execute(
        "INSERT INTO users (telegram_id, created_at, deleted_at) VALUES (?, ?, ?)",
        (222222, now, now),
    )

    # Создаем активное сообщение
    await db.execute(
        "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
        (1, "user", "Active", 6, now),
    )

    # Создаем удаленное сообщение
    await db.execute(
        "INSERT INTO messages (user_id, role, content, length, created_at, deleted_at) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "user", "Deleted", 7, now, now),
    )

    stats = await collector.get_stats(days=7)

    assert stats.metrics.total_users == 1
    assert stats.metrics.total_messages == 1
    assert len(stats.recent_messages) == 1
    assert stats.recent_messages[0].preview == "Active"


@pytest.mark.asyncio
async def test_preview_truncation(db, collector):
    """Тест обрезки превью сообщений."""
    now = datetime.utcnow().isoformat()

    await db.execute(
        "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
        (123456, now),
    )

    long_content = "x" * 200
    await db.execute(
        "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
        (1, "user", long_content, len(long_content), now),
    )

    stats = await collector.get_stats(days=7)

    assert len(stats.recent_messages[0].preview) == 100
    assert stats.recent_messages[0].preview == "x" * 100


@pytest.mark.asyncio
async def test_activity_chart_ordering(db, collector):
    """Тест правильной сортировки графика активности."""
    now = datetime.utcnow()

    await db.execute(
        "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
        (123456, now.isoformat()),
    )

    # Создаем сообщения в обратном порядке
    for i in range(5, 0, -1):
        date = (now - timedelta(days=i)).isoformat()
        await db.execute(
            "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
            (1, "user", "test", 4, date),
        )

    stats = await collector.get_stats(days=7)

    # Проверяем что даты идут по возрастанию
    dates = [point.date for point in stats.activity_chart]
    assert dates == sorted(dates)


@pytest.mark.asyncio
async def test_chart_data_aggregation(db, collector):
    """Тест агрегации данных для детального графика."""
    now = datetime.utcnow()

    # Создаем 3 пользователей
    for i in range(3):
        await db.execute(
            "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
            (100000 + i, now.isoformat()),
        )

    # Все отправляют сообщения сегодня
    date_today = now.isoformat()
    for user_id in range(1, 4):
        for length in [10, 20, 30]:
            await db.execute(
                "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, "user", "x" * length, length, date_today),
            )

    stats = await collector.get_stats(days=1)

    assert len(stats.chart_data) == 1
    point = stats.chart_data[0]
    assert point.active_users == 3
    assert point.messages == 9
    assert point.avg_length == 20.0


@pytest.mark.asyncio
async def test_recent_messages_limit(db, collector):
    """Тест ограничения количества последних сообщений."""
    now = datetime.utcnow()

    await db.execute(
        "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
        (123456, now.isoformat()),
    )

    # Создаем 15 сообщений
    for i in range(15):
        date = (now - timedelta(minutes=i)).isoformat()
        await db.execute(
            "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
            (1, "user", f"Message {i}", 10, date),
        )

    stats = await collector.get_stats(days=7)

    # Проверяем что возвращается максимум 10
    assert len(stats.recent_messages) == 10


@pytest.mark.asyncio
async def test_different_days_parameter(db, collector):
    """Тест параметра days для разных периодов."""
    now = datetime.utcnow()

    await db.execute(
        "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)",
        (123456, now.isoformat()),
    )

    # Создаем сообщения за 15 дней
    for i in range(15):
        date = (now - timedelta(days=i)).isoformat()
        await db.execute(
            "INSERT INTO messages (user_id, role, content, length, created_at) VALUES (?, ?, ?, ?, ?)",
            (1, "user", "test", 4, date),
        )

    # Проверяем разные периоды
    stats_7 = await collector.get_stats(days=7)
    stats_14 = await collector.get_stats(days=14)

    assert len(stats_7.activity_chart) == 7
    assert len(stats_14.activity_chart) == 14

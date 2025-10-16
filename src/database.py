from datetime import datetime

import aiosqlite


class DatabaseManager:
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.connection = await aiosqlite.connect(self.database_path)
        self.connection.row_factory = aiosqlite.Row

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def execute(self, query: str, params: tuple = ()) -> None:
        if not self.connection:
            raise RuntimeError("Database not connected")
        await self.connection.execute(query, params)
        await self.connection.commit()

    async def fetchone(self, query: str, params: tuple = ()) -> dict | None:
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = await self.connection.execute(query, params)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def fetchall(self, query: str, params: tuple = ()) -> list[dict]:
        if not self.connection:
            raise RuntimeError("Database not connected")
        cursor = await self.connection.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_or_create_user(self, telegram_id: int) -> int:
        user = await self.fetchone(
            "SELECT id FROM users WHERE telegram_id = ? AND deleted_at IS NULL", (telegram_id,)
        )
        if user:
            return int(user["id"])

        now = datetime.utcnow().isoformat()
        await self.execute(
            "INSERT INTO users (telegram_id, created_at) VALUES (?, ?)", (telegram_id, now)
        )

        user = await self.fetchone("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        if not user:
            raise RuntimeError("Failed to create user")
        return int(user["id"])

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        now = datetime.utcnow().isoformat()
        length = len(content)
        query = """
            INSERT INTO messages (user_id, role, content, length, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        await self.execute(query, (user_id, role, content, length, now))

    async def get_messages(self, user_id: int) -> list[dict]:
        query = """
            SELECT role, content FROM messages
            WHERE user_id = ? AND deleted_at IS NULL
            ORDER BY created_at
        """
        return await self.fetchall(query, (user_id,))

    async def clear_messages(self, user_id: int) -> None:
        now = datetime.utcnow().isoformat()
        await self.execute(
            "UPDATE messages SET deleted_at = ? WHERE user_id = ? AND deleted_at IS NULL",
            (now, user_id),
        )

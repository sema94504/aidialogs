from .database import DatabaseManager


class SessionManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def get_session(self, user_id: int) -> list[dict]:
        internal_user_id = await self.db.get_or_create_user(user_id)
        return await self.db.get_messages(internal_user_id)

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        internal_user_id = await self.db.get_or_create_user(user_id)
        await self.db.add_message(internal_user_id, role, content)

    async def clear_session(self, user_id: int) -> None:
        internal_user_id = await self.db.get_or_create_user(user_id)
        await self.db.clear_messages(internal_user_id)

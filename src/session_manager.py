import json

from .database import DatabaseManager


class SessionManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def get_session(self, user_id: int) -> list[dict]:
        internal_user_id = await self.db.get_or_create_user(user_id)
        messages = await self.db.get_messages(internal_user_id)

        result = []
        for msg in messages:
            try:
                content_data = json.loads(msg["content"])
            except (json.JSONDecodeError, KeyError):
                content_data = {"text": msg["content"]}

            if "image" in content_data:
                content = []
                if content_data.get("text"):
                    content.append({"type": "text", "text": content_data["text"]})
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{content_data['image']}"},
                    }
                )
            else:
                content = content_data["text"]

            result.append({"role": msg["role"], "content": content})

        return result

    async def add_message(
        self, user_id: int, role: str, content: str, image: str | None = None
    ) -> None:
        internal_user_id = await self.db.get_or_create_user(user_id)
        if image:
            content_json = json.dumps({"text": content, "image": image})
        else:
            content_json = json.dumps({"text": content})
        await self.db.add_message(internal_user_id, role, content_json)

    async def clear_session(self, user_id: int) -> None:
        internal_user_id = await self.db.get_or_create_user(user_id)
        await self.db.clear_messages(internal_user_id)

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

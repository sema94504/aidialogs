"""Pydantic модели для Chat API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Сообщение в чате."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ChatRequest(BaseModel):
    """Запрос на отправку сообщения."""

    message: str = Field(..., min_length=1, max_length=4000)
    mode: Literal["normal", "admin"] = "normal"
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Ответ на сообщение чата."""

    message: str
    session_id: str
    mode: str

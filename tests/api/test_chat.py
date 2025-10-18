"""Тесты для Chat API."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.chat_service import ChatService
from src.api.main import app


@pytest.fixture
def mock_llm_client():
    """Mock LLM client."""
    mock_client = MagicMock()
    mock_client.get_response.return_value = "Это мок ответ от LLM"
    mock_client.model = "test-model"
    mock_client.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Мок ответ в admin режиме"))]
    )
    return mock_client


@pytest.fixture
def mock_db():
    """Mock database manager."""
    return MagicMock()


@pytest.fixture
def client(mock_llm_client, mock_db):
    """Test client для FastAPI приложения."""
    # Инициализируем состояние приложения вручную
    chat_service = ChatService(mock_llm_client, mock_db)
    app.state.chat_service = chat_service
    app.state.db = mock_db
    app.state.llm_client = mock_llm_client

    return TestClient(app)


class TestChatEndpoint:
    """Тесты endpoint /api/chat/message."""

    def test_chat_message_normal_mode(self, client):
        """Тест отправки сообщения в normal режиме."""
        response = client.post(
            "/api/chat/message",
            json={"message": "Привет!", "mode": "normal"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "session_id" in data
        assert "mode" in data
        assert data["mode"] == "normal"
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_chat_message_admin_mode(self, client):
        """Тест отправки сообщения в admin режиме."""
        response = client.post(
            "/api/chat/message",
            json={"message": "Покажи статистику", "mode": "admin"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "session_id" in data
        assert data["mode"] == "admin"

    def test_chat_message_with_session_id(self, client):
        """Тест сохранения контекста через session_id."""
        # Первое сообщение
        response1 = client.post(
            "/api/chat/message",
            json={"message": "Меня зовут Иван", "mode": "normal"},
        )

        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1["session_id"]

        # Второе сообщение с тем же session_id
        response2 = client.post(
            "/api/chat/message",
            json={
                "message": "Как меня зовут?",
                "mode": "normal",
                "session_id": session_id,
            },
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id

    def test_chat_message_empty_text(self, client):
        """Тест с пустым сообщением."""
        response = client.post(
            "/api/chat/message",
            json={"message": "", "mode": "normal"},
        )

        # Должна быть ошибка валидации
        assert response.status_code == 422

    def test_chat_message_invalid_mode(self, client):
        """Тест с неправильным режимом."""
        response = client.post(
            "/api/chat/message",
            json={"message": "Привет", "mode": "invalid"},
        )

        # Должна быть ошибка валидации
        assert response.status_code == 422

    def test_chat_message_long_text(self, client):
        """Тест с длинным сообщением."""
        long_message = "x" * 5000  # Больше лимита 4000

        response = client.post(
            "/api/chat/message",
            json={"message": long_message, "mode": "normal"},
        )

        # Должна быть ошибка валидации
        assert response.status_code == 422


class TestChatModels:
    """Тесты Pydantic моделей для чата."""

    def test_chat_request_valid(self):
        """Тест валидного ChatRequest."""
        from src.api.chat_models import ChatRequest

        request = ChatRequest(message="Привет", mode="normal")
        assert request.message == "Привет"
        assert request.mode == "normal"
        assert request.session_id is None

    def test_chat_request_with_session(self):
        """Тест ChatRequest с session_id."""
        from src.api.chat_models import ChatRequest

        request = ChatRequest(message="Привет", mode="admin", session_id="test-session-123")
        assert request.session_id == "test-session-123"

    def test_chat_response_valid(self):
        """Тест валидного ChatResponse."""
        from src.api.chat_models import ChatResponse

        response = ChatResponse(message="Ответ", session_id="session-123", mode="normal")
        assert response.message == "Ответ"
        assert response.session_id == "session-123"
        assert response.mode == "normal"

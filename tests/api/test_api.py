"""Тесты для FastAPI endpoints."""

import os

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.models import DashboardStats


@pytest.fixture
def client():
    """Test client для FastAPI приложения."""
    # Используем Mock режим для тестов
    os.environ["USE_MOCK_STATS"] = "true"
    return TestClient(app)


class TestRootEndpoints:
    """Тесты корневых endpoints."""

    def test_root_endpoint(self, client):
        """Корневой endpoint возвращает информацию об API."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Dialogs Dashboard API"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "redoc" in data

    def test_health_endpoint(self, client):
        """Health check endpoint работает."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestStatsEndpoint:
    """Тесты endpoint /api/stats."""

    def test_stats_endpoint_returns_200(self, client):
        """Endpoint возвращает код 200."""
        response = client.get("/api/stats")
        assert response.status_code == 200

    def test_stats_endpoint_returns_valid_structure(self, client):
        """Endpoint возвращает валидную структуру данных."""
        response = client.get("/api/stats")
        data = response.json()

        # Проверяем наличие основных ключей
        assert "metrics" in data
        assert "activity_chart" in data
        assert "recent_messages" in data

    def test_stats_endpoint_metrics_structure(self, client):
        """Метрики имеют правильную структуру."""
        response = client.get("/api/stats")
        data = response.json()
        metrics = data["metrics"]

        assert "total_users" in metrics
        assert "total_messages" in metrics
        assert "active_today" in metrics
        assert "avg_message_length" in metrics

        # Проверяем типы
        assert isinstance(metrics["total_users"], int)
        assert isinstance(metrics["total_messages"], int)
        assert isinstance(metrics["active_today"], int)
        assert isinstance(metrics["avg_message_length"], (int, float))

    def test_stats_endpoint_metrics_positive(self, client):
        """Метрики содержат положительные значения."""
        response = client.get("/api/stats")
        data = response.json()
        metrics = data["metrics"]

        assert metrics["total_users"] >= 0
        assert metrics["total_messages"] >= 0
        assert metrics["active_today"] >= 0
        assert metrics["avg_message_length"] >= 0.0

    def test_stats_endpoint_activity_chart_structure(self, client):
        """График активности имеет правильную структуру."""
        response = client.get("/api/stats")
        data = response.json()
        chart = data["activity_chart"]

        assert isinstance(chart, list)
        assert len(chart) > 0

        # Проверяем первую точку
        point = chart[0]
        assert "date" in point
        assert "count" in point
        assert isinstance(point["date"], str)
        assert isinstance(point["count"], int)

    def test_stats_endpoint_recent_messages_structure(self, client):
        """Последние сообщения имеют правильную структуру."""
        response = client.get("/api/stats")
        data = response.json()
        messages = data["recent_messages"]

        assert isinstance(messages, list)
        assert len(messages) > 0

        # Проверяем первое сообщение
        message = messages[0]
        assert "telegram_id" in message
        assert "role" in message
        assert "preview" in message
        assert "created_at" in message

        assert isinstance(message["telegram_id"], int)
        assert message["role"] in ["user", "assistant"]
        assert isinstance(message["preview"], str)
        assert len(message["preview"]) <= 100

    def test_stats_endpoint_validates_with_pydantic(self, client):
        """Response можно валидировать через Pydantic модель."""
        response = client.get("/api/stats")
        data = response.json()

        # Это не должно выбросить исключение
        stats = DashboardStats(**data)
        assert stats.metrics.total_users >= 0

    def test_stats_endpoint_content_type(self, client):
        """Endpoint возвращает JSON."""
        response = client.get("/api/stats")
        assert "application/json" in response.headers["content-type"]


class TestOpenAPIDocumentation:
    """Тесты автогенерации документации."""

    def test_openapi_json_available(self, client):
        """OpenAPI spec доступен."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_swagger_ui_available(self, client):
        """Swagger UI доступен."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client):
        """ReDoc доступен."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_spec_contains_stats_endpoint(self, client):
        """OpenAPI spec содержит /api/stats endpoint."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/api/stats" in data["paths"]
        assert "get" in data["paths"]["/api/stats"]

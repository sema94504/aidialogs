"""Тесты для Pydantic моделей Dashboard API."""

import pytest
from pydantic import ValidationError

from src.api.models import ActivityPoint, ChartDataPoint, DashboardStats, Metrics, RecentMessage


class TestMetrics:
    """Тесты модели Metrics."""

    def test_valid_metrics(self):
        """Валидные данные метрик."""
        metrics = Metrics(
            total_users=100,
            total_messages=500,
            active_today=10,
            avg_message_length=87.5,
        )
        assert metrics.total_users == 100
        assert metrics.total_messages == 500
        assert metrics.active_today == 10
        assert metrics.avg_message_length == 87.5

    def test_zero_values(self):
        """Нулевые значения допустимы."""
        metrics = Metrics(
            total_users=0,
            total_messages=0,
            active_today=0,
            avg_message_length=0.0,
        )
        assert metrics.total_users == 0
        assert metrics.avg_message_length == 0.0

    def test_negative_values_rejected(self):
        """Отрицательные значения отклоняются."""
        with pytest.raises(ValidationError):
            Metrics(
                total_users=-1,
                total_messages=100,
                active_today=5,
                avg_message_length=50.0,
            )

    def test_missing_fields_rejected(self):
        """Отсутствующие поля отклоняются."""
        with pytest.raises(ValidationError):
            Metrics(total_users=100, total_messages=500)


class TestActivityPoint:
    """Тесты модели ActivityPoint."""

    def test_valid_activity_point(self):
        """Валидная точка активности."""
        point = ActivityPoint(date="2025-10-17", count=42)
        assert point.date == "2025-10-17"
        assert point.count == 42

    def test_zero_count(self):
        """Нулевое количество допустимо."""
        point = ActivityPoint(date="2025-10-17", count=0)
        assert point.count == 0

    def test_negative_count_rejected(self):
        """Отрицательное количество отклоняется."""
        with pytest.raises(ValidationError):
            ActivityPoint(date="2025-10-17", count=-1)


class TestRecentMessage:
    """Тесты модели RecentMessage."""

    def test_valid_user_message(self):
        """Валидное сообщение пользователя."""
        message = RecentMessage(
            telegram_id=123456789,
            role="user",
            preview="Привет, как дела?",
            created_at="2025-10-17T10:30:00Z",
        )
        assert message.telegram_id == 123456789
        assert message.role == "user"
        assert message.preview == "Привет, как дела?"
        assert message.created_at == "2025-10-17T10:30:00Z"

    def test_valid_assistant_message(self):
        """Валидное сообщение ассистента."""
        message = RecentMessage(
            telegram_id=123456789,
            role="assistant",
            preview="Отлично, спасибо!",
            created_at="2025-10-17T10:30:05Z",
        )
        assert message.role == "assistant"

    def test_invalid_role_rejected(self):
        """Невалидная роль отклоняется."""
        with pytest.raises(ValidationError):
            RecentMessage(
                telegram_id=123456789,
                role="system",
                preview="Test",
                created_at="2025-10-17T10:30:00Z",
            )

    def test_preview_max_length(self):
        """Превью ограничено 100 символами."""
        long_text = "a" * 101
        with pytest.raises(ValidationError):
            RecentMessage(
                telegram_id=123456789,
                role="user",
                preview=long_text,
                created_at="2025-10-17T10:30:00Z",
            )

    def test_preview_exactly_100_chars(self):
        """Превью ровно 100 символов валидно."""
        text_100 = "a" * 100
        message = RecentMessage(
            telegram_id=123456789,
            role="user",
            preview=text_100,
            created_at="2025-10-17T10:30:00Z",
        )
        assert len(message.preview) == 100


class TestDashboardStats:
    """Тесты модели DashboardStats."""

    def test_valid_dashboard_stats(self):
        """Валидная статистика дашборда."""
        stats = DashboardStats(
            metrics=Metrics(
                total_users=100,
                total_messages=500,
                active_today=10,
                avg_message_length=87.5,
            ),
            activity_chart=[
                ActivityPoint(date="2025-10-16", count=45),
                ActivityPoint(date="2025-10-17", count=67),
            ],
            chart_data=[
                ChartDataPoint(
                    date="2025-10-16",
                    active_users=10,
                    messages=45,
                    avg_length=87.5,
                ),
                ChartDataPoint(
                    date="2025-10-17",
                    active_users=12,
                    messages=67,
                    avg_length=90.0,
                ),
            ],
            recent_messages=[
                RecentMessage(
                    telegram_id=123456789,
                    role="user",
                    preview="Тест",
                    created_at="2025-10-17T10:30:00Z",
                )
            ],
        )
        assert stats.metrics.total_users == 100
        assert len(stats.activity_chart) == 2
        assert len(stats.chart_data) == 2
        assert len(stats.recent_messages) == 1

    def test_empty_collections(self):
        """Пустые коллекции допустимы."""
        stats = DashboardStats(
            metrics=Metrics(
                total_users=0,
                total_messages=0,
                active_today=0,
                avg_message_length=0.0,
            ),
            activity_chart=[],
            chart_data=[],
            recent_messages=[],
        )
        assert len(stats.activity_chart) == 0
        assert len(stats.chart_data) == 0
        assert len(stats.recent_messages) == 0

    def test_activity_chart_max_length(self):
        """График активности ограничен 30 точками."""
        points = [ActivityPoint(date=f"2025-10-{i:02d}", count=i) for i in range(1, 32)]
        with pytest.raises(ValidationError):
            DashboardStats(
                metrics=Metrics(
                    total_users=100,
                    total_messages=500,
                    active_today=10,
                    avg_message_length=87.5,
                ),
                activity_chart=points,
                recent_messages=[],
            )

    def test_recent_messages_max_length(self):
        """Последние сообщения ограничены 20 записями."""
        messages = [
            RecentMessage(
                telegram_id=i,
                role="user",
                preview=f"Message {i}",
                created_at="2025-10-17T10:30:00Z",
            )
            for i in range(21)
        ]
        with pytest.raises(ValidationError):
            DashboardStats(
                metrics=Metrics(
                    total_users=100,
                    total_messages=500,
                    active_today=10,
                    avg_message_length=87.5,
                ),
                activity_chart=[],
                recent_messages=messages,
            )

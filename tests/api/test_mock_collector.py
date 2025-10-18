"""Тесты для Mock реализации StatCollector."""

import pytest

from src.api.mock_stat_collector import MockStatCollector


@pytest.mark.asyncio
class TestMockStatCollector:
    """Тесты MockStatCollector."""

    async def test_get_stats_returns_valid_structure(self):
        """get_stats возвращает валидную структуру данных."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        assert stats.metrics is not None
        assert stats.activity_chart is not None
        assert stats.recent_messages is not None

    async def test_metrics_have_positive_values(self):
        """Метрики содержат положительные значения."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        assert stats.metrics.total_users >= 0
        assert stats.metrics.total_messages >= 0
        assert stats.metrics.active_today >= 0
        assert stats.metrics.avg_message_length >= 0.0

    async def test_metrics_consistency(self):
        """Метрики согласованы между собой."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        # Активных пользователей не может быть больше общего количества
        assert stats.metrics.active_today <= stats.metrics.total_users

    async def test_activity_chart_has_7_days(self):
        """График активности содержит 7 дней по умолчанию."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        assert len(stats.activity_chart) == 7

    async def test_activity_chart_sorted_by_date(self):
        """График активности отсортирован по дате."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        dates = [point.date for point in stats.activity_chart]
        assert dates == sorted(dates)

    async def test_activity_chart_dates_are_sequential(self):
        """Даты в графике последовательны (без пропусков)."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        for i in range(len(stats.activity_chart) - 1):
            current = stats.activity_chart[i].date
            next_date = stats.activity_chart[i + 1].date
            assert current < next_date

    async def test_recent_messages_count(self):
        """Последние сообщения содержат 10 записей по умолчанию."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        assert len(stats.recent_messages) == 10

    async def test_recent_messages_have_both_roles(self):
        """Последние сообщения содержат оба типа ролей."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        roles = {msg.role for msg in stats.recent_messages}
        assert "user" in roles
        assert "assistant" in roles

    async def test_recent_messages_preview_length(self):
        """Превью сообщений не превышает 100 символов."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        for msg in stats.recent_messages:
            assert len(msg.preview) <= 100

    async def test_recent_messages_have_valid_timestamps(self):
        """Сообщения имеют валидные timestamps."""
        collector = MockStatCollector(seed=42)
        stats = await collector.get_stats()

        for msg in stats.recent_messages:
            assert "T" in msg.created_at
            assert msg.created_at.endswith("Z")

    async def test_seed_produces_same_results(self):
        """Одинаковый seed генерирует идентичные данные."""
        collector1 = MockStatCollector(seed=123)
        collector2 = MockStatCollector(seed=123)

        stats1 = await collector1.get_stats()
        stats2 = await collector2.get_stats()

        assert stats1.metrics.total_users == stats2.metrics.total_users
        assert stats1.metrics.total_messages == stats2.metrics.total_messages
        assert stats1.activity_chart[0].count == stats2.activity_chart[0].count

    async def test_different_seeds_produce_different_results(self):
        """Разные seeds генерируют разные данные."""
        collector1 = MockStatCollector(seed=123)
        collector2 = MockStatCollector(seed=456)

        stats1 = await collector1.get_stats()
        stats2 = await collector2.get_stats()

        # Вероятность совпадения всех значений крайне мала
        assert (
            stats1.metrics.total_users != stats2.metrics.total_users
            or stats1.metrics.total_messages != stats2.metrics.total_messages
        )

    async def test_no_seed_produces_random_results(self):
        """Без seed генерируются случайные данные."""
        collector1 = MockStatCollector()
        collector2 = MockStatCollector()

        stats1 = await collector1.get_stats()
        stats2 = await collector2.get_stats()

        # Вероятность совпадения всех значений крайне мала
        assert (
            stats1.metrics.total_users != stats2.metrics.total_users
            or stats1.metrics.total_messages != stats2.metrics.total_messages
        )

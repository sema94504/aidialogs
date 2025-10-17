"""Интерфейс для сборщиков статистики диалогов."""

from typing import Protocol

from src.api.models import DashboardStats


class StatCollector(Protocol):
    """Протокол для реализаций сборщиков статистики.

    Определяет контракт для получения статистики диалогов.
    Поддерживает различные реализации: Mock, Real и т.д.

    Examples:
        >>> collector = MockStatCollector()
        >>> stats = await collector.get_stats()
        >>> print(stats.metrics.total_users)
        42
    """

    async def get_stats(self) -> DashboardStats:
        """Получить статистику для дашборда.

        Returns:
            DashboardStats: Полная статистика с метриками, графиком и сообщениями.

        Raises:
            Exception: При ошибках получения данных.
        """
        ...

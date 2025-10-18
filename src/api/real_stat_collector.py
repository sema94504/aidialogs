"""Real реализация сборщика статистики из SQLite БД."""

from datetime import datetime, timedelta

from src.api.models import ActivityPoint, ChartDataPoint, DashboardStats, Metrics, RecentMessage
from src.database import DatabaseManager


class RealStatCollector:
    """Сборщик статистики из реальной БД.

    Получает данные из SQLite БД с таблицами users и messages.
    """

    def __init__(self, db: DatabaseManager):
        """Инициализация real коллектора.

        Args:
            db: DatabaseManager для работы с БД.
        """
        self.db = db

    async def get_stats(self, days: int = 7) -> DashboardStats:
        """Получить статистику из БД.

        Args:
            days: Количество дней для графиков (по умолчанию 7).

        Returns:
            DashboardStats: Реальные данные из БД.
        """
        metrics = await self._get_metrics()
        activity_chart = await self._get_activity_chart(days)
        chart_data = await self._get_chart_data(days)
        recent_messages = await self._get_recent_messages()

        return DashboardStats(
            metrics=metrics,
            activity_chart=activity_chart,
            chart_data=chart_data,
            recent_messages=recent_messages,
        )

    async def _get_metrics(self) -> Metrics:
        """Получить ключевые метрики."""
        # Всего пользователей
        total_users_row = await self.db.fetchone(
            "SELECT COUNT(*) as count FROM users WHERE deleted_at IS NULL"
        )
        total_users = total_users_row["count"] if total_users_row else 0

        # Всего сообщений
        total_messages_row = await self.db.fetchone(
            "SELECT COUNT(*) as count FROM messages WHERE deleted_at IS NULL"
        )
        total_messages = total_messages_row["count"] if total_messages_row else 0

        # Активных сегодня (за последние 24 часа)
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        active_today_row = await self.db.fetchone(
            """
            SELECT COUNT(DISTINCT user_id) as count
            FROM messages
            WHERE deleted_at IS NULL AND created_at >= ?
            """,
            (yesterday,),
        )
        active_today = active_today_row["count"] if active_today_row else 0

        # Средняя длина сообщения
        avg_length_row = await self.db.fetchone(
            "SELECT AVG(length) as avg FROM messages WHERE deleted_at IS NULL"
        )
        avg_message_length = (
            float(avg_length_row["avg"]) if avg_length_row and avg_length_row["avg"] else 0.0
        )

        return Metrics(
            total_users=total_users,
            total_messages=total_messages,
            active_today=active_today,
            avg_message_length=avg_message_length,
        )

    async def _get_activity_chart(self, days: int) -> list[ActivityPoint]:
        """Получить данные для простого графика активности.

        Args:
            days: Количество дней назад.

        Returns:
            Список точек с датой и количеством сообщений.
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        rows = await self.db.fetchall(
            """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM messages
            WHERE deleted_at IS NULL AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            (start_date,),
        )

        return [ActivityPoint(date=row["date"], count=row["count"]) for row in rows]

    async def _get_chart_data(self, days: int) -> list[ChartDataPoint]:
        """Получить данные для детального графика.

        Args:
            days: Количество дней назад.

        Returns:
            Список точек с датой, активными пользователями, сообщениями и средней длиной.
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        rows = await self.db.fetchall(
            """
            SELECT
                DATE(created_at) as date,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as messages,
                AVG(length) as avg_length
            FROM messages
            WHERE deleted_at IS NULL AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            (start_date,),
        )

        return [
            ChartDataPoint(
                date=row["date"],
                active_users=row["active_users"],
                messages=row["messages"],
                avg_length=float(row["avg_length"]) if row["avg_length"] else 0.0,
            )
            for row in rows
        ]

    async def _get_recent_messages(self) -> list[RecentMessage]:
        """Получить последние сообщения.

        Returns:
            Список последних 10 сообщений с telegram_id.
        """
        rows = await self.db.fetchall(
            """
            SELECT
                u.telegram_id,
                m.role,
                m.content,
                m.created_at
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.deleted_at IS NULL
            ORDER BY m.created_at DESC
            LIMIT 10
            """
        )

        return [
            RecentMessage(
                telegram_id=row["telegram_id"],
                role=row["role"],
                preview=row["content"][:100],
                created_at=row["created_at"],
            )
            for row in rows
        ]


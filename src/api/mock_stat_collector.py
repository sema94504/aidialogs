"""Mock реализация сборщика статистики для тестирования и разработки UI."""

import random
from datetime import datetime, timedelta

from src.api.models import ActivityPoint, DashboardStats, Metrics, RecentMessage


class MockStatCollector:
    """Генератор синтетических данных для дашборда.

    Создает реалистичные тестовые данные без подключения к БД.
    Используется для разработки frontend и демонстрации UI.
    """

    def __init__(self, seed: int | None = None):
        """Инициализация mock коллектора.

        Args:
            seed: Seed для генератора случайных чисел (для воспроизводимости).
        """
        self.random = random.Random(seed)

    async def get_stats(self) -> DashboardStats:
        """Сгенерировать mock статистику.

        Returns:
            DashboardStats: Синтетические данные для дашборда.
        """
        return DashboardStats(
            metrics=self._generate_metrics(),
            activity_chart=self._generate_activity_chart(),
            recent_messages=self._generate_recent_messages(),
        )

    def _generate_metrics(self) -> Metrics:
        """Сгенерировать ключевые метрики."""
        total_messages = self.random.randint(500, 5000)
        total_users = self.random.randint(50, 500)
        active_today = self.random.randint(5, min(50, total_users))

        return Metrics(
            total_users=total_users,
            total_messages=total_messages,
            active_today=active_today,
            avg_message_length=round(self.random.uniform(50.0, 150.0), 1),
        )

    def _generate_activity_chart(self, days: int = 7) -> list[ActivityPoint]:
        """Сгенерировать данные графика активности.

        Args:
            days: Количество дней истории (по умолчанию 7).

        Returns:
            Список точек активности за последние дни.
        """
        today = datetime.now().date()
        points = []

        for i in range(days):
            date = today - timedelta(days=days - 1 - i)
            count = self.random.randint(20, 150)
            points.append(ActivityPoint(date=date.isoformat(), count=count))

        return points

    def _generate_recent_messages(self, count: int = 10) -> list[RecentMessage]:
        """Сгенерировать последние сообщения.

        Args:
            count: Количество сообщений (по умолчанию 10).

        Returns:
            Список последних сообщений.
        """
        messages = []
        now = datetime.now()

        # Шаблоны сообщений для реалистичности
        user_templates = [
            "Как настроить систему?",
            "Покажи статистику за неделю",
            "Что нового в обновлении?",
            "Помоги разобраться с ошибкой",
            "Как экспортировать данные?",
            "Можно ли изменить настройки?",
            "Где посмотреть логи?",
            "Как добавить нового пользователя?",
            "Объясни как работает функция X",
            "Не получается подключиться к API",
        ]

        assistant_templates = [
            "Для настройки системы выполните шаги: откройте конфигурацию, измените параметры...",
            "Статистика за 7 дней: всего сообщений 1234, активных пользователей 42...",
            "В последнем обновлении: поддержка изображений, улучшенная статистика...",
            "Проверьте: версию зависимостей, права доступа, логи системы...",
            "Для экспорта используйте команду export или API endpoint /api/export...",
            "Да, настройки можно изменить в конфигурации или через /settings...",
            "Логи в файле bot.log и через команду journalctl для systemd...",
            "Для добавления пользователя используйте adduser или регистрацию через бот...",
            "Функция X: принимает параметры A и B, возвращает результат C...",
            "Убедитесь что API запущен на порту 8000 и доступен на localhost...",
        ]

        for i in range(count):
            # Чередуем user и assistant сообщения
            is_user = i % 2 == 0
            role = "user" if is_user else "assistant"
            templates = user_templates if is_user else assistant_templates

            # Выбираем случайный текст и обрезаем до 100 символов
            text = self.random.choice(templates)
            preview = text[:100]

            # Генерируем timestamp (сообщения в обратном порядке)
            timestamp = now - timedelta(minutes=i * 5)

            telegram_id = self.random.randint(100000000, 999999999)

            messages.append(
                RecentMessage(
                    telegram_id=telegram_id,
                    role=role,
                    preview=preview,
                    created_at=timestamp.isoformat() + "Z",
                )
            )

        return messages

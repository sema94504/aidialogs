"""Pydantic модели для Dashboard API."""

from pydantic import BaseModel, Field


class Metrics(BaseModel):
    """Ключевые метрики дашборда."""

    total_users: int = Field(..., ge=0, description="Всего пользователей")
    total_messages: int = Field(..., ge=0, description="Всего сообщений")
    active_today: int = Field(..., ge=0, description="Активных пользователей сегодня")
    avg_message_length: float = Field(..., ge=0.0, description="Средняя длина сообщения")


class ActivityPoint(BaseModel):
    """Точка данных для графика активности."""

    date: str = Field(..., description="Дата в формате ISO (YYYY-MM-DD)")
    count: int = Field(..., ge=0, description="Количество сообщений за день")


class ChartDataPoint(BaseModel):
    """Точка данных для интерактивных графиков."""

    date: str = Field(..., description="Дата в формате ISO (YYYY-MM-DD)")
    active_users: int | None = Field(None, ge=0, description="Активные пользователи за день")
    messages: int | None = Field(None, ge=0, description="Количество сообщений за день")
    avg_length: float | None = Field(None, ge=0.0, description="Средняя длина сообщения за день")


class RecentMessage(BaseModel):
    """Последнее сообщение пользователя."""

    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    role: str = Field(..., pattern="^(user|assistant)$", description="Роль отправителя")
    preview: str = Field(..., max_length=100, description="Превью текста (первые 100 символов)")
    full_text: str = Field(..., description="Полный текст сообщения")
    created_at: str = Field(..., description="Дата создания в формате ISO 8601")


class DashboardStats(BaseModel):
    """Полная статистика для дашборда."""

    metrics: Metrics
    activity_chart: list[ActivityPoint] = Field(..., min_length=0, max_length=30)
    chart_data: list[ChartDataPoint] = Field(..., min_length=0, max_length=90)
    recent_messages: list[RecentMessage] = Field(..., min_length=0, max_length=20)

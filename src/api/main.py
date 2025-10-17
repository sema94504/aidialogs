"""FastAPI приложение для Dashboard API."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.mock_stat_collector import MockStatCollector
from src.api.models import DashboardStats
from src.api.stat_collector import StatCollector

app = FastAPI(
    title="AI Dialogs Dashboard API",
    description="API для получения статистики диалогов с Telegram ботом",
    version="1.0.0",
)

# CORS для доступа из frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_stat_collector() -> StatCollector:
    """Dependency для получения StatCollector.

    Возвращает Mock реализацию (в будущем будет переключение на Real).

    Returns:
        StatCollector: Реализация сборщика статистики.
    """
    return MockStatCollector()


@app.get("/api/stats", response_model=DashboardStats)
async def get_stats(collector: StatCollector = Depends(get_stat_collector)) -> DashboardStats:
    """Получить статистику для дашборда.

    Args:
        collector: Инжектированный StatCollector.

    Returns:
        DashboardStats: Полная статистика с метриками, графиком и сообщениями.
    """
    return await collector.get_stats()


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой endpoint с информацией об API.

    Returns:
        dict: Информация об API.
    """
    return {
        "name": "AI Dialogs Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Статус здоровья API.
    """
    return {"status": "ok"}

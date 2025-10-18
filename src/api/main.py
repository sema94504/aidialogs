"""FastAPI приложение для Dashboard API."""

import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.chat_models import ChatRequest, ChatResponse
from src.api.chat_service import ChatService
from src.api.mock_stat_collector import MockStatCollector
from src.api.real_stat_collector import RealStatCollector
from src.api.stat_collector import StatCollector
from src.config import Config
from src.database import DatabaseManager
from src.llm_client import LLMClient


class UnicodeJSONResponse(JSONResponse):
    """JSONResponse с корректной обработкой Unicode."""

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    config = Config()

    # Инициализация DatabaseManager
    db = DatabaseManager(config.database_path)
    await db.connect()
    app.state.db = db

    # Инициализация LLMClient для чата
    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt_file=config.system_prompt_file,
    )
    app.state.llm_client = llm_client

    # Инициализация ChatService
    chat_service = ChatService(llm_client, db)
    app.state.chat_service = chat_service

    yield

    await db.close()


app = FastAPI(
    title="AI Dialogs Dashboard API",
    description="API для получения статистики диалогов с Telegram ботом",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=UnicodeJSONResponse,
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

    Возвращает Mock или Real реализацию в зависимости от конфигурации.

    Returns:
        StatCollector: Реализация сборщика статистики.
    """
    config = Config()
    if config.use_mock_stats:
        return MockStatCollector()
    return RealStatCollector(app.state.db)


@app.get("/api/stats")
async def get_stats(
    days: int = 7, collector: StatCollector = Depends(get_stat_collector)
) -> UnicodeJSONResponse:
    """Получить статистику для дашборда.

    Args:
        days: Количество дней для графиков (по умолчанию 7).
        collector: Инжектированный StatCollector.

    Returns:
        DashboardStats: Полная статистика с метриками, графиком и сообщениями.
    """
    stats = await collector.get_stats(days=days)
    return UnicodeJSONResponse(content=stats.dict())


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


@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest) -> ChatResponse:
    """Отправить сообщение в чат и получить ответ.

    Args:
        request: Запрос с сообщением и режимом.

    Returns:
        ChatResponse: Ответ ассистента с session_id.
    """
    chat_service: ChatService = app.state.chat_service

    response_text, session_id = await chat_service.process_message(
        message=request.message, mode=request.mode, session_id=request.session_id
    )

    return ChatResponse(message=response_text, session_id=session_id, mode=request.mode)

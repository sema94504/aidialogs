"""Сервис для обработки запросов чата."""

import logging
import uuid
from datetime import datetime

from src.database import DatabaseManager
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ChatSession:
    """Сессия чата с историей сообщений."""

    def __init__(self, session_id: str, mode: str = "normal"):
        self.session_id = session_id
        self.mode = mode
        self.messages: list[dict] = []
        self.created_at = datetime.utcnow()


class ChatService:
    """Сервис для обработки сообщений чата."""

    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        """Инициализация chat сервиса.

        Args:
            llm_client: Клиент для работы с LLM.
            db: Менеджер базы данных.
        """
        self.llm_client = llm_client
        self.db = db
        self.sessions: dict[str, ChatSession] = {}
        self.admin_prompt = self._get_admin_prompt()

    def _get_admin_prompt(self) -> str:
        """Получить system prompt для admin режима."""
        return """Ты помощник администратора для анализа статистики Telegram бота.

База данных содержит:
- Таблица users: id, telegram_id, created_at, deleted_at
- Таблица messages: id, user_id, role (user/assistant), content, length, created_at, deleted_at

Ты можешь помогать администратору:
- Объяснять статистику
- Отвечать на вопросы об активности пользователей
- Давать рекомендации по анализу данных

Отвечай кратко и по делу на русском языке."""

    def _get_or_create_session(self, session_id: str | None, mode: str) -> ChatSession:
        """Получить или создать сессию.

        Args:
            session_id: ID сессии или None для новой.
            mode: Режим работы (normal/admin).

        Returns:
            ChatSession: Сессия чата.
        """
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            # Обновить режим если изменился
            session.mode = mode
            return session

        # Создать новую сессию
        new_session_id = session_id or str(uuid.uuid4())
        session = ChatSession(new_session_id, mode)
        self.sessions[new_session_id] = session
        logger.info(f"Создана новая сессия: {new_session_id}, режим: {mode}")
        return session

    async def process_message(
        self, message: str, mode: str, session_id: str | None
    ) -> tuple[str, str]:
        """Обработать сообщение и вернуть ответ.

        Args:
            message: Текст сообщения пользователя.
            mode: Режим работы (normal/admin).
            session_id: ID сессии или None.

        Returns:
            tuple[str, str]: (ответ, session_id)
        """
        session = self._get_or_create_session(session_id, mode)

        # Добавить сообщение пользователя в историю
        user_message = {"role": "user", "content": message}
        session.messages.append(user_message)

        try:
            # Получить ответ от LLM
            if mode == "admin":
                response = await self._process_admin_message(session)
            else:
                response = await self._process_normal_message(session)

            # Добавить ответ ассистента в историю
            assistant_message = {"role": "assistant", "content": response}
            session.messages.append(assistant_message)

            logger.info(
                f"Обработано сообщение в сессии {session.session_id}, "
                f"режим: {mode}, длина ответа: {len(response)}"
            )

            return response, session.session_id

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            error_response = "Извините, произошла ошибка при обработке вашего запроса."
            return error_response, session.session_id

    async def _process_normal_message(self, session: ChatSession) -> str:
        """Обработать сообщение в normal режиме.

        Args:
            session: Сессия чата.

        Returns:
            str: Ответ ассистента.
        """
        # Использовать стандартный system prompt из LLMClient
        response = self.llm_client.get_response(session.messages)
        return response

    async def _process_admin_message(self, session: ChatSession) -> str:
        """Обработать сообщение в admin режиме.

        Args:
            session: Сессия чата.

        Returns:
            str: Ответ ассистента.
        """
        # Получить реальную статистику из БД
        stats_context = await self._get_stats_context()

        # Создать расширенный admin prompt с реальными данными
        admin_prompt_with_stats = f"""{self.admin_prompt}

Текущая статистика из базы данных:
{stats_context}

Используй эти данные для ответа на вопросы пользователя."""

        messages_with_admin_prompt = [
            {"role": "system", "content": admin_prompt_with_stats}
        ] + session.messages

        # Вызвать LLM напрямую через client
        response = self.llm_client.client.chat.completions.create(
            model=self.llm_client.model, messages=messages_with_admin_prompt
        )

        content = response.choices[0].message.content
        return content if content is not None else ""

    async def _get_stats_context(self) -> str:
        """Получить контекст со статистикой из БД.

        Returns:
            str: Текстовое представление статистики.
        """
        try:
            # Получить базовые метрики
            total_users = await self.db.fetchone(
                "SELECT COUNT(*) as count FROM users WHERE deleted_at IS NULL"
            )
            total_messages = await self.db.fetchone(
                "SELECT COUNT(*) as count FROM messages WHERE deleted_at IS NULL"
            )
            avg_length = await self.db.fetchone(
                "SELECT AVG(length) as avg FROM messages WHERE deleted_at IS NULL"
            )

            # Активные пользователи за последние 24 часа
            from datetime import timedelta

            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            active_today = await self.db.fetchone(
                """SELECT COUNT(DISTINCT user_id) as count
                   FROM messages
                   WHERE deleted_at IS NULL AND created_at >= ?""",
                (yesterday,),
            )

            # Последние сообщения
            recent = await self.db.fetchall(
                """SELECT COUNT(*) as count, role
                   FROM messages
                   WHERE deleted_at IS NULL
                   GROUP BY role"""
            )

            users_count = total_users["count"] if total_users else 0
            messages_count = total_messages["count"] if total_messages else 0
            active_count = active_today["count"] if active_today else 0
            avg_len = float(avg_length["avg"]) if (avg_length and avg_length.get("avg")) else 0.0

            stats_text = f"""
- Всего пользователей: {users_count}
- Всего сообщений: {messages_count}
- Активных пользователей за последние 24 часа: {active_count}
- Средняя длина сообщения: {avg_len:.1f} символов
- Распределение по ролям:"""

            for row in recent:
                stats_text += f"\n  - {row['role']}: {row['count']} сообщений"

            return stats_text.strip()

        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return "Статистика временно недоступна."

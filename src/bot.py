import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

try:
    from .llm_client import LLMClient
except ImportError:
    from llm_client import LLMClient

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, llm_client: LLMClient):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.llm_client = llm_client
        self.user_sessions: dict[int, list[dict]] = {}
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message.register(self._start_handler, Command("start"))
        self.dp.message.register(self._reset_handler, Command("reset"))
        self.dp.message.register(self._message_handler)

    async def _start_handler(self, message: Message):
        user_id = message.from_user.id
        logger.info(f"Команда /start от пользователя {user_id}")
        self.user_sessions[user_id] = []
        await message.answer("Привет! Я AI-ассистент. Задай мне любой вопрос.")

    async def _reset_handler(self, message: Message):
        user_id = message.from_user.id
        logger.info(f"Команда /reset от пользователя {user_id}")
        self.user_sessions[user_id] = []
        await message.answer("История диалога очищена. Начнём сначала!")

    async def _message_handler(self, message: Message):
        if not message.text:
            return

        user_id = message.from_user.id
        logger.info(f"Сообщение от пользователя {user_id}: {message.text}")

        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []

        self.user_sessions[user_id].append({"role": "user", "content": message.text})

        try:
            logger.info(f"Отправка запроса в LLM для пользователя {user_id}")
            response = self.llm_client.get_response(self.user_sessions[user_id])
            logger.info(f"Получен ответ от LLM для пользователя {user_id}")

            self.user_sessions[user_id].append({"role": "assistant", "content": response})

            await message.answer(response)
        except Exception as e:
            logger.error(f"Ошибка при получении ответа LLM для пользователя {user_id}: {e}")
            await message.answer("Извините, произошла ошибка. Попробуйте позже.")

    async def start(self):
        await self.dp.start_polling(self.bot)

import asyncio
import base64
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from .database import DatabaseManager
from .llm_client import LLMClient
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
        self, token: str, llm_client: LLMClient, system_prompt_file: str, db: DatabaseManager
    ):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.llm_client = llm_client
        self.session_manager = SessionManager(db)
        self.system_prompt_file = system_prompt_file
        self.db = db
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message.register(self._start_handler, Command("start"))
        self.dp.message.register(self._reset_handler, Command("reset"))
        self.dp.message.register(self._role_handler, Command("role"))
        self.dp.message.register(self._message_handler)

    async def _start_handler(self, message: Message):
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /start от пользователя {user_id}")
        await self.session_manager.clear_session(user_id)
        await message.answer("Привет! Я AI-ассистент. Задай мне любой вопрос.")

    async def _reset_handler(self, message: Message):
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /reset от пользователя {user_id}")
        await self.session_manager.clear_session(user_id)
        await message.answer("История диалога очищена. Начнём сначала!")

    async def _role_handler(self, message: Message):
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info(f"Команда /role от пользователя {user_id}")
        prompt = self.llm_client.system_prompt.strip()
        if not prompt:
            await message.answer("Системный промпт не задан.")
        else:
            await message.answer(prompt)

    async def _message_handler(self, message: Message):
        if not message.from_user:
            return

        user_id = message.from_user.id

        if message.photo:
            file = await self.bot.get_file(message.photo[-1].file_id)
            image_bytes = await self.bot.download_file(file.file_path)
            image_base64 = base64.b64encode(image_bytes.read()).decode()

            text = message.caption or ""
            logger.info(f"Фото от пользователя {user_id}, размер: {len(image_base64)} байт")
            await self.session_manager.add_message(user_id, "user", text, image_base64)
        elif message.text:
            logger.info(f"Сообщение от пользователя {user_id}: {message.text}")
            await self.session_manager.add_message(user_id, "user", message.text)
        else:
            return

        try:
            logger.info(f"Отправка запроса в LLM для пользователя {user_id}")
            session = await self.session_manager.get_session(user_id)
            response = await asyncio.to_thread(self.llm_client.get_response, session)
            logger.info(f"Получен ответ от LLM для пользователя {user_id}")

            await self.session_manager.add_message(user_id, "assistant", response)

            await message.answer(response)
        except Exception as e:
            logger.error(f"Ошибка при получении ответа LLM для пользователя {user_id}: {e}")
            await message.answer("Извините, произошла ошибка. Попробуйте позже.")

    async def start(self):
        await self.dp.start_polling(self.bot)

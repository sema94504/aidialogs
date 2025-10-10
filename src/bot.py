import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self._register_handlers()
    
    def _register_handlers(self):
        self.dp.message.register(self._start_handler, Command('start'))
        self.dp.message.register(self._echo_handler)
    
    async def _start_handler(self, message: Message):
        await message.answer('Привет! Я эхо-бот. Отправь мне сообщение.')
    
    async def _echo_handler(self, message: Message):
        if message.text:
            await message.answer(message.text)
    
    async def start(self):
        await self.dp.start_polling(self.bot)


import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message
from src.bot import TelegramBot

@pytest.fixture
def bot():
    with patch('src.bot.Bot'):
        return TelegramBot('123456789:ABCdefGHIjklMNOpqrsTUVwxyz')

@pytest.mark.asyncio
async def test_start_command(bot):
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()
    await bot._start_handler(message)
    message.answer.assert_called_once_with('Привет! Я эхо-бот. Отправь мне сообщение.')

@pytest.mark.asyncio
async def test_echo_handler(bot):
    message = MagicMock(spec=Message)
    message.text = 'Тестовое сообщение'
    message.answer = AsyncMock()
    await bot._echo_handler(message)
    message.answer.assert_called_once_with('Тестовое сообщение')


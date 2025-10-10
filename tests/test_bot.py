import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message
from src.bot import TelegramBot
from src.llm_client import LLMClient

@pytest.fixture
def llm_client():
    return MagicMock(spec=LLMClient)

@pytest.fixture
def bot(llm_client):
    with patch('src.bot.Bot'):
        return TelegramBot('123456789:ABCdefGHIjklMNOpqrsTUVwxyz', llm_client)

@pytest.mark.asyncio
async def test_start_command(bot):
    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()
    
    await bot._start_handler(message)
    
    assert 123 in bot.user_sessions
    assert bot.user_sessions[123] == []
    message.answer.assert_called_once_with('Привет! Я AI-ассистент. Задай мне любой вопрос.')

@pytest.mark.asyncio
async def test_message_handler(bot, llm_client):
    llm_client.get_response.return_value = "Это ответ от LLM"
    
    message = MagicMock()
    message.from_user.id = 123
    message.text = 'Привет, как дела?'
    message.answer = AsyncMock()
    
    await bot._message_handler(message)
    
    assert len(bot.user_sessions[123]) == 2
    assert bot.user_sessions[123][0] == {"role": "user", "content": "Привет, как дела?"}
    assert bot.user_sessions[123][1] == {"role": "assistant", "content": "Это ответ от LLM"}
    
    llm_client.get_response.assert_called_once()
    message.answer.assert_called_once_with("Это ответ от LLM")

@pytest.mark.asyncio
async def test_message_handler_with_history(bot, llm_client):
    bot.user_sessions[123] = [
        {"role": "user", "content": "Первое сообщение"},
        {"role": "assistant", "content": "Первый ответ"}
    ]
    
    def check_history(messages):
        assert len(messages) == 3
        assert messages[0] == {"role": "user", "content": "Первое сообщение"}
        assert messages[1] == {"role": "assistant", "content": "Первый ответ"}
        assert messages[2] == {"role": "user", "content": "Второе сообщение"}
        return "Второй ответ"
    
    llm_client.get_response.side_effect = check_history
    
    message = MagicMock()
    message.from_user.id = 123
    message.text = 'Второе сообщение'
    message.answer = AsyncMock()
    
    await bot._message_handler(message)
    
    assert len(bot.user_sessions[123]) == 4
    llm_client.get_response.assert_called_once()

@pytest.mark.asyncio
async def test_reset_command(bot):
    bot.user_sessions[123] = [
        {"role": "user", "content": "Старое сообщение"},
        {"role": "assistant", "content": "Старый ответ"}
    ]
    
    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()
    
    await bot._reset_handler(message)
    
    assert 123 in bot.user_sessions
    assert bot.user_sessions[123] == []
    message.answer.assert_called_once_with('История диалога очищена. Начнём сначала!')


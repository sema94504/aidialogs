from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot import TelegramBot
from src.llm_client import LLMClient


@pytest.fixture
def llm_client():
    return MagicMock(spec=LLMClient)


@pytest.fixture
def bot(llm_client):
    with patch("src.bot.Bot"):
        return TelegramBot("123456789:ABCdefGHIjklMNOpqrsTUVwxyz", llm_client)


@pytest.mark.asyncio
async def test_start_command(bot):
    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()

    await bot._start_handler(message)

    assert bot.session_manager.get_session(123) == []
    message.answer.assert_called_once_with("Привет! Я AI-ассистент. Задай мне любой вопрос.")


@pytest.mark.asyncio
async def test_message_handler(bot, llm_client):
    llm_client.get_response.return_value = "Это ответ от LLM"

    message = MagicMock()
    message.from_user.id = 123
    message.text = "Привет, как дела?"
    message.answer = AsyncMock()

    await bot._message_handler(message)

    session = bot.session_manager.get_session(123)
    assert len(session) == 2
    assert session[0] == {"role": "user", "content": "Привет, как дела?"}
    assert session[1] == {"role": "assistant", "content": "Это ответ от LLM"}

    llm_client.get_response.assert_called_once()
    message.answer.assert_called_once_with("Это ответ от LLM")


@pytest.mark.asyncio
async def test_message_handler_with_history(bot, llm_client):
    bot.session_manager.add_message(123, "user", "Первое сообщение")
    bot.session_manager.add_message(123, "assistant", "Первый ответ")

    def check_history(messages):
        assert len(messages) == 3
        assert messages[0] == {"role": "user", "content": "Первое сообщение"}
        assert messages[1] == {"role": "assistant", "content": "Первый ответ"}
        assert messages[2] == {"role": "user", "content": "Второе сообщение"}
        return "Второй ответ"

    llm_client.get_response.side_effect = check_history

    message = MagicMock()
    message.from_user.id = 123
    message.text = "Второе сообщение"
    message.answer = AsyncMock()

    await bot._message_handler(message)

    assert len(bot.session_manager.get_session(123)) == 4
    llm_client.get_response.assert_called_once()


@pytest.mark.asyncio
async def test_reset_command(bot):
    bot.session_manager.add_message(123, "user", "Старое сообщение")
    bot.session_manager.add_message(123, "assistant", "Старый ответ")

    message = MagicMock()
    message.from_user.id = 123
    message.answer = AsyncMock()

    await bot._reset_handler(message)

    assert bot.session_manager.get_session(123) == []
    message.answer.assert_called_once_with("История диалога очищена. Начнём сначала!")


@pytest.mark.asyncio
async def test_message_handler_llm_error(bot, llm_client):
    llm_client.get_response.side_effect = Exception("LLM Error")

    message = MagicMock()
    message.from_user.id = 123
    message.text = "Тест"
    message.answer = AsyncMock()

    await bot._message_handler(message)

    message.answer.assert_called_once_with("Извините, произошла ошибка. Попробуйте позже.")


@pytest.mark.asyncio
async def test_message_handler_no_text(bot, llm_client):
    message = MagicMock()
    message.from_user.id = 123
    message.text = None
    message.answer = AsyncMock()

    await bot._message_handler(message)

    message.answer.assert_not_called()
    llm_client.get_response.assert_not_called()

from unittest.mock import patch

from src.bot import TelegramBot
from src.config import Config
from src.llm_client import LLMClient


def test_full_integration():
    config = Config(
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt="Test prompt",
    )
    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt=config.system_prompt,
    )

    with patch("src.bot.Bot"):
        bot = TelegramBot(config.telegram_bot_token, llm_client)

        assert bot.llm_client == llm_client
        assert bot.session_manager.get_session(999) == []


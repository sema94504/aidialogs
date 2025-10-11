from unittest.mock import patch

from src.bot import TelegramBot
from src.config import Config
from src.llm_client import LLMClient


def test_full_integration():
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "LLM_BASE_URL": "http://test.api/v1",
        "LLM_MODEL": "test-model",
        "SYSTEM_PROMPT": "Test prompt",
    }

    with patch("src.config.load_dotenv"), patch.dict("os.environ", env_vars):
        config = Config()
        llm_client = LLMClient(
            base_url=config.llm_base_url,
            model=config.llm_model,
            system_prompt=config.system_prompt,
        )

        with patch("src.bot.Bot"):
            bot = TelegramBot(config.telegram_bot_token, llm_client)

            assert bot.llm_client == llm_client
            assert bot.user_sessions == {}


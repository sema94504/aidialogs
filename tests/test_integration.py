from unittest.mock import patch

import pytest

from src.bot import TelegramBot
from src.config import Config
from src.llm_client import LLMClient


def test_full_integration(tmp_path):
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("Test prompt")

    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file=str(prompt_file),
    )
    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt_file=config.system_prompt_file,
    )

    with patch("src.bot.Bot"):
        bot = TelegramBot(config.telegram_bot_token, llm_client, config.system_prompt_file)

        assert bot.llm_client == llm_client
        assert bot.session_manager.get_session(999) == []


def test_smoke_initialization(tmp_path):
    prompt_file = tmp_path / "smoke_prompt.txt"
    prompt_file.write_text("Ты smoke test ассистент.")

    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file=str(prompt_file),
    )

    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt_file=config.system_prompt_file,
    )
    assert llm_client.system_prompt == "Ты smoke test ассистент."

    with patch("src.bot.Bot"):
        bot = TelegramBot(config.telegram_bot_token, llm_client, config.system_prompt_file)

        assert bot.llm_client is not None
        assert bot.session_manager is not None
        assert bot.system_prompt_file == str(prompt_file)


def test_smoke_prompt_file_not_found():
    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file="nonexistent.txt",
    )

    with pytest.raises(FileNotFoundError):
        LLMClient(
            base_url=config.llm_base_url,
            model=config.llm_model,
            system_prompt_file=config.system_prompt_file,
        )

import pytest
from pydantic import ValidationError

from src.config import Config


def test_config_missing_token():
    with pytest.raises(ValidationError):
        Config(
            _env_file=None,
            telegram_bot_token=None,  # type: ignore
            llm_base_url="http://test.api/v1",
            llm_model="test-model",
            system_prompt_file="prompts/system_prompt.txt",
        )


def test_config_valid():
    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file="prompts/system_prompt.txt",
    )
    assert config.telegram_bot_token == "test_token"
    assert config.llm_base_url == "http://test.api/v1"
    assert config.llm_model == "test-model"
    assert config.system_prompt_file == "prompts/system_prompt.txt"


def test_config_with_system_prompt_file():
    config = Config(
        _env_file=None,
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt_file="prompts/system_prompt.txt",
    )
    assert config.system_prompt_file == "prompts/system_prompt.txt"

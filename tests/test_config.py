import pytest
from pydantic import ValidationError

from src.config import Config


def test_config_missing_token():
    with pytest.raises(ValidationError):
        Config(
            telegram_bot_token=None,  # type: ignore
            llm_base_url="http://test.api/v1",
            llm_model="test-model",
            system_prompt="Test prompt",
        )


def test_config_valid():
    config = Config(
        telegram_bot_token="test_token",
        llm_base_url="http://test.api/v1",
        llm_model="test-model",
        system_prompt="Test prompt",
    )
    assert config.telegram_bot_token == "test_token"
    assert config.llm_base_url == "http://test.api/v1"
    assert config.llm_model == "test-model"
    assert config.system_prompt == "Test prompt"

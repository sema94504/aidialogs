import pytest
from unittest.mock import patch
from src.config import Config

def test_config_missing_token():
    with patch('src.config.load_dotenv'), patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match='TELEGRAM_BOT_TOKEN'):
            Config()

def test_config_valid():
    env_vars = {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'LLM_BASE_URL': 'http://test.api/v1',
        'LLM_MODEL': 'test-model',
        'SYSTEM_PROMPT': 'Test prompt'
    }
    with patch('src.config.load_dotenv'), patch.dict('os.environ', env_vars):
        config = Config()
        assert config.telegram_bot_token == 'test_token'
        assert config.llm_base_url == 'http://test.api/v1'
        assert config.llm_model == 'test-model'
        assert config.system_prompt == 'Test prompt'


import pytest
from unittest.mock import patch
from src.config import Config

def test_config_missing_token():
    with patch('src.config.load_dotenv'), patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match='TELEGRAM_BOT_TOKEN'):
            Config()

def test_config_valid():
    with patch('src.config.load_dotenv'), patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': 'test_token'}):
        config = Config()
        assert config.telegram_bot_token == 'test_token'


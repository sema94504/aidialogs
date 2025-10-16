from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.main import main


@pytest.mark.asyncio
async def test_main_initialization(tmp_path):
    prompt_file = tmp_path / "test_prompt.txt"
    prompt_file.write_text("Test prompt")

    with (
        patch("src.main.Config") as mock_config,
        patch("src.main.DatabaseManager") as mock_db,
        patch("src.main.LLMClient") as mock_llm_client,
        patch("src.main.TelegramBot") as mock_bot,
    ):
        mock_config_instance = MagicMock()
        mock_config_instance.telegram_bot_token = "test_token"
        mock_config_instance.llm_base_url = "http://test.api/v1"
        mock_config_instance.llm_model = "test-model"
        mock_config_instance.system_prompt_file = str(prompt_file)
        mock_config_instance.database_path = "aidialogs.db"
        mock_config.return_value = mock_config_instance

        mock_db_instance = MagicMock()
        mock_db_instance.connect = AsyncMock()
        mock_db_instance.close = AsyncMock()
        mock_db.return_value = mock_db_instance

        mock_llm_instance = MagicMock()
        mock_llm_client.return_value = mock_llm_instance

        mock_bot_instance = MagicMock()
        mock_bot_instance.start = AsyncMock(side_effect=KeyboardInterrupt)
        mock_bot.return_value = mock_bot_instance

        await main()

        mock_config.assert_called_once()
        mock_db.assert_called_once_with("aidialogs.db")
        mock_db_instance.connect.assert_called_once()
        mock_llm_client.assert_called_once_with(
            base_url="http://test.api/v1",
            model="test-model",
            system_prompt_file=str(prompt_file),
        )
        mock_bot.assert_called_once()
        mock_bot_instance.start.assert_called_once()
        mock_db_instance.close.assert_called_once()


@pytest.mark.asyncio
async def test_main_keyboard_interrupt():
    with (
        patch("src.main.Config") as mock_config,
        patch("src.main.DatabaseManager") as mock_db,
        patch("src.main.LLMClient") as mock_llm_client,
        patch("src.main.TelegramBot") as mock_bot,
        patch("src.main.logger") as mock_logger,
    ):
        mock_config_instance = MagicMock()
        mock_config_instance.telegram_bot_token = "test_token"
        mock_config_instance.llm_base_url = "http://test.api/v1"
        mock_config_instance.llm_model = "test-model"
        mock_config_instance.system_prompt_file = "prompts/system_prompt.txt"
        mock_config_instance.database_path = "aidialogs.db"
        mock_config.return_value = mock_config_instance

        mock_db_instance = MagicMock()
        mock_db_instance.connect = AsyncMock()
        mock_db_instance.close = AsyncMock()
        mock_db.return_value = mock_db_instance

        mock_llm_instance = MagicMock()
        mock_llm_client.return_value = mock_llm_instance

        mock_bot_instance = MagicMock()
        mock_bot_instance.start = AsyncMock(side_effect=KeyboardInterrupt)
        mock_bot.return_value = mock_bot_instance

        await main()

        mock_logger.info.assert_any_call("Бот запущен")
        mock_logger.info.assert_any_call("Бот остановлен")


@pytest.mark.asyncio
async def test_main_exception_handling():
    with (
        patch("src.main.Config") as mock_config,
        patch("src.main.DatabaseManager") as mock_db,
        patch("src.main.LLMClient") as mock_llm_client,
        patch("src.main.TelegramBot") as mock_bot,
        patch("src.main.logger") as mock_logger,
    ):
        mock_config_instance = MagicMock()
        mock_config_instance.telegram_bot_token = "test_token"
        mock_config_instance.llm_base_url = "http://test.api/v1"
        mock_config_instance.llm_model = "test-model"
        mock_config_instance.system_prompt_file = "prompts/system_prompt.txt"
        mock_config_instance.database_path = "aidialogs.db"
        mock_config.return_value = mock_config_instance

        mock_db_instance = MagicMock()
        mock_db_instance.connect = AsyncMock()
        mock_db_instance.close = AsyncMock()
        mock_db.return_value = mock_db_instance

        mock_llm_instance = MagicMock()
        mock_llm_client.return_value = mock_llm_instance

        mock_bot_instance = MagicMock()
        test_exception = Exception("Test error")
        mock_bot_instance.start = AsyncMock(side_effect=test_exception)
        mock_bot.return_value = mock_bot_instance

        with pytest.raises(Exception, match="Test error"):
            await main()

        mock_logger.error.assert_called_once_with(f"Критическая ошибка: {test_exception}")

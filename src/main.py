import asyncio
import logging

from .bot import TelegramBot
from .config import Config
from .database import DatabaseManager
from .llm_client import LLMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")],
)

logger = logging.getLogger(__name__)


async def main():
    config = Config()

    db = DatabaseManager(config.database_path)
    await db.connect()

    try:
        llm_client = LLMClient(
            base_url=config.llm_base_url,
            model=config.llm_model,
            system_prompt_file=config.system_prompt_file,
        )
        bot = TelegramBot(config.telegram_bot_token, llm_client, config.system_prompt_file, db)

        logger.info("Бот запущен")
        try:
            await bot.start()
        except KeyboardInterrupt:
            logger.info("Бот остановлен")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            raise
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

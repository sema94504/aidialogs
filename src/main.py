import asyncio
import logging

from bot import TelegramBot
from config import Config
from llm_client import LLMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")],
)

logger = logging.getLogger(__name__)


async def main():
    config = Config()
    llm_client = LLMClient(
        base_url=config.llm_base_url, model=config.llm_model, system_prompt=config.system_prompt
    )
    bot = TelegramBot(config.telegram_bot_token, llm_client)

    logger.info("Бот запущен")
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

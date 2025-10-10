import asyncio
from config import Config
from bot import TelegramBot
from llm_client import LLMClient

async def main():
    config = Config()
    llm_client = LLMClient(
        base_url=config.llm_base_url,
        model=config.llm_model,
        system_prompt=config.system_prompt
    )
    bot = TelegramBot(config.telegram_bot_token, llm_client)
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())


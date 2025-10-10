import asyncio
from config import Config
from bot import TelegramBot

async def main():
    config = Config()
    bot = TelegramBot(config.telegram_bot_token)
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())


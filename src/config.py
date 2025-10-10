import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self._validate()
    
    def _validate(self):
        if not self.telegram_bot_token:
            raise ValueError('TELEGRAM_BOT_TOKEN не указан в .env')


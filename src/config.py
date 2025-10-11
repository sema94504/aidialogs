import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.llm_base_url = os.getenv("LLM_BASE_URL")
        self.llm_model = os.getenv("LLM_MODEL")
        self.system_prompt = os.getenv("SYSTEM_PROMPT")
        self._validate()

    def _validate(self):
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не указан в .env")
        if not self.llm_base_url:
            raise ValueError("LLM_BASE_URL не указан в .env")
        if not self.llm_model:
            raise ValueError("LLM_MODEL не указан в .env")
        if not self.system_prompt:
            raise ValueError("SYSTEM_PROMPT не указан в .env")

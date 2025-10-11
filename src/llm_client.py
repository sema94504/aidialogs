import logging

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, base_url: str, model: str, system_prompt: str):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model = model
        self.system_prompt = system_prompt

    def get_response(self, messages: list[dict]) -> str:
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(model=self.model, messages=full_messages)
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            logger.error(f"Ошибка LLM API: {e}")
            raise

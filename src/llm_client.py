import logging

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, base_url: str, model: str, system_prompt_file: str):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model = model
        self.system_prompt = self._read_prompt_file(system_prompt_file)

    def _read_prompt_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Файл промпта не найден: {file_path}")
            raise

    def get_response(self, messages: list[dict]) -> str:
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(model=self.model, messages=full_messages)
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            logger.error(f"Ошибка LLM API: {e}")
            raise

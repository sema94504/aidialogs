import logging
import time

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, base_url: str, model: str, system_prompt_file: str, max_retries: int = 3):
        self.client = OpenAI(base_url=base_url, api_key="not-needed", timeout=60.0)
        self.model = model
        self.system_prompt = self._read_prompt_file(system_prompt_file)
        self.max_retries = max_retries

    def _read_prompt_file(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.error(f"Файл промпта не найден: {file_path}")
            raise

    def get_response(self, messages: list[dict]) -> str:
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Запрос к LLM (попытка {attempt}/{self.max_retries})")
                response = self.client.chat.completions.create(
                    model=self.model, messages=full_messages
                )
                content = response.choices[0].message.content
                result = content if content is not None else ""
                logger.info(f"Ответ LLM (длина: {len(result)}): {result[:200]}...")
                return result
            except Exception as e:
                error_msg = f"Ошибка LLM API (попытка {attempt}/{self.max_retries})"
                logger.error(f"{error_msg}: {type(e).__name__}: {e}")
                if attempt < self.max_retries:
                    wait_time = attempt * 2
                    logger.info(f"Повтор через {wait_time}с...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Все {self.max_retries} попытки исчерпаны")
                    raise

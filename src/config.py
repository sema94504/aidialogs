from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    telegram_bot_token: str
    llm_base_url: str
    llm_model: str
    system_prompt_file: str = "prompts/system_prompt.txt"
    database_path: str = "aidialogs.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

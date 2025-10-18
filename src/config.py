from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse


class Config(BaseSettings):
    telegram_bot_token: str
    llm_base_url: str
    llm_model: str
    system_prompt_file: str = "prompts/system_prompt.txt"
    database_url: str = "sqlite:///aidialogs.db"
    use_mock_stats: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_path(self) -> str:
        """Parse database path from database_url."""
        if self.database_url.startswith("sqlite:///"):
            # sqlite:///path/to/db.db -> /path/to/db.db
            return self.database_url.replace("sqlite:///", "")
        elif self.database_url.startswith("sqlite:////"):
            # sqlite:////data/db.db -> /data/db.db (for Docker with absolute paths)
            return self.database_url.replace("sqlite:////", "/")
        else:
            # Fallback
            return "aidialogs.db"

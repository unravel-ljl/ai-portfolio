from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Portfolio"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    # D6 会用到，现在先留空
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    model_name: str = "deepseek-flash"


@lru_cache
def get_settings() -> Settings:
    return Settings()

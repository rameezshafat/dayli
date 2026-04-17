from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Dayli"
    environment: str = "development"
    api_prefix: str = "/v1"
    default_timezone: str = "UTC"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "llama3.2"
    cors_allow_origins: list[str] = ["*"]

    # Google Calendar OAuth2
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Dayli"
    environment: str = "development"
    api_prefix: str = "/v1"
    default_timezone: str = "UTC"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    cors_allow_origins: list[str] = ["*"]

    # Google Calendar OAuth2
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

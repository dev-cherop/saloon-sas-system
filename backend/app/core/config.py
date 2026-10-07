
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field


BACKEND_DIR = Path(__file__).resolve().parents[2]



class Settings(BaseSettings):
    database_url: str

    jwt_secret_key: str = Field(min_length=32)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resume_analyzer"
    ANALYSIS_API_KEY: str = "placeholder"
    ANALYSIS_MODEL: str = "claude-sonnet-4-6"
    ALLOWED_ORIGINS: List[str] = ["*"]
    APP_NAME: str = "Resume Analyzer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False


settings = Settings()

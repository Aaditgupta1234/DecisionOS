"""Application configuration settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "DecisionOS API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # Database Settings
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/decisionos"

    # Security & JWT Settings
    SECRET_KEY: str = "development_secret_key_change_in_production_4f89d3a7e2b10"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 60 minutes for development

    # Storage & Upload Settings
    UPLOAD_DIR: str = "uploads/datasets"
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50MB

    # LLM Settings
    OLLAMA_URL: str = "http://localhost:11434"

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite Dev Server
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

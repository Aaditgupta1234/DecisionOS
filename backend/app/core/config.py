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

    # Diagnostic Engine Configurable Thresholds (Phase 5.5)
    # 1. Revenue Thresholds
    REVENUE_DECLINE_THRESHOLD: float = 0.15  # 15% period-over-period drop
    REVENUE_STAGNATION_THRESHOLD: float = 0.02  # 2% growth ceiling for stagnation
    REVENUE_GROWTH_THRESHOLD: float = 0.20  # 20% growth acceleration trigger
    REVENUE_VOLATILITY_THRESHOLD: float = 0.30  # 30% coefficient of variation

    # 2. Customer Thresholds
    CHURN_ALERT_THRESHOLD: float = 0.10  # 10% churn rate
    RETENTION_ALERT_THRESHOLD: float = 0.25  # 25% repeat purchase / retention rate floor
    CUSTOMER_SLOWDOWN_THRESHOLD: float = 0.05  # 5% new customer growth rate floor
    CUSTOMER_ACQUISITION_THRESHOLD: float = 0.25  # 25% acquisition surge trigger

    # 3. Operational Thresholds
    COST_SPIKE_THRESHOLD: float = 0.20  # 20% cost surge
    MARGIN_COMPRESSION_THRESHOLD: float = 0.05  # 5% margin drop
    OPERATIONAL_DELAY_THRESHOLD: float = 5.0  # 5.0 days average delivery time
    OPERATIONAL_CANCELLATION_THRESHOLD: float = 0.15  # 15% cancellation rate

    # 4. Product Thresholds
    PRODUCT_CONCENTRATION_THRESHOLD: float = 0.50  # 50% top product revenue share
    PRODUCT_UNDERPERFORMANCE_THRESHOLD: float = 0.05  # 5% revenue share floor
    PRODUCT_GROWTH_THRESHOLD: float = 0.30  # 30% category growth trigger
    PRODUCT_DECLINE_THRESHOLD: float = 0.20  # 20% category revenue decline trigger

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

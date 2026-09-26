import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Server
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    PROJECT_NAME: str = "CareerRadar API"
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/careerradar_db"
    TEST_DATABASE_URL: Optional[str] = None

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Security & JWT
    JWT_SECRET: str = "super-secret-jwt-key-replace-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # SerpApi (Google Jobs)
    SERPAPI_API_KEY: Optional[str] = None
    SERPAPI_MOCK_MODE: bool = False

    # LLM Provider
    LLM_PROVIDER: str = "gemini"  # "mock" | "openai" | "gemini" | "anthropic"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"

    # Freshness & Cache Configuration (Maximum 60 days / 2 months recency validation)
    MAX_JOB_AGE_DAYS: int = 60
    SERPAPI_DATE_POSTED_CHIP: str = "date_posted:month"
    JOB_FRESHNESS_DAYS_TTL: int = 14
    SEARCH_CACHE_HOURS_TTL: int = 12
    STALE_JOB_DAYS_THRESHOLD: int = 60

    # Central Job Database Scheduled Refresh Configuration
    JOB_DATABASE_REFRESH_DAY: str = "MONDAY"
    JOB_DATABASE_REFRESH_TIME: str = "10:00"
    JOB_DATABASE_TIMEZONE: str = "Asia/Kolkata"

    # SMTP Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "alerts@careerradar.io"
    SMTP_FROM_NAME: str = "CareerRadar Job Radar"
    SMTP_USE_TLS: bool = True
    MAX_WEEKLY_EMAIL_JOBS: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()

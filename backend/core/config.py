from pathlib import Path
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve project root (backend/../ = project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Job Apply Portal"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-super-secret-key-that-should-be-changed"

    # Database
    MONGO_URL: str = "mongodb://aijob:aijob_secret_2024@localhost:27017"
    MONGO_DB: str = "ai_job_portal"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # External APIs
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Storage Paths
    STORAGE_RESUMES: str = "storage/resumes"
    STORAGE_SCREENSHOTS: str = "storage/screenshots"
    STORAGE_LOGS: str = "storage/logs"

    # Worker/Crawler Settings
    MAX_BROWSER_SESSIONS: int = 3
    DEFAULT_RATE_LIMIT_PER_SITE: int = 5
    APPLY_RETRY_MAX: int = 2
    CRAWL_INTERVAL_MINUTES: int = 60

    # AI Match Score Thresholds (0-100 scale)
    SCORE_AUTO_APPLY: int = 90
    SCORE_MATCHED: int = 75
    SCORE_PARTIAL: int = 60

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

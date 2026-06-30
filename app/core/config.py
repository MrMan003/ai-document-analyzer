"""
Application configuration with validation.
"""
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "AI Document Analyzer"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    STORAGE_BACKEND: str = "local"

    # AWS S3 (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None

    # Azure Blob (optional)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = None

    # Anthropic API
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ANTHROPIC_MAX_TOKENS: int = 4000
    ANTHROPIC_TEMPERATURE: float = 0.3

    # Azure AD
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    AZURE_TENANT_ID: str = ""
    AZURE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    AZURE_SCOPES: List[str] = ["User.Read"]

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_TIME_LIMIT: int = 3600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3000

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def azure_authority_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.AZURE_TENANT_ID}"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("sqlite"):
            return v
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be postgresql or sqlite")
        return v

    @field_validator("MAX_UPLOAD_SIZE_MB")
    @classmethod
    def validate_max_upload(cls, v: int) -> int:
        if v > 100:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be <= 100")
        return v


settings = Settings()
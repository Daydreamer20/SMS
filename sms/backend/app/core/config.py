"""
Configuration settings for the School Management System application.
"""

import secrets
from typing import Any, Dict, List, Optional
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    # Application settings
    APP_NAME: str = "School Management System"
    ENVIRONMENT: str = "development"  # development, testing, staging, production
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api"
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"

    # Backend settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # CORS settings
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        """Validate CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security settings
    @field_validator("DOCS_URL", "REDOC_URL", mode="before")
    def disable_docs_in_production(cls, v: str, info) -> Optional[str]:
        """Disable API docs in production."""
        if info.data.get("ENVIRONMENT") == "production":
            return None
        return v

    # Database settings
    DATABASE_URL: Optional[str] = None
    DB_DRIVER: str = "postgresql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "sms_db"
    DB_SCHEMA: str = "public"
    DB_POOL_SIZE: int = 5
    DB_ECHO: bool = False

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Assemble database connection string."""
        if self.DATABASE_URL:
            # Use DATABASE_URL if provided (for Railway, Heroku, etc.)
            if "postgresql://" in self.DATABASE_URL:
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            return self.DATABASE_URL
        elif self.ENVIRONMENT == "development":
            # Use SQLite for local development
            return "sqlite+aiosqlite:///./sms_dev.db"
        else:
            # Build PostgreSQL URL from individual components
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your_super_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v: str, info) -> str:
        """Validate JWT secret key in production."""
        if info.data.get("ENVIRONMENT") == "production" and v == "your_super_secret_key_here":
            raise ValueError("JWT_SECRET_KEY must be changed in production")
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v

    # Security Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    SECURITY_HEADERS_ENABLED: bool = True

    # Redis Configuration (for caching and rate limiting)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        """Assemble Redis connection string."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # Testing settings
    TEST_DB_NAME: str = "sms_test_db"

    @property
    def SQLALCHEMY_TEST_DATABASE_URI(self) -> Optional[PostgresDsn]:
        """Assemble test database connection string."""
        return PostgresDsn.build(
            scheme=f"{self.DB_DRIVER}+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=f"/{self.TEST_DB_NAME}",
        )

    def get_environment_variables(self) -> Dict[str, Any]:
        """Return all environment variables as a dictionary."""
        return self.model_dump()


# Create global settings object
settings = Settings() 
"""
Configuration settings for the School Management System application.
"""

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
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

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

    # Database settings
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
    def SQLALCHEMY_DATABASE_URI(self) -> Optional[PostgresDsn]:
        """Assemble database connection string."""
        return PostgresDsn.build(
            scheme=f"{self.DB_DRIVER}+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=f"/{self.DB_NAME}",
        )

    # JWT Authentication
    JWT_SECRET_KEY: str = "your_super_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

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
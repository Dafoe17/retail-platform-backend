"""Application configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import Union, List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Online Shop API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://retail_user:retail_password@localhost:5433/retail_shop"

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def convert_database_url(cls, v: str) -> str:
        """Convert postgresql:// to postgresql+asyncpg:// for asyncpg driver"""
        if not v:
            return v

        # Convert to asyncpg format
        if v.startswith('postgresql://') and '+asyncpg' not in v:
            v = v.replace('postgresql://', 'postgresql+asyncpg://', 1)

        # Add SSL for external databases (Supabase, etc.)
        if 'supabase' in v or 'render.com' in v:
            if '?' not in v:
                v = v + '?ssl=require'
            elif 'ssl' not in v:
                v = v + '&ssl=require'

        return v

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS_ORIGINS from string to list"""
        if isinstance(v, str):
            # Allow all origins
            if v.strip() == "*":
                return ["*"]
            # Split by comma
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    """Get settings (singleton)"""
    return Settings()

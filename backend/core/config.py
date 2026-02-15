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

        # For Supabase: use Session Pooler (port 6543) and add required params
        if 'supabase' in v:
            # Replace port 5432 with 6543 for Session Pooler
            v = v.replace(':5432/', ':6543/')
            # Remove existing query params
            if '?' in v:
                base, params = v.split('?', 1)
                v = base
            # Add required params for Supabase pooler
            v = v + '?ssl=require&pgbouncer=true'

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

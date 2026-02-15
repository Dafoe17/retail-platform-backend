"""Подключение к базе данных"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from .config import get_settings

settings = get_settings()

# Parse DATABASE_URL and set connect_args
db_url = settings.DATABASE_URL
connect_args = {}

# For Supabase/Neon: extract params and set connect_args
if 'supabase' in db_url or 'neon.tech' in db_url:
    # Remove query params from URL (asyncpg doesn't parse them)
    if '?' in db_url:
        base_url, params_str = db_url.split('?', 1)
        db_url = base_url

        # Parse params
        params = {}
        for param in params_str.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value

        # Set connect_args for asyncpg
        if params.get('ssl') == 'require':
            connect_args['ssl'] = True
        if params.get('pgbouncer') == 'true':
            # For Supabase pooler - use server-side binding
            connect_args['server_settings'] = {'statement_cache_mode': 'describe'}

# Async engine
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args if connect_args else None,
)

# Async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Базовая класс для всех моделей"""
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию БД (для dependency injection)"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

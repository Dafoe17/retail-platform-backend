"""Подключение к базе данных"""
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from .config import get_settings

settings = get_settings()

# Determine if SSL is needed
connect_args = {}
if 'ssl=require' in settings.DATABASE_URL or 'supabase' in settings.DATABASE_URL:
    # Remove ssl param from URL (asyncpg doesn't parse it from URL)
    db_url = settings.DATABASE_URL.replace('?ssl=require', '').replace('&ssl=require', '')
    connect_args['ssl'] = True
else:
    db_url = settings.DATABASE_URL

# Async engine
engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
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

"""
INDRA — Database session factory (Step 3 foundation)

Provides an async SQLAlchemy engine and session factory.
Business-logic repositories are NOT implemented here.
This module only establishes the database connection.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,   # SQL logging in development
    pool_pre_ping=True,        # verify connection before use
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base. Models will extend this in later steps."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields a database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Lightweight connectivity check.
    Returns True if the database is reachable, False otherwise.
    Used by the /health endpoint.
    """
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

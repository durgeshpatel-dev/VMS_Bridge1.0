from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def get_engine() -> AsyncEngine:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in your .env (see .env.example)."
        )

    # Convert sync database URL to async if needed
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

    return create_async_engine(
        database_url,
        pool_pre_ping=True,
    )


_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine_and_sessionmaker() -> None:
    global _engine, _async_session_factory

    if _engine is None:
        _engine = get_engine()
        _async_session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    init_engine_and_sessionmaker()
    assert _async_session_factory is not None

    async with _async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

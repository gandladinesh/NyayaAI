"""
Database engine and session management.
SQLite (Phase 1) → PostgreSQL ready.

To migrate: change DATABASE_URL in .env to a PostgreSQL URL.
No changes to this file or any model are needed.
"""

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create async engine — works for both SQLite and PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    # SQLite-specific: needed for async SQLite only, ignored by PostgreSQL
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables() -> None:
    """Create all tables on startup. Idempotent."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """FastAPI dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session

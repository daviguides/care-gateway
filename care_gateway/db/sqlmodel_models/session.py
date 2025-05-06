import os

from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

# Database URL — you can override this via environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://admin:admin@localhost:5432/claims_db"
)

# # --- SQLModel setup (used by FastAPI) ---
sqlmodel_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=sqlmodel_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_sqlmodel_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


def create_test_session_local(engine: AsyncEngine):
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def init_sqlmodel_db():
    """Create all SQLModel tables (for development and testing only)."""
    from care_gateway.db.sqlmodel_models import models

    async with sqlmodel_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def dispose_db():
    await sqlmodel_engine.dispose()

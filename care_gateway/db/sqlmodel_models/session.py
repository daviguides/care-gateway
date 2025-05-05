from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

# Default database URL
DATABASE_URL = "postgresql+psycopg://admin:admin@localhost:5432/claims_db"

# Global objects used by the application
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency function to get a session (FastAPI will override this in tests)
async def get_sqlmodel_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Optional factory for tests
def create_test_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, echo=True)


def create_test_session_local(engine: AsyncEngine):
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

from contextlib import asynccontextmanager

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from care_gateway.api_fastapi.app import app
from care_gateway.db.sqlmodel_models.session import (
    get_sqlmodel_session as get_session_original,
)
from care_gateway.utils.create_test_db import create_database

# Test database config
TEST_DB_NAME = "claims_test_db"
TEST_DATABASE_URL = f"postgresql+psycopg://admin:admin@localhost:5432/{TEST_DB_NAME}"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocalTest = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    create_database()


@pytest.fixture
def engine_fixture():
    return engine_test


@pytest.fixture(scope="function", autouse=True)
async def override_get_session():
    async def get_test_session() -> AsyncSession:
        async with AsyncSessionLocalTest() as session:
            yield session

    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    app.dependency_overrides[get_session_original] = get_test_session

    yield

    # Clear data after test
    async with engine_test.begin() as conn:
        for table in reversed(SQLModel.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest.fixture
async def client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as ac:
            yield ac

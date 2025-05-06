import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from care_gateway.db.sqlmodel_models.session import (
    create_test_session_local,
    dispose_db,
    get_sqlmodel_session,
    init_sqlmodel_db,
)


@pytest.mark.asyncio
async def test_get_sqlmodel_session_yields():
    session_gen = get_sqlmodel_session()
    session = await anext(session_gen)  # força o yield
    assert session is not None
    await session.aclose()


def test_create_test_session_local():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = create_test_session_local(engine)
    assert callable(session_factory)


@pytest.mark.asyncio
async def test_init_sqlmodel_db_executes():
    await init_sqlmodel_db()


@pytest.mark.asyncio
async def test_dispose_db_executes():
    await dispose_db()

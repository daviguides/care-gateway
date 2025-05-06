from care_gateway.db.sqlalchemy_models.session import (
    get_sqlalchemy_session,
    get_sync_session,
)


def test_get_sqlalchemy_session():
    gen = get_sqlalchemy_session()
    session = next(gen)
    assert session is not None
    session.close()


def test_get_sync_session():
    session = get_sync_session()
    assert session is not None
    session.close()

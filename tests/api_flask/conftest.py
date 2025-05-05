import pytest
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from care_gateway.api_flask.app import create_app
from care_gateway.db.sqlalchemy_models.models import Base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database as sa_create_database


def create_database(database_url: str):
    engine = create_engine(database_url)
    if not database_exists(engine.url):
        sa_create_database(engine.url)


TEST_DB_URL = "postgresql+psycopg://admin:admin@localhost:5432/claims_test_db_test"


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    # Só cria o banco se ele não existir
    create_database(TEST_DB_URL)
    # Só agora criamos o engine
    engine = create_engine(TEST_DB_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Guarda o engine para outros fixtures
    global _engine
    _engine = engine


@pytest.fixture(scope="function")
def db_session():
    SessionLocal = sessionmaker(bind=_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session) -> FlaskClient:
    app = create_app(testing=True, db_session=db_session)
    with app.test_client() as client:
        yield client

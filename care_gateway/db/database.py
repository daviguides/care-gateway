import os
from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session as SQLModelSession

# Database URL — you can override this via environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://admin:admin@localhost:5432/claims_db"
)

# --- SQLAlchemy setup (used by Flask) ---
sqlalchemy_engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlalchemy_engine)


def get_session():
    return current_app.config.get(
        "DB_SESSION",
    ) or next(
        get_sqlalchemy_session(),
    )


def get_sqlalchemy_session():
    """Yield a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- SQLModel setup (used by FastAPI) ---
sqlmodel_engine = create_engine(DATABASE_URL, echo=False)


def get_sqlmodel_session():
    """Yield a SQLModel session."""
    with SQLModelSession(sqlmodel_engine) as session:
        yield session


def init_sqlmodel_db():
    """Create all SQLModel tables (for development and testing only)."""
    from care_gateway.db.sqlmodel_models import models

    SQLModel.metadata.create_all(sqlmodel_engine)

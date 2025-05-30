import os

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Environment-configured database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://admin:admin@localhost:5432/claims_db"
)

# Create engine
sqlalchemy_engine = create_engine(
    DATABASE_URL,
    future=True,
)

# Session factory
SessionFactory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sqlalchemy_engine,
)

# Scoped session (for Flask web requests)
SessionLocal = scoped_session(SessionFactory)


def get_session():
    return current_app.config.get(
        "DB_SESSION",
    ) or next(
        get_sqlalchemy_session(),
    )


def get_sqlalchemy_session():
    """Yield a scoped session for use in Flask routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sync_session():
    """Return a regular SQLAlchemy session for background use (e.g., gRPC, scripts)."""
    return SessionFactory()

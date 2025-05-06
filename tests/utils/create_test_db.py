import psycopg
from urllib.parse import urlparse
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://admin:admin@localhost:5432/claims_test_db"
)


def parse_sqlalchemy_url_to_psycopg_dsn(
    sqlalchemy_url: str, db_override: str = None
) -> str:
    parsed = urlparse(sqlalchemy_url.replace("postgresql+psycopg", "postgresql"))
    dbname = db_override if db_override else parsed.path.lstrip("/")
    return (
        f"dbname={dbname} "
        f"user={parsed.username} "
        f"password={parsed.password} "
        f"host={parsed.hostname} "
        f"port={parsed.port}"
    )


def create_database(database_url=DATABASE_URL):
    parsed = urlparse(DATABASE_URL.replace("postgresql+psycopg", "postgresql"))
    db_name = parsed.path.lstrip("/")
    print(f"Target DB: {db_name}")

    dsn_admin = parse_sqlalchemy_url_to_psycopg_dsn(
        DATABASE_URL, db_override="postgres"
    )

    with psycopg.connect(dsn_admin, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                print(f"Creating database {db_name}...")
                cur.execute(f"CREATE DATABASE {db_name}")
            else:
                print(f"Database {db_name} already exists.")


def drop_database_if_exists(db_name: str, admin_dsn: str):
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
                (db_name,),
            )
            cur.execute("DROP DATABASE IF EXISTS %s" % db_name)


if __name__ == "__main__":
    create_database()

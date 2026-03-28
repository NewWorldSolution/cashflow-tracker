import os

import pytest


PG_URL = os.getenv("DATABASE_URL", "")


@pytest.fixture
def pg_db():
    if not PG_URL.startswith(("postgresql://", "postgres://")):
        pytest.skip("PostgreSQL DATABASE_URL not set")

    import psycopg2

    conn = psycopg2.connect(PG_URL)
    try:
        from db.init_db import initialise_db

        initialise_db(conn)
        yield conn
    finally:
        conn.close()

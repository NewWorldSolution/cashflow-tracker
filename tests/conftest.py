import os

import pytest

PG_URL = os.getenv("DATABASE_URL", "")


@pytest.fixture
def pg_db():
    if not PG_URL.startswith(("postgresql://", "postgres://")):
        pytest.skip("PostgreSQL DATABASE_URL not set")

    from db.init_db import initialise_db
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    from app.main import _connect

    wrapped = _connect(PG_URL)
    try:
        initialise_db(wrapped)
        yield wrapped
    finally:
        wrapped.close()

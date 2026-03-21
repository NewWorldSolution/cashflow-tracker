"""
Tests for I1-T1 (schema + seed) and I1-T3 (opening balance route).
All tests use isolated in-memory databases or TestClient with tmp_path.
"""
import sqlite3
import pytest
from fastapi.testclient import TestClient

from db.init_db import initialise_db


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Fresh in-memory SQLite database, fully initialised."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialise_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def client(tmp_path):
    """TestClient with a temporary database — isolated per test."""
    import os
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = f"sqlite:///./{db_path}"

    from app.main import create_app
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c


# ── schema + seed tests (I1-T1) ───────────────────────────────────────────────

def test_init_db_creates_all_tables(db):
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"users", "categories", "transactions", "settings", "settings_audit"}.issubset(tables)


def test_init_db_is_idempotent(db):
    """Running initialise_db twice must not create duplicate rows."""
    initialise_db(db)  # second run
    category_count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert category_count == 22
    assert user_count == 3


def test_categories_count_is_22(db):
    count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    assert count == 22


def test_categories_income_count_is_4(db):
    count = db.execute(
        "SELECT COUNT(*) FROM categories WHERE direction = 'income'"
    ).fetchone()[0]
    assert count == 4


def test_categories_expense_count_is_18(db):
    count = db.execute(
        "SELECT COUNT(*) FROM categories WHERE direction = 'expense'"
    ).fetchone()[0]
    assert count == 18


def test_users_count_is_3(db):
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 3


def test_users_passwords_are_hashed(db):
    """Passwords must be bcrypt hashes — never plaintext."""
    hashes = db.execute("SELECT password_hash FROM users").fetchall()
    assert len(hashes) == 3
    for row in hashes:
        h = row[0]
        assert h.startswith("$2b$"), (
            f"Expected bcrypt hash starting with '$2b$', got: {h!r}. "
            "Plaintext passwords must never be stored."
        )


# ── opening balance route tests (I1-T3) ───────────────────────────────────────

def test_opening_balance_saves_to_settings(client):
    response = client.post(
        "/settings/opening-balance",
        data={"opening_balance": "50000.00", "as_of_date": "2026-01-01"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    # Verify DB directly — status code alone is insufficient
    import sqlite3
    import os
    db_path = os.environ.get("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT value FROM settings WHERE key = 'opening_balance'").fetchone()
    conn.close()
    assert row is not None
    assert float(row[0]) == 50000.00


def test_opening_balance_writes_audit_row(client):
    client.post(
        "/settings/opening-balance",
        data={"opening_balance": "50000.00", "as_of_date": "2026-01-01"},
        follow_redirects=False,
    )
    import sqlite3
    import os
    db_path = os.environ.get("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT key, old_value, new_value FROM settings_audit ORDER BY id"
    ).fetchall()
    conn.close()
    keys = [r[0] for r in rows]
    assert "opening_balance" in keys
    # First write: old_value must be NULL
    balance_row = next(r for r in rows if r[0] == "opening_balance")
    assert balance_row[1] is None, (
        f"old_value must be NULL on first write, got: {balance_row[1]!r}"
    )


def test_opening_balance_rejects_negative(client):
    response = client.post(
        "/settings/opening-balance",
        data={"opening_balance": "-100", "as_of_date": "2026-01-01"},
    )
    assert response.status_code == 400


def test_missing_opening_balance_redirects(client):
    """Any protected route must redirect to opening balance when balance is not set."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/settings/opening-balance" in response.headers["location"]

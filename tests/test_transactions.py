import os
import sqlite3

import pytest
from fastapi.testclient import TestClient


INCOME_CATEGORY_ID = 1
EXPENSE_CATEGORY_ID = 5
OTHER_EXPENSE_CATEGORY_ID = 22


@pytest.fixture
def client(tmp_path):
    """Opening balance pre-set. Authenticated as 'owner'. db_path accessible as client.db_path."""
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"

    from app.main import create_app

    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        c.db_path = db_path
        c.post(
            "/settings/opening-balance",
            data={"opening_balance": "50000", "as_of_date": "2026-01-01"},
            follow_redirects=True,
        )
        c.post("/auth/login", data={"username": "owner", "password": "owner123"})
        yield c


@pytest.fixture
def logged_out_client(tmp_path):
    """Opening balance pre-set. NOT authenticated (no login step)."""
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"

    from app.main import create_app

    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        c.post(
            "/settings/opening-balance",
            data={"opening_balance": "50000", "as_of_date": "2026-01-01"},
            follow_redirects=True,
        )
        yield c


def valid_income_form(**overrides):
    data = {
        "date": "2026-01-15",
        "direction": "income",
        "amount": "1000.00",
        "category_id": str(INCOME_CATEGORY_ID),
        "payment_method": "transfer",
        "vat_rate": "23",
        "income_type": "external",
        "vat_deductible_pct": "",
        "description": "",
    }
    data.update(overrides)
    return data


def valid_expense_form(**overrides):
    data = {
        "date": "2026-01-15",
        "direction": "expense",
        "amount": "500.00",
        "category_id": str(EXPENSE_CATEGORY_ID),
        "payment_method": "card",
        "vat_rate": "23",
        "income_type": "",
        "vat_deductible_pct": "100",
        "description": "",
    }
    data.update(overrides)
    return data


def test_create_form_loads(client):
    r = client.get("/transactions/new")

    assert r.status_code == 200


def test_create_transaction_success_redirects(client):
    r = client.post("/transactions/new", data=valid_income_form())

    assert r.status_code == 302
    assert r.headers["location"] == "/transactions/"


def test_create_transaction_saves_to_db(client):
    response = client.post("/transactions/new", data=valid_expense_form())

    assert response.status_code == 302

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM transactions").fetchone()
    conn.close()

    assert row is not None
    assert row["direction"] == "expense"
    assert row["category_id"] == EXPENSE_CATEGORY_ID
    assert row["vat_deductible_pct"] == 100.0


def test_logged_by_set_from_session_not_form(client):
    response = client.post(
        "/transactions/new",
        data=valid_income_form(logged_by="999"),
    )

    assert response.status_code == 302

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT logged_by FROM transactions").fetchone()
    conn.close()

    assert row["logged_by"] != 999
    assert row["logged_by"] == 1


def test_create_transaction_shows_all_errors(client):
    r = client.post(
        "/transactions/new",
        data=valid_income_form(category_id="", payment_method="cheque"),
    )

    assert r.status_code == 422
    assert "Category must be a valid category id." in r.text
    assert "Payment method must be cash, card, or transfer." in r.text


def test_form_input_preserved_on_error(client):
    r = client.post(
        "/transactions/new",
        data=valid_income_form(payment_method="cheque", description="test note"),
    )

    assert r.status_code == 422
    assert "test note" in r.text


def test_internal_income_vat_rate_enforced(client):
    r = client.post(
        "/transactions/new",
        data=valid_income_form(income_type="internal", vat_rate="23"),
    )

    assert r.status_code == 422
    assert "Internal income must use a VAT rate of 0." in r.text


def test_other_expense_description_required(client):
    r = client.post(
        "/transactions/new",
        data=valid_expense_form(category_id=str(OTHER_EXPENSE_CATEGORY_ID)),
    )

    assert r.status_code == 422
    assert "Description is required for other_expense and other_income." in r.text


def test_transaction_list_loads(client):
    r = client.get("/transactions/")

    assert r.status_code == 200


def test_transaction_list_shows_recent(client):
    create = client.post(
        "/transactions/new",
        data=valid_income_form(amount="1234.56"),
    )
    r = client.get("/transactions/")

    assert create.status_code == 302
    assert r.status_code == 200
    assert "1234.56" in r.text


def test_transaction_list_excludes_inactive(client):
    conn = sqlite3.connect(client.db_path)
    conn.execute(
        "INSERT INTO transactions (date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, logged_by, is_active, void_reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("2026-01-01", "9876.54", "income", INCOME_CATEGORY_ID, "cash", 23, "external", 1, 0, "test void"),
    )
    conn.commit()
    conn.close()

    r = client.get("/transactions/")

    assert r.status_code == 200
    assert "9876.54" not in r.text


def test_transaction_list_ordered_by_created_at(client):
    conn = sqlite3.connect(client.db_path)
    conn.execute(
        "INSERT INTO transactions (date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, logged_by, is_active, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("2026-01-01", "111.11", "income", INCOME_CATEGORY_ID, "cash", 23, "external", 1, 1, "2026-01-01 10:00:00"),
    )
    conn.execute(
        "INSERT INTO transactions (date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, logged_by, is_active, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("2026-01-02", "222.22", "income", INCOME_CATEGORY_ID, "transfer", 23, "external", 1, 1, "2026-01-01 11:00:00"),
    )
    conn.commit()
    conn.close()

    r = client.get("/transactions/")

    assert r.status_code == 200
    assert r.text.index("222.22") < r.text.index("111.11")


def test_categories_endpoint_returns_json(client):
    r = client.get("/categories")
    data = r.json()

    assert r.status_code == 200
    assert isinstance(data, list)
    assert data
    assert {
        "category_id",
        "name",
        "label",
        "direction",
        "default_vat_rate",
        "default_vat_deductible_pct",
    }.issubset(data[0].keys())


def test_unauthenticated_create_redirects(logged_out_client):
    r = logged_out_client.get("/transactions/new")

    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]

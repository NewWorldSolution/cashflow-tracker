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


def insert_transaction(client, **overrides):
    data = {
        "date": "2026-01-15",
        "amount": "500.00",
        "direction": "expense",
        "category_id": EXPENSE_CATEGORY_ID,
        "payment_method": "card",
        "vat_rate": 23,
        "income_type": None,
        "vat_deductible_pct": 100,
        "description": "Original transaction",
        "logged_by": 1,
        "is_active": 1,
        "void_reason": None,
        "voided_by": None,
        "replacement_transaction_id": None,
        "created_at": "2026-01-15 10:00:00",
    }
    data.update(overrides)

    conn = sqlite3.connect(client.db_path)
    cursor = conn.execute(
        "INSERT INTO transactions (date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, vat_deductible_pct, description, logged_by, is_active, "
        "void_reason, voided_by, replacement_transaction_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            data["amount"],
            data["direction"],
            data["category_id"],
            data["payment_method"],
            data["vat_rate"],
            data["income_type"],
            data["vat_deductible_pct"],
            data["description"],
            data["logged_by"],
            data["is_active"],
            data["void_reason"],
            data["voided_by"],
            data["replacement_transaction_id"],
            data["created_at"],
        ),
    )
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id


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


def test_detail_view_returns_200(client):
    transaction_id = insert_transaction(client, amount="654.32")

    r = client.get(f"/transactions/{transaction_id}")

    assert r.status_code == 200
    assert "654.32" in r.text
    assert f"Transaction #{transaction_id}" in r.text


def test_detail_view_404_for_missing(client):
    r = client.get("/transactions/99999")

    assert r.status_code == 404


def test_void_form_loads(client):
    transaction_id = insert_transaction(client)

    r = client.get(f"/transactions/{transaction_id}/void")

    assert r.status_code == 200
    assert 'name="void_reason"' in r.text


def test_void_requires_void_reason(client):
    transaction_id = insert_transaction(client)

    r = client.post(f"/transactions/{transaction_id}/void", data={"void_reason": "   "})

    assert r.status_code == 422
    assert "Void reason is required." in r.text


def test_void_success(client):
    transaction_id = insert_transaction(client)

    r = client.post(
        f"/transactions/{transaction_id}/void",
        data={"void_reason": "Duplicate entry"},
    )

    assert r.status_code == 302
    assert r.headers["location"] == "/transactions/"

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT is_active, void_reason, voided_by FROM transactions WHERE id = ?",
        (transaction_id,),
    ).fetchone()
    conn.close()

    assert row["is_active"] == 0
    assert row["void_reason"] == "Duplicate entry"
    assert row["voided_by"] == 1


def test_voided_transaction_excluded_from_list(client):
    transaction_id = insert_transaction(client, amount="777.77")

    void_response = client.post(
        f"/transactions/{transaction_id}/void",
        data={"void_reason": "Entered twice"},
    )
    r = client.get("/transactions/")

    assert void_response.status_code == 302
    assert r.status_code == 200
    assert "777.77" not in r.text


def test_void_already_voided_rejected(client):
    transaction_id = insert_transaction(
        client,
        is_active=0,
        void_reason="Already voided",
        voided_by=1,
    )

    r = client.post(
        f"/transactions/{transaction_id}/void",
        data={"void_reason": "Try again"},
    )

    assert r.status_code == 422
    assert "Transaction is already voided." in r.text


def test_correct_form_prefills_original(client):
    transaction_id = insert_transaction(
        client,
        amount="888.88",
        vat_rate=23.0,
        vat_deductible_pct=100.0,
        description="Needs correction",
    )

    r = client.get(f"/transactions/{transaction_id}/correct")

    assert r.status_code == 200
    assert 'action="/transactions/%s/correct"' % transaction_id in r.text
    assert 'value="888.88"' in r.text
    assert 'option value="23"' in r.text
    assert 'option value="100"' in r.text
    assert "Needs correction" in r.text


def test_correct_creates_new_voids_original(client):
    transaction_id = insert_transaction(client, amount="500.00")

    r = client.post(
        f"/transactions/{transaction_id}/correct",
        data=valid_expense_form(amount="650.00", description="Corrected amount"),
    )

    assert r.status_code == 302
    assert r.headers["location"] == "/transactions/"

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, amount, is_active, void_reason, voided_by, replacement_transaction_id "
        "FROM transactions ORDER BY id"
    ).fetchall()
    conn.close()

    original = next(row for row in rows if row["id"] == transaction_id)
    replacements = [row for row in rows if row["id"] != transaction_id]

    assert len(replacements) == 1
    replacement = replacements[0]
    assert original["is_active"] == 0
    assert original["void_reason"] == "Corrected"
    assert original["voided_by"] == 1
    assert original["replacement_transaction_id"] == replacement["id"]
    assert replacement["is_active"] == 1
    assert replacement["amount"] == 650


def test_correct_on_voided_rejected(client):
    transaction_id = insert_transaction(
        client,
        is_active=0,
        void_reason="Already voided",
        voided_by=1,
    )

    r = client.get(f"/transactions/{transaction_id}/correct")

    assert r.status_code == 404

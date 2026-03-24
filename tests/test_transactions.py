import os
import sqlite3

import pytest
from fastapi.testclient import TestClient


CASH_IN_LEAF_ID = 101
CASH_OUT_LEAF_ID = 121
OTHER_EXPENSE_CATEGORY_ID = 162


@pytest.fixture
def client(tmp_path):
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


def valid_cash_in_form(**overrides):
    data = {
        "date": "2026-01-15",
        "direction": "cash_in",
        "amount": "1000.00",
        "category_id": str(CASH_IN_LEAF_ID),
        "company_id": "1",
        "payment_method": "card",
        "vat_mode": "automatic",
        "vat_rate": "23",
        "manual_vat_amount": "",
        "manual_vat_deductible_amount": "",
        "cash_in_type": "external",
        "vat_deductible_pct": "",
        "customer_type": "private",
        "document_flow": "receipt",
        "description": "",
        "for_accountant": "1",
    }
    data.update(overrides)
    return data


def valid_cash_out_form(**overrides):
    data = {
        "date": "2026-01-15",
        "direction": "cash_out",
        "amount": "500.00",
        "category_id": str(CASH_OUT_LEAF_ID),
        "company_id": "1",
        "payment_method": "card",
        "vat_mode": "automatic",
        "vat_rate": "23",
        "manual_vat_amount": "",
        "manual_vat_deductible_amount": "",
        "cash_in_type": "",
        "vat_deductible_pct": "100",
        "customer_type": "company",
        "document_flow": "",
        "description": "",
        "for_accountant": "1",
    }
    data.update(overrides)
    return data


def insert_transaction(client, **overrides):
    data = {
        "date": "2026-01-15",
        "amount": "500.00",
        "direction": "cash_out",
        "category_id": CASH_OUT_LEAF_ID,
        "company_id": 1,
        "payment_method": "card",
        "vat_rate": 23,
        "vat_mode": "automatic",
        "manual_vat_amount": None,
        "manual_vat_deductible_amount": None,
        "cash_in_type": None,
        "vat_deductible_pct": 100,
        "customer_type": "company",
        "document_flow": None,
        "description": "Original transaction",
        "for_accountant": 1,
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
        "INSERT INTO transactions (date, amount, direction, category_id, company_id, payment_method, "
        "vat_rate, vat_mode, manual_vat_amount, manual_vat_deductible_amount, cash_in_type, vat_deductible_pct, "
        "customer_type, document_flow, description, for_accountant, logged_by, is_active, void_reason, voided_by, "
        "replacement_transaction_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            data["amount"],
            data["direction"],
            data["category_id"],
            data["company_id"],
            data["payment_method"],
            data["vat_rate"],
            data["vat_mode"],
            data["manual_vat_amount"],
            data["manual_vat_deductible_amount"],
            data["cash_in_type"],
            data["vat_deductible_pct"],
            data["customer_type"],
            data["document_flow"],
            data["description"],
            data["for_accountant"],
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


def test_create_cash_in_transaction_with_new_fields(client):
    response = client.post("/transactions/new", data=valid_cash_in_form())
    assert response.status_code == 302

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    assert row["direction"] == "cash_in"
    assert row["cash_in_type"] == "external"
    assert row["customer_type"] == "private"
    assert row["document_flow"] == "receipt"


def test_create_cash_out_transaction_with_new_fields(client):
    response = client.post("/transactions/new", data=valid_cash_out_form())
    assert response.status_code == 302

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    assert row["direction"] == "cash_out"
    assert row["customer_type"] == "company"
    assert row["document_flow"] is None


def test_create_internal_cash_in_with_forced_values(client):
    response = client.post(
        "/transactions/new",
        data=valid_cash_in_form(
            cash_in_type="internal",
            payment_method="cash",
            vat_rate="0",
            customer_type="private",
            document_flow="",
            for_accountant="",
        ),
    )
    assert response.status_code == 302


def test_create_transaction_with_manual_vat_mode(client):
    response = client.post(
        "/transactions/new",
        data=valid_cash_out_form(
            vat_mode="manual",
            vat_rate="",
            vat_deductible_pct="",
            manual_vat_amount="46.00",
            manual_vat_deductible_amount="23.00",
        ),
    )
    assert response.status_code == 302


def test_for_accountant_defaults_true_on_create(client):
    response = client.post(
        "/transactions/new",
        data=valid_cash_out_form(for_accountant="1"),
    )
    assert response.status_code == 302

    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT for_accountant FROM transactions ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row["for_accountant"] == 1


def test_correct_preserves_stored_values(client):
    transaction_id = insert_transaction(
        client,
        direction="cash_in",
        category_id=CASH_IN_LEAF_ID,
        payment_method="card",
        vat_mode="manual",
        vat_rate=None,
        manual_vat_amount="46.00",
        manual_vat_deductible_amount=None,
        cash_in_type="external",
        vat_deductible_pct=None,
        customer_type="company",
        document_flow="invoice",
        for_accountant=0,
    )

    response = client.get(f"/transactions/{transaction_id}/correct")
    assert response.status_code == 200
    assert 'value="manual"' in response.text
    assert 'value="company" selected' in response.text
    assert 'value="invoice" selected' in response.text


def test_correct_allows_switching_vat_mode(client):
    transaction_id = insert_transaction(client)
    response = client.post(
        f"/transactions/{transaction_id}/correct",
        data={
            **valid_cash_out_form(
                vat_mode="manual",
                vat_rate="",
                vat_deductible_pct="",
                manual_vat_amount="46.00",
                manual_vat_deductible_amount="23.00",
            ),
            "correction_reason": "switch mode",
        },
    )
    assert response.status_code == 302


def test_correct_preselects_category_parent_and_child(client):
    transaction_id = insert_transaction(client, category_id=CASH_OUT_LEAF_ID)
    response = client.get(f"/transactions/{transaction_id}/correct")
    assert response.status_code == 200
    assert 'id="category_group"' in response.text
    assert f'data-selected-value="{CASH_OUT_LEAF_ID}"' in response.text


def test_list_view_shows_category_path_and_direction_labels(client):
    insert_transaction(client, direction="cash_out", category_id=CASH_OUT_LEAF_ID)
    response = client.get("/transactions/")
    assert response.status_code == 200
    assert "&gt;" in response.text or ">" in response.text
    assert "Wypływ" in response.text or "Wydatek" in response.text


def test_detail_view_shows_manual_vat_and_metadata(client):
    transaction_id = insert_transaction(
        client,
        vat_mode="manual",
        vat_rate=None,
        manual_vat_amount="46.00",
        manual_vat_deductible_amount="23.00",
        customer_type="company",
        document_flow="other_document",
    )
    response = client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 200
    assert "Ręczny VAT" in response.text or "Manual VAT" in response.text
    assert "Typ kontrahenta" in response.text or "Customer Type" in response.text
    assert "Obieg dokumentów" in response.text or "Document Flow" in response.text


def test_other_expense_description_required(client):
    response = client.post(
        "/transactions/new",
        data=valid_cash_out_form(category_id=str(OTHER_EXPENSE_CATEGORY_ID)),
    )
    assert response.status_code == 422


def test_categories_endpoint_returns_json(client):
    response = client.get("/categories")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert {
        "category_id",
        "name",
        "label",
        "direction",
        "default_vat_rate",
        "default_vat_deductible_pct",
    }.issubset(data[0].keys())


def test_dashboard_renders_translated_directions(client):
    insert_transaction(client, direction="cash_out", category_id=CASH_OUT_LEAF_ID)
    response = client.get("/")
    assert response.status_code == 200
    assert "Łączne wpływy" in response.text or "Total Cash In" in response.text
    assert "Łączne wypływy" in response.text or "Total Cash Out" in response.text

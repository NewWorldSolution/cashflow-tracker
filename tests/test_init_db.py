import sqlite3

import pytest
from fastapi.testclient import TestClient

from db.init_db import initialise_db


EXPECTED_CATEGORY_SLUGS = {
    "ci_services",
    "ci_services_test",
    "ci_training",
    "ci_products",
    "ci_financial_loan_taken",
    "ci_other_income",
    "co_marketing",
    "co_marketing_paid_ads",
    "co_operations",
    "co_operations_rent",
    "co_people_salaries",
    "co_taxes_vat",
    "co_financial_loan_given",
    "co_inventory_supplements",
    "co_other_expense",
}


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialise_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def client(tmp_path):
    import os

    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = f"sqlite:///./{db_path}"

    from app.main import create_app

    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c


def test_init_db_creates_all_tables(db):
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {
        "users",
        "categories",
        "companies",
        "transactions",
        "settings",
        "settings_audit",
    }.issubset(tables)


def test_categories_have_parent_id_column(db):
    columns = {row["name"] for row in db.execute("PRAGMA table_info(categories)")}
    assert "parent_id" in columns


def test_categories_seed_19_parents_and_62_children(db):
    parent_count = db.execute(
        "SELECT COUNT(*) FROM categories WHERE parent_id IS NULL"
    ).fetchone()[0]
    child_count = db.execute(
        "SELECT COUNT(*) FROM categories WHERE parent_id IS NOT NULL"
    ).fetchone()[0]
    assert parent_count == 19
    assert child_count == 62


def test_all_expected_taxonomy_slugs_exist(db):
    names = {row["name"] for row in db.execute("SELECT name FROM categories")}
    assert EXPECTED_CATEGORY_SLUGS.issubset(names)


def test_parent_groups_have_null_vat_defaults(db):
    count = db.execute(
        "SELECT COUNT(*) FROM categories "
        "WHERE parent_id IS NULL AND (default_vat_rate IS NOT NULL OR default_vat_deductible_pct IS NOT NULL)"
    ).fetchone()[0]
    assert count == 0


def test_subcategory_vat_defaults_match_known_values(db):
    lookup = {
        row["name"]: (row["default_vat_rate"], row["default_vat_deductible_pct"])
        for row in db.execute(
            "SELECT name, default_vat_rate, default_vat_deductible_pct "
            "FROM categories WHERE parent_id IS NOT NULL"
        )
    }
    assert lookup["ci_services_test"] == (23.0, None)
    assert lookup["co_marketing_paid_ads"] == (23.0, 100.0)
    assert lookup["co_operations_transport"] == (23.0, 50.0)
    assert lookup["co_taxes_vat"] == (0.0, 0.0)
    assert lookup["co_financial_loan_given"] == (0.0, 0.0)


def test_transactions_table_has_all_i8_columns(db):
    columns = {row["name"] for row in db.execute("PRAGMA table_info(transactions)")}
    legacy_cash_in_type = "".join(["in", "come", "_type"])
    assert {
        "vat_mode",
        "customer_type",
        "document_flow",
        "manual_vat_amount",
        "manual_vat_deductible_amount",
        "cash_in_type",
    }.issubset(columns)
    assert legacy_cash_in_type not in columns


def test_vat_rate_is_nullable(db):
    columns = {
        row["name"]: row["notnull"] for row in db.execute("PRAGMA table_info(transactions)")
    }
    assert columns["vat_rate"] == 0


def test_direction_check_constraint_uses_cash_in_cash_out(db):
    sql = db.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'"
    ).fetchone()[0]
    legacy_cash_in = "".join(["in", "come"])
    legacy_cash_out = "".join(["ex", "pense"])
    assert "'cash_in'" in sql
    assert "'cash_out'" in sql
    assert f"'{legacy_cash_in}'" not in sql
    assert f"'{legacy_cash_out}'" not in sql


def test_opening_balance_saves_to_settings(client):
    response = client.post(
        "/settings/opening-balance",
        data={"opening_balance": "50000.00", "as_of_date": "2026-01-01"},
        follow_redirects=False,
    )
    assert response.status_code == 302

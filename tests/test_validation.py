import sqlite3
from decimal import Decimal

import pytest

from app.services.validation import validate_transaction
from db.init_db import initialise_db


INCOME_CATEGORY_ID = 1
EXPENSE_CATEGORY_ID = 5
INTERNAL_TRANSFER_CATEGORY_ID = 3
OTHER_INCOME_CATEGORY_ID = 4
OTHER_EXPENSE_CATEGORY_ID = 22


@pytest.fixture
def db():
    """In-memory db seeded with categories and one test user set."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialise_db(conn)
    try:
        yield conn
    finally:
        conn.close()


def valid_income():
    return {
        "date": "2026-01-15",
        "direction": "income",
        "amount": Decimal("1000.00"),
        "category_id": INCOME_CATEGORY_ID,
        "payment_method": "transfer",
        "vat_rate": 23.0,
        "income_type": "external",
        "vat_deductible_pct": None,
        "description": None,
        "logged_by": 1,
        "is_active": True,
    }


def valid_expense():
    return {
        "date": "2026-01-15",
        "direction": "expense",
        "amount": Decimal("500.00"),
        "category_id": EXPENSE_CATEGORY_ID,
        "payment_method": "card",
        "vat_rate": 23.0,
        "income_type": None,
        "vat_deductible_pct": 100.0,
        "description": None,
        "logged_by": 1,
        "is_active": True,
    }


def test_valid_income_transaction_accepted(db):
    assert validate_transaction(valid_income(), db) == []


def test_valid_expense_transaction_accepted(db):
    assert validate_transaction(valid_expense(), db) == []


def test_internal_income_vat_zero_accepted(db):
    data = valid_income()
    data["income_type"] = "internal"
    data["vat_rate"] = 0.0
    data["payment_method"] = "cash"

    assert validate_transaction(data, db) == []


def test_internal_income_nonzero_vat_rejected(db):
    data = valid_income()
    data["income_type"] = "internal"

    errors = validate_transaction(data, db)

    assert "Internal income must use a VAT rate of 0." in errors


def test_expense_vat_rate_override_accepted(db):
    data = valid_expense()
    data["vat_rate"] = 5.0

    assert validate_transaction(data, db) == []


def test_expense_without_vat_deductible_pct_rejected(db):
    data = valid_expense()
    data["vat_deductible_pct"] = None

    errors = validate_transaction(data, db)

    assert (
        "VAT deductible percentage is required for expense transactions." in errors
    )


def test_income_with_vat_deductible_pct_rejected(db):
    data = valid_income()
    data["vat_deductible_pct"] = 100.0

    errors = validate_transaction(data, db)

    assert "VAT deductible percentage must be empty for income transactions." in errors


def test_income_without_income_type_rejected(db):
    data = valid_income()
    data["income_type"] = None

    errors = validate_transaction(data, db)

    assert "Income type is required for income transactions." in errors


def test_expense_with_income_type_rejected(db):
    data = valid_expense()
    data["income_type"] = "external"

    errors = validate_transaction(data, db)

    assert "Income type must be empty for expense transactions." in errors


def test_other_expense_without_description_rejected(db):
    data = valid_expense()
    data["category_id"] = OTHER_EXPENSE_CATEGORY_ID

    errors = validate_transaction(data, db)

    assert "Description is required for other_expense and other_income." in errors


def test_other_income_without_description_rejected(db):
    data = valid_income()
    data["category_id"] = OTHER_INCOME_CATEGORY_ID

    errors = validate_transaction(data, db)

    assert "Description is required for other_expense and other_income." in errors


def test_other_expense_with_description_accepted(db):
    data = valid_expense()
    data["category_id"] = OTHER_EXPENSE_CATEGORY_ID
    data["description"] = "Terminal maintenance"

    assert validate_transaction(data, db) == []


def test_invalid_category_id_rejected(db):
    data = valid_income()
    data["category_id"] = 9999

    errors = validate_transaction(data, db)

    assert "Category must be a valid category id." in errors


def test_direction_category_mismatch_rejected(db):
    data = valid_income()
    data["category_id"] = EXPENSE_CATEGORY_ID

    errors = validate_transaction(data, db)

    assert "Category direction must match transaction direction." in errors


def test_direction_category_match_accepted(db):
    assert validate_transaction(valid_income(), db) == []


def test_invalid_vat_rate_rejected(db):
    data = valid_income()
    data["vat_rate"] = 7.0

    errors = validate_transaction(data, db)

    assert "VAT rate must be one of 0, 5, 8, or 23." in errors


def test_invalid_payment_method_rejected(db):
    data = valid_income()
    data["payment_method"] = "cheque"

    errors = validate_transaction(data, db)

    assert "Payment method must be cash, card, or transfer." in errors


def test_invalid_vat_deductible_pct_rejected(db):
    data = valid_expense()
    data["vat_deductible_pct"] = 75.0

    errors = validate_transaction(data, db)

    assert "VAT deductible percentage must be one of 0, 50, or 100." in errors


def test_zero_amount_rejected(db):
    data = valid_income()
    data["amount"] = Decimal("0")

    errors = validate_transaction(data, db)

    assert "Amount must be greater than 0." in errors


def test_negative_amount_rejected(db):
    data = valid_income()
    data["amount"] = Decimal("-1.00")

    errors = validate_transaction(data, db)

    assert "Amount must be greater than 0." in errors


def test_invalid_date_format_rejected(db):
    data = valid_income()
    data["date"] = "not-a-date"

    errors = validate_transaction(data, db)

    assert "Date must be a valid YYYY-MM-DD value." in errors


def test_multiple_errors_returned_together(db):
    data = valid_income()
    data["payment_method"] = "cheque"
    data["vat_rate"] = 7.0

    errors = validate_transaction(data, db)

    assert "Payment method must be cash, card, or transfer." in errors
    assert "VAT rate must be one of 0, 5, 8, or 23." in errors
    assert len(errors) >= 2


def test_invalid_income_type_rejected(db):
    data = valid_income()
    data["income_type"] = "bogus"

    errors = validate_transaction(data, db)

    assert "Income type must be internal or external." in errors


def test_internal_transfer_category_rejected(db):
    data = valid_income()
    data["category_id"] = INTERNAL_TRANSFER_CATEGORY_ID
    data["income_type"] = "internal"
    data["vat_rate"] = 0.0

    errors = validate_transaction(data, db)

    assert "This category is not available for manual transactions." in errors


def test_internal_income_card_rejected(db):
    data = valid_income()
    data["income_type"] = "internal"
    data["vat_rate"] = 0.0
    data["payment_method"] = "card"

    errors = validate_transaction(data, db)

    assert "Internal income must use cash as payment method." in errors


def test_internal_income_transfer_rejected(db):
    data = valid_income()
    data["income_type"] = "internal"
    data["vat_rate"] = 0.0
    data["payment_method"] = "transfer"

    errors = validate_transaction(data, db)

    assert "Internal income must use cash as payment method." in errors


def test_internal_income_cash_accepted(db):
    data = valid_income()
    data["income_type"] = "internal"
    data["vat_rate"] = 0.0
    data["payment_method"] = "cash"

    errors = validate_transaction(data, db)

    assert errors == []

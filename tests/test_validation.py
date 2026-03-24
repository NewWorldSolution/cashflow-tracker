import sqlite3
from decimal import Decimal

import pytest

from app.services.validation import validate_transaction
from db.init_db import initialise_db


CASH_IN_LEAF_ID = 101
CASH_OUT_LEAF_ID = 121
CASH_IN_PARENT_ID = 1
CASH_OUT_PARENT_ID = 8
OTHER_INCOME_CATEGORY_ID = 120
OTHER_EXPENSE_CATEGORY_ID = 162


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialise_db(conn)
    try:
        yield conn
    finally:
        conn.close()


def valid_cash_in(**overrides):
    data = {
        "date": "2026-01-15",
        "direction": "cash_in",
        "amount": Decimal("1000.00"),
        "category_id": CASH_IN_LEAF_ID,
        "company_id": 1,
        "payment_method": "transfer",
        "vat_rate": "23",
        "vat_mode": "automatic",
        "manual_vat_amount": None,
        "manual_vat_deductible_amount": None,
        "cash_in_type": "external",
        "vat_deductible_pct": None,
        "customer_type": "private",
        "document_flow": "receipt",
        "description": None,
        "for_accountant": "",
        "logged_by": 1,
        "is_active": True,
    }
    data.update(overrides)
    return data


def valid_cash_out(**overrides):
    data = {
        "date": "2026-01-15",
        "direction": "cash_out",
        "amount": Decimal("500.00"),
        "category_id": CASH_OUT_LEAF_ID,
        "company_id": 1,
        "payment_method": "card",
        "vat_rate": "23",
        "vat_mode": "automatic",
        "manual_vat_amount": None,
        "manual_vat_deductible_amount": None,
        "cash_in_type": None,
        "vat_deductible_pct": "100",
        "customer_type": "company",
        "document_flow": None,
        "description": None,
        "for_accountant": "1",
        "logged_by": 1,
        "is_active": True,
    }
    data.update(overrides)
    return data


def test_valid_cash_in_transaction_accepted(db):
    assert validate_transaction(valid_cash_in(), db) == []


def test_valid_cash_out_transaction_accepted(db):
    assert validate_transaction(valid_cash_out(), db) == []


def test_vat_mode_automatic_requires_vat_rate(db):
    errors = validate_transaction(valid_cash_out(vat_rate=None), db)
    assert "VAT rate must be one of 0, 5, 8, or 23." in errors


def test_vat_mode_manual_requires_manual_vat_amount(db):
    errors = validate_transaction(
        valid_cash_out(
            vat_mode="manual",
            vat_rate=None,
            vat_deductible_pct=None,
            manual_vat_amount=None,
            manual_vat_deductible_amount="10.00",
        ),
        db,
    )
    assert "Manual VAT amount is required when VAT mode is manual." in errors


def test_vat_mode_manual_rejects_vat_rate(db):
    errors = validate_transaction(
        valid_cash_out(
            vat_mode="manual",
            vat_rate="23",
            vat_deductible_pct=None,
            manual_vat_amount="10.00",
            manual_vat_deductible_amount="10.00",
        ),
        db,
    )
    assert "VAT rate must be empty when VAT mode is manual." in errors


def test_vat_mode_manual_cash_out_requires_manual_deductible(db):
    errors = validate_transaction(
        valid_cash_out(
            vat_mode="manual",
            vat_rate=None,
            vat_deductible_pct=None,
            manual_vat_amount="10.00",
            manual_vat_deductible_amount=None,
        ),
        db,
    )
    assert (
        "Manual VAT deductible amount is required for cash_out in manual VAT mode."
        in errors
    )


def test_manual_vat_deductible_cannot_exceed_manual_vat_amount(db):
    errors = validate_transaction(
        valid_cash_out(
            vat_mode="manual",
            vat_rate=None,
            vat_deductible_pct=None,
            manual_vat_amount="10.00",
            manual_vat_deductible_amount="12.00",
        ),
        db,
    )
    assert "Manual VAT deductible amount cannot exceed manual VAT amount." in errors


def test_missing_customer_type_rejected(db):
    errors = validate_transaction(valid_cash_out(customer_type=None), db)
    assert "Customer type must be private, company, or other." in errors


def test_invalid_customer_type_rejected(db):
    errors = validate_transaction(valid_cash_out(customer_type="bogus"), db)
    assert "Customer type must be private, company, or other." in errors


@pytest.mark.parametrize("customer_type", ["private", "company", "other"])
def test_valid_customer_type_values_accepted(customer_type, db):
    assert validate_transaction(valid_cash_out(customer_type=customer_type), db) == []


def test_external_cash_in_without_document_flow_rejected(db):
    errors = validate_transaction(valid_cash_in(document_flow=None), db)
    assert "Document flow is required for external cash_in transactions." in errors


def test_internal_cash_in_with_document_flow_rejected(db):
    errors = validate_transaction(
        valid_cash_in(
            cash_in_type="internal",
            vat_rate="0",
            payment_method="cash",
            customer_type="private",
            document_flow="receipt",
            for_accountant="",
        ),
        db,
    )
    assert "Document flow must be empty for internal cash_in transactions." in errors


def test_cash_out_without_document_flow_accepted(db):
    assert validate_transaction(valid_cash_out(document_flow=None), db) == []


def test_invalid_document_flow_rejected(db):
    errors = validate_transaction(valid_cash_in(document_flow="bogus"), db)
    assert (
        "Document flow must be invoice, receipt, invoice_and_receipt, or other_document."
        in errors
    )


def test_invoice_and_receipt_company_rejected(db):
    errors = validate_transaction(
        valid_cash_in(customer_type="company", document_flow="invoice_and_receipt"),
        db,
    )
    assert "invoice_and_receipt is only allowed when customer type is private." in errors


def test_invoice_and_receipt_private_accepted(db):
    assert (
        validate_transaction(
            valid_cash_in(
                customer_type="private", document_flow="invoice_and_receipt"
            ),
            db,
        )
        == []
    )


def test_internal_cash_in_manual_mode_rejected(db):
    errors = validate_transaction(
        valid_cash_in(
            cash_in_type="internal",
            payment_method="cash",
            vat_mode="manual",
            vat_rate=None,
            manual_vat_amount="10.00",
            customer_type="private",
            document_flow=None,
            for_accountant="",
        ),
        db,
    )
    assert "Internal cash_in must use automatic VAT mode." in errors


def test_internal_cash_in_nonzero_vat_rejected(db):
    errors = validate_transaction(
        valid_cash_in(
            cash_in_type="internal",
            vat_rate="23",
            payment_method="cash",
            customer_type="private",
            document_flow=None,
            for_accountant="",
        ),
        db,
    )
    assert "Internal cash_in must use a VAT rate of 0." in errors


@pytest.mark.parametrize("payment_method", ["card", "transfer"])
def test_internal_cash_in_non_cash_payment_rejected(payment_method, db):
    errors = validate_transaction(
        valid_cash_in(
            cash_in_type="internal",
            vat_rate="0",
            payment_method=payment_method,
            customer_type="private",
            document_flow=None,
            for_accountant="",
        ),
        db,
    )
    assert "Internal cash_in must use cash as payment method." in errors


def test_internal_cash_in_for_accountant_true_rejected(db):
    errors = validate_transaction(
        valid_cash_in(
            cash_in_type="internal",
            vat_rate="0",
            payment_method="cash",
            customer_type="private",
            document_flow=None,
            for_accountant="1",
        ),
        db,
    )
    assert "Internal cash_in cannot be marked for accountant." in errors


def test_internal_cash_in_non_private_customer_rejected(db):
    errors = validate_transaction(
        valid_cash_in(
            cash_in_type="internal",
            vat_rate="0",
            payment_method="cash",
            customer_type="company",
            document_flow=None,
            for_accountant="",
        ),
        db,
    )
    assert "Internal cash_in must use customer type private." in errors


def test_internal_cash_in_valid_case_accepted(db):
    assert (
        validate_transaction(
            valid_cash_in(
                cash_in_type="internal",
                vat_rate="0",
                payment_method="cash",
                customer_type="private",
                document_flow=None,
                for_accountant="",
            ),
            db,
        )
        == []
    )


def test_cash_in_type_set_on_cash_out_rejected(db):
    errors = validate_transaction(valid_cash_out(cash_in_type="external"), db)
    assert "Cash-in type must be empty for cash_out transactions." in errors


def test_vat_deductible_pct_set_on_cash_in_rejected(db):
    errors = validate_transaction(valid_cash_in(vat_deductible_pct="100"), db)
    assert "VAT deductible percentage must be empty for cash_in transactions." in errors


def test_parent_group_category_rejected(db):
    errors = validate_transaction(valid_cash_in(category_id=CASH_IN_PARENT_ID), db)
    assert "Category must be a selectable leaf category." in errors


def test_category_direction_mismatch_rejected(db):
    errors = validate_transaction(valid_cash_in(category_id=CASH_OUT_LEAF_ID), db)
    assert "Category direction must match transaction direction." in errors


def test_valid_leaf_category_accepted(db):
    assert validate_transaction(valid_cash_out(category_id=CASH_OUT_LEAF_ID), db) == []


def test_other_income_requires_description(db):
    errors = validate_transaction(
        valid_cash_in(category_id=OTHER_INCOME_CATEGORY_ID, description=None),
        db,
    )
    assert "Description is required for ci_other_income and co_other_expense." in errors


def test_other_expense_requires_description(db):
    errors = validate_transaction(
        valid_cash_out(category_id=OTHER_EXPENSE_CATEGORY_ID, description=None),
        db,
    )
    assert "Description is required for ci_other_income and co_other_expense." in errors

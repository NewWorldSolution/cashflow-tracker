from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation

from app.services.transaction_service import get_category


ALLOWED_DIRECTIONS = {"cash_in", "cash_out"}
ALLOWED_PAYMENT_METHODS = {"cash", "card", "transfer"}
ALLOWED_VAT_RATES = {Decimal("0"), Decimal("5"), Decimal("8"), Decimal("23")}
ALLOWED_VAT_DEDUCTIBLE_PCTS = {Decimal("0"), Decimal("50"), Decimal("100")}
ALLOWED_CASH_IN_TYPES = {"internal", "external"}
ALLOWED_VAT_MODES = {"automatic", "manual"}
ALLOWED_CUSTOMER_TYPES = {"private", "company", "other"}
ALLOWED_DOCUMENT_FLOWS = {
    "invoice",
    "receipt",
    "invoice_and_receipt",
    "other_document",
}
DESCRIPTION_REQUIRED_CATEGORY_NAMES = {"ci_other_income", "co_other_expense"}


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _parse_decimal(value) -> Decimal | None:
    if value is None or value == "" or isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse_int(value) -> int | None:
    if value is None or value == "" or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _parse_bool(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "on", "yes"}


def validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]:
    errors: list[str] = []

    raw_date = data.get("date")
    raw_direction = data.get("direction")
    raw_amount = data.get("amount")
    raw_category_id = data.get("category_id")
    raw_company_id = data.get("company_id")
    raw_payment_method = data.get("payment_method")
    raw_vat_rate = data.get("vat_rate")
    raw_vat_mode = data.get("vat_mode", "automatic")
    raw_manual_vat_amount = data.get("manual_vat_amount")
    raw_manual_vat_deductible_amount = data.get("manual_vat_deductible_amount")
    raw_customer_type = data.get("customer_type")
    raw_document_flow = data.get("document_flow")
    cash_in_type = data.get("cash_in_type")
    raw_vat_deductible_pct = data.get("vat_deductible_pct")
    description = data.get("description")
    raw_logged_by = data.get("logged_by")
    raw_for_accountant = data.get("for_accountant")

    if not raw_date:
        errors.append("Date is required.")
    else:
        try:
            date.fromisoformat(str(raw_date))
        except (TypeError, ValueError):
            errors.append("Date must be a valid YYYY-MM-DD value.")

    direction = str(raw_direction) if raw_direction is not None else None
    if direction not in ALLOWED_DIRECTIONS:
        errors.append("Direction must be cash_in or cash_out.")

    amount = _parse_decimal(raw_amount)
    if amount is None:
        errors.append("Amount must be a positive number.")
    elif amount <= 0:
        errors.append("Amount must be greater than 0.")

    category_id = _parse_int(raw_category_id)
    category = None
    if category_id is None:
        errors.append("Category must be a valid category id.")
    else:
        category = get_category(category_id, db)
        if category is None:
            errors.append("Category must be a valid category id.")
        elif category["parent_id"] is None:
            errors.append("Category must be a selectable leaf category.")

    company_id = _parse_int(raw_company_id)
    if company_id is None:
        errors.append("Company is required.")
    else:
        company_row = db.execute(
            "SELECT id FROM companies WHERE id = ? AND is_active = TRUE",
            (company_id,),
        ).fetchone()
        if company_row is None:
            errors.append("Company must be a valid active company.")

    payment_method = str(raw_payment_method) if raw_payment_method is not None else None
    if payment_method not in ALLOWED_PAYMENT_METHODS:
        errors.append("Payment method must be cash, card, or transfer.")

    vat_mode = str(raw_vat_mode) if raw_vat_mode is not None else None
    if vat_mode not in ALLOWED_VAT_MODES:
        errors.append("VAT mode must be automatic or manual.")

    vat_rate = _parse_decimal(raw_vat_rate)
    if vat_mode == "automatic":
        if vat_rate is None:
            errors.append("VAT rate must be one of 0, 5, 8, or 23.")
        elif vat_rate not in ALLOWED_VAT_RATES:
            errors.append("VAT rate must be one of 0, 5, 8, or 23.")
    elif vat_mode == "manual":
        if not _is_blank(raw_vat_rate):
            errors.append("VAT rate must be empty when VAT mode is manual.")

    manual_vat_amount = _parse_decimal(raw_manual_vat_amount)
    manual_vat_deductible_amount = _parse_decimal(raw_manual_vat_deductible_amount)

    if vat_mode == "manual":
        if manual_vat_amount is None:
            errors.append("Manual VAT amount is required when VAT mode is manual.")
        elif manual_vat_amount < 0:
            errors.append("Manual VAT amount must be 0 or greater.")

        if direction == "cash_out":
            if manual_vat_deductible_amount is None:
                errors.append(
                    "Manual VAT deductible amount is required for cash_out in manual VAT mode."
                )
            elif manual_vat_deductible_amount < 0:
                errors.append("Manual VAT deductible amount must be 0 or greater.")
            elif (
                manual_vat_amount is not None
                and manual_vat_deductible_amount > manual_vat_amount
            ):
                errors.append(
                    "Manual VAT deductible amount cannot exceed manual VAT amount."
                )
        elif not _is_blank(raw_manual_vat_deductible_amount):
            errors.append(
                "Manual VAT deductible amount must be empty for cash_in transactions."
            )
    else:
        if not _is_blank(raw_manual_vat_amount):
            errors.append("Manual VAT amount must be empty when VAT mode is automatic.")
        if not _is_blank(raw_manual_vat_deductible_amount):
            errors.append(
                "Manual VAT deductible amount must be empty when VAT mode is automatic."
            )

    customer_type = str(raw_customer_type) if raw_customer_type is not None else None
    if customer_type not in ALLOWED_CUSTOMER_TYPES:
        errors.append("Customer type must be private, company, or other.")

    document_flow = (
        str(raw_document_flow) if raw_document_flow is not None else raw_document_flow
    )
    if not _is_blank(document_flow) and document_flow not in ALLOWED_DOCUMENT_FLOWS:
        errors.append(
            "Document flow must be invoice, receipt, invoice_and_receipt, or other_document."
        )

    vat_deductible_pct = _parse_decimal(raw_vat_deductible_pct)
    if direction == "cash_in":
        if cash_in_type is None:
            errors.append("Cash-in type is required for cash_in transactions.")
        elif cash_in_type not in ALLOWED_CASH_IN_TYPES:
            errors.append("Cash-in type must be internal or external.")

        if not _is_blank(raw_vat_deductible_pct):
            errors.append(
                "VAT deductible percentage must be empty for cash_in transactions."
            )

        if cash_in_type == "external" and _is_blank(document_flow):
            errors.append("Document flow is required for external cash_in transactions.")
    elif direction == "cash_out":
        if cash_in_type not in {None, ""}:
            errors.append("Cash-in type must be empty for cash_out transactions.")

        if vat_mode == "automatic":
            if raw_vat_deductible_pct is None:
                errors.append(
                    "VAT deductible percentage is required for cash_out transactions."
                )
            elif vat_deductible_pct is None or (
                vat_deductible_pct not in ALLOWED_VAT_DEDUCTIBLE_PCTS
            ):
                errors.append(
                    "VAT deductible percentage must be one of 0, 50, or 100."
                )
        elif not _is_blank(raw_vat_deductible_pct):
            errors.append(
                "VAT deductible percentage must be empty when VAT mode is manual."
            )

    if (
        direction == "cash_out"
        and vat_mode == "automatic"
        and raw_vat_deductible_pct is not None
        and vat_deductible_pct is None
    ):
        errors.append("VAT deductible percentage must be one of 0, 50, or 100.")

    if (
        direction == "cash_in"
        and not _is_blank(raw_manual_vat_deductible_amount)
    ):
        errors.append(
            "Manual VAT deductible amount must be empty for cash_in transactions."
        )

    if cash_in_type == "internal":
        if vat_mode != "automatic":
            errors.append("Internal cash_in must use automatic VAT mode.")
        if vat_rate is not None and vat_rate != Decimal("0"):
            errors.append("Internal cash_in must use a VAT rate of 0.")
        if payment_method != "cash":
            errors.append("Internal cash_in must use cash as payment method.")
        if _parse_bool(raw_for_accountant):
            errors.append("Internal cash_in cannot be marked for accountant.")
        if customer_type is not None and customer_type != "private":
            errors.append("Internal cash_in must use customer type private.")
        if not _is_blank(document_flow):
            errors.append("Document flow must be empty for internal cash_in transactions.")

    if (
        document_flow == "invoice_and_receipt"
        and customer_type is not None
        and customer_type != "private"
    ):
        errors.append(
            "invoice_and_receipt is only allowed when customer type is private."
        )

    if category is not None and direction in ALLOWED_DIRECTIONS:
        if category["direction"] != direction:
            errors.append("Category direction must match transaction direction.")
        if category["name"] in DESCRIPTION_REQUIRED_CATEGORY_NAMES:
            if description is None or str(description).strip() == "":
                errors.append(
                    "Description is required for ci_other_income and co_other_expense."
                )

    logged_by = _parse_int(raw_logged_by)
    if logged_by is None:
        errors.append("logged_by must be a valid user id.")
    else:
        user_row = db.execute(
            "SELECT id FROM users WHERE id = ?",
            (logged_by,),
        ).fetchone()
        if user_row is None:
            errors.append("logged_by must be a valid user id.")

    return errors

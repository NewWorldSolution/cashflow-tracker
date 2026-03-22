from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation


ALLOWED_DIRECTIONS = {"income", "expense"}
ALLOWED_PAYMENT_METHODS = {"cash", "card", "transfer"}
ALLOWED_VAT_RATES = {Decimal("0"), Decimal("5"), Decimal("8"), Decimal("23")}
ALLOWED_VAT_DEDUCTIBLE_PCTS = {Decimal("0"), Decimal("50"), Decimal("100")}
ALLOWED_INCOME_TYPES = {"internal", "external"}
BLOCKED_CATEGORY_NAMES = {"internal_transfer"}


def _parse_decimal(value) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse_int(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        text = str(value).strip()
        if text == "":
            return None
        return int(text)
    except (TypeError, ValueError):
        return None


def validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]:
    errors: list[str] = []

    raw_date = data.get("date")
    raw_direction = data.get("direction")
    raw_amount = data.get("amount")
    raw_category_id = data.get("category_id")
    raw_payment_method = data.get("payment_method")
    raw_vat_rate = data.get("vat_rate")
    income_type = data.get("income_type")
    raw_vat_deductible_pct = data.get("vat_deductible_pct")
    description = data.get("description")
    raw_logged_by = data.get("logged_by")

    if not raw_date:
        errors.append("Date is required.")
    else:
        try:
            date.fromisoformat(str(raw_date))
        except (TypeError, ValueError):
            errors.append("Date must be a valid YYYY-MM-DD value.")

    direction = str(raw_direction) if raw_direction is not None else None
    if direction not in ALLOWED_DIRECTIONS:
        errors.append("Direction must be income or expense.")

    amount = _parse_decimal(raw_amount)
    if amount is None:
        errors.append("Amount must be a positive number.")
    elif amount <= 0:
        errors.append("Amount must be greater than 0.")

    category_id = _parse_int(raw_category_id)
    category_row = None
    if category_id is None:
        errors.append("Category must be a valid category id.")
    else:
        category_row = db.execute(
            "SELECT category_id, direction, name FROM categories WHERE category_id = ?",
            (category_id,),
        ).fetchone()
        if category_row is None:
            errors.append("Category must be a valid category id.")

    payment_method = str(raw_payment_method) if raw_payment_method is not None else None
    if payment_method not in ALLOWED_PAYMENT_METHODS:
        errors.append("Payment method must be cash, card, or transfer.")

    vat_rate = _parse_decimal(raw_vat_rate)
    if vat_rate is None:
        errors.append("VAT rate must be one of 0, 5, 8, or 23.")
    elif vat_rate not in ALLOWED_VAT_RATES:
        errors.append("VAT rate must be one of 0, 5, 8, or 23.")

    vat_deductible_pct = _parse_decimal(raw_vat_deductible_pct)
    if direction == "income":
        if income_type is None:
            errors.append("Income type is required for income transactions.")
        elif income_type not in ALLOWED_INCOME_TYPES:
            errors.append("Income type must be internal or external.")
        if raw_vat_deductible_pct is not None:
            errors.append(
                "VAT deductible percentage must be empty for income transactions."
            )
    elif direction == "expense":
        if income_type is not None:
            errors.append("Income type must be empty for expense transactions.")
        if raw_vat_deductible_pct is None:
            errors.append(
                "VAT deductible percentage is required for expense transactions."
            )

    if raw_vat_deductible_pct is not None:
        if vat_deductible_pct is None:
            errors.append(
                "VAT deductible percentage must be one of 0, 50, or 100."
            )
        elif vat_deductible_pct not in ALLOWED_VAT_DEDUCTIBLE_PCTS:
            errors.append(
                "VAT deductible percentage must be one of 0, 50, or 100."
            )

    if income_type == "internal" and vat_rate is not None and vat_rate != Decimal("0"):
        errors.append("Internal income must use a VAT rate of 0.")

    if income_type == "internal" and payment_method != "cash":
        errors.append("Internal income must use cash as payment method.")

    if category_row is not None and direction in ALLOWED_DIRECTIONS:
        if category_row["direction"] != direction:
            errors.append("Category direction must match transaction direction.")
        if category_row["name"] in BLOCKED_CATEGORY_NAMES:
            errors.append("This category is not available for manual transactions.")
        if category_row["name"] in {"other_expense", "other_income"}:
            if description is None or str(description).strip() == "":
                errors.append(
                    "Description is required for other_expense and other_income."
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

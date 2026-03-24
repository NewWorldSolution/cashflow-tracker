from __future__ import annotations

import sqlite3
from decimal import Decimal
from typing import Any


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def get_category(category_id: int, db: sqlite3.Connection) -> dict[str, Any] | None:
    row = db.execute(
        "SELECT c.category_id, c.name, c.label, c.direction, c.default_vat_rate, "
        "c.default_vat_deductible_pct, c.parent_id, "
        "p.name AS parent_name, p.label AS parent_label "
        "FROM categories c "
        "LEFT JOIN categories p ON c.parent_id = p.category_id "
        "WHERE c.category_id = ?",
        (category_id,),
    ).fetchone()
    return _row_to_dict(row)


def is_leaf_category(category_id: int, db: sqlite3.Connection) -> bool:
    row = db.execute(
        "SELECT 1 FROM categories WHERE category_id = ? AND parent_id IS NOT NULL",
        (category_id,),
    ).fetchone()
    return row is not None


def get_category_path(category_id: int, db: sqlite3.Connection) -> str | None:
    category = get_category(category_id, db)
    if category is None:
        return None
    if category["parent_label"]:
        return f'{category["parent_label"]} > {category["label"]}'
    return category["label"]


def get_children_of_parent(
    parent_category_id: int, db: sqlite3.Connection
) -> list[dict[str, Any]]:
    rows = db.execute(
        "SELECT category_id, name, label, direction, default_vat_rate, "
        "default_vat_deductible_pct, parent_id "
        "FROM categories "
        "WHERE parent_id = ? "
        "ORDER BY label",
        (parent_category_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_categories_by_direction(
    direction: str, db: sqlite3.Connection
) -> list[dict[str, Any]]:
    parent_rows = db.execute(
        "SELECT category_id, name, label, direction "
        "FROM categories "
        "WHERE direction = ? AND parent_id IS NULL "
        "ORDER BY category_id",
        (direction,),
    ).fetchall()
    groups: list[dict[str, Any]] = []
    for parent_row in parent_rows:
        parent = dict(parent_row)
        parent["children"] = get_children_of_parent(parent["category_id"], db)
        groups.append(parent)
    return groups


def _coerce_decimal_or_none(value: Any) -> str | None:
    if value is None or value == "":
        return None
    return str(Decimal(str(value)))


def _coerce_bool(value: Any) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if value is None:
        return 0
    return 1 if str(value).strip().lower() in {"1", "true", "on", "yes"} else 0


def create_transaction(data: dict[str, Any], db: sqlite3.Connection) -> int:
    db.execute(
        "INSERT INTO transactions "
        "("
        "date, amount, direction, category_id, company_id, payment_method, vat_rate, "
        "cash_in_type, vat_deductible_pct, manual_vat_amount, vat_mode, "
        "manual_vat_deductible_amount, customer_type, document_flow, description, "
        "for_accountant, logged_by"
        ") "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            _coerce_decimal_or_none(data["amount"]),
            data["direction"],
            int(data["category_id"]),
            int(data["company_id"]),
            data["payment_method"],
            float(data["vat_rate"]) if data.get("vat_rate") is not None else None,
            data.get("cash_in_type"),
            (
                float(data["vat_deductible_pct"])
                if data.get("vat_deductible_pct") is not None
                else None
            ),
            _coerce_decimal_or_none(data.get("manual_vat_amount")),
            data.get("vat_mode", "automatic"),
            _coerce_decimal_or_none(data.get("manual_vat_deductible_amount")),
            data["customer_type"],
            data.get("document_flow"),
            data.get("description"),
            _coerce_bool(data.get("for_accountant")),
            data["logged_by"],
        ),
    )
    return int(db.execute("SELECT last_insert_rowid()").fetchone()[0])


def correct_transaction(
    transaction_id: int,
    data: dict[str, Any],
    correction_reason: str,
    voided_by: int,
    db: sqlite3.Connection,
) -> int:
    transaction = get_transaction(transaction_id, db)
    if transaction is None:
        raise ValueError("Transaction not found.")
    if not transaction["is_active"]:
        raise ValueError("Transaction is already voided.")

    reason = correction_reason.strip()
    if not reason:
        raise ValueError("Correction reason is required.")

    new_id = create_transaction(data, db)
    db.execute(
        "UPDATE transactions "
        "SET is_active = 0, void_reason = ?, voided_by = ?, "
        "voided_at = CURRENT_TIMESTAMP, replacement_transaction_id = ? "
        "WHERE id = ?",
        (reason, voided_by, new_id, transaction_id),
    )
    return new_id


def get_transaction(transaction_id: int, db: sqlite3.Connection) -> dict | None:
    row = db.execute(
        "SELECT t.*, c.label AS category_label, c.name AS category_name, c.parent_id AS parent_id, "
        "p.label AS parent_category_label, p.name AS parent_category_name, "
        "u.username AS logged_by_username, "
        "vb.username AS voided_by_username, "
        "co.name AS company_name "
        "FROM transactions t "
        "JOIN categories c ON t.category_id = c.category_id "
        "LEFT JOIN categories p ON c.parent_id = p.category_id "
        "JOIN users u ON t.logged_by = u.id "
        "LEFT JOIN users vb ON t.voided_by = vb.id "
        "LEFT JOIN companies co ON t.company_id = co.id "
        "WHERE t.id = ?",
        (transaction_id,),
    ).fetchone()
    transaction = _row_to_dict(row)
    if transaction is None:
        return None
    transaction["category_path"] = get_category_path(transaction["category_id"], db)
    return transaction


def void_transaction(
    transaction_id: int,
    void_reason: str,
    voided_by: int,
    db: sqlite3.Connection,
) -> None:
    transaction = get_transaction(transaction_id, db)
    if transaction is None:
        raise ValueError("Transaction not found.")

    if not transaction["is_active"]:
        raise ValueError("Transaction is already voided.")

    reason = void_reason.strip()
    if not reason:
        raise ValueError("Void reason is required.")

    db.execute(
        "UPDATE transactions "
        "SET is_active = 0, void_reason = ?, voided_by = ?, voided_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (reason, voided_by, transaction_id),
    )

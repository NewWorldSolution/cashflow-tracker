from __future__ import annotations

import sqlite3


def get_transaction(transaction_id: int, db: sqlite3.Connection) -> dict | None:
    row = db.execute(
        "SELECT t.*, c.label AS category_label, "
        "u.username AS logged_by_username, "
        "vb.username AS voided_by_username "
        "FROM transactions t "
        "JOIN categories c ON t.category_id = c.category_id "
        "JOIN users u ON t.logged_by = u.id "
        "LEFT JOIN users vb ON t.voided_by = vb.id "
        "WHERE t.id = ?",
        (transaction_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


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

"""
Idempotent database initialiser.
Run with: python db/init_db.py
Safe to run multiple times — no duplicate rows, no errors.
"""
import pathlib
import sqlite3

import bcrypt

DB_PATH = pathlib.Path("cashflow.db")
SCHEMA_PATH = pathlib.Path("db/schema.sql")
CATEGORIES_SQL = pathlib.Path("seed/categories.sql")
COMPANIES_SQL = pathlib.Path("seed/companies.sql")

USERS = [
    ("owner", "owner123"),
    ("assistant", "assistant123"),
    ("wife", "wife123"),
]


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    return any(
        row[1] == column_name for row in conn.execute(f"PRAGMA table_info({table_name})")
    )


def _has_incompatible_pre_i8_schema(conn: sqlite3.Connection) -> bool:
    if not _table_exists(conn, "categories") and not _table_exists(conn, "transactions"):
        return False

    category_incompatible = _table_exists(conn, "categories") and not _column_exists(
        conn, "categories", "parent_id"
    )
    transaction_incompatible = _table_exists(conn, "transactions") and any(
        not _column_exists(conn, "transactions", column_name)
        for column_name in (
            "cash_in_type",
            "vat_mode",
            "manual_vat_deductible_amount",
            "customer_type",
            "document_flow",
        )
    )
    return category_incompatible or transaction_incompatible


def _reset_all_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS settings_audit;
        DROP TABLE IF EXISTS settings;
        DROP TABLE IF EXISTS transactions;
        DROP TABLE IF EXISTS companies;
        DROP TABLE IF EXISTS categories;
        DROP TABLE IF EXISTS users;
        """
    )


def initialise_db(conn: sqlite3.Connection | None = None) -> None:
    """Create schema and seed data. Accepts an optional connection for testing."""
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    if _has_incompatible_pre_i8_schema(conn):
        _reset_all_tables(conn)

    # Apply schema
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)

    # Seed companies before backfilling company_id so the FK target exists.
    companies_sql = COMPANIES_SQL.read_text()
    conn.executescript(companies_sql)

    # Seed categories
    categories_sql = CATEGORIES_SQL.read_text()
    conn.executescript(categories_sql)

    # Seed users — hash passwords at runtime
    for username, plaintext_password in USERS:
        password_hash = bcrypt.hashpw(
            plaintext_password.encode(), bcrypt.gensalt()
        ).decode()
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )

    conn.commit()


if __name__ == "__main__":
    initialise_db()
    print("Database initialised.")

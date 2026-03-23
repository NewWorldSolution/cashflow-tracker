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


def initialise_db(conn: sqlite3.Connection | None = None) -> None:
    """Create schema and seed data. Accepts an optional connection for testing."""
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    # Apply schema
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)

    # Migration: add voided_at column for existing databases
    try:
        conn.execute("ALTER TABLE transactions ADD COLUMN voided_at TIMESTAMP")
    except Exception:
        pass  # Column already exists

    # Migration: add company_id column for existing databases.
    # Legacy SQLite schemas cannot add a new NOT NULL FK column safely, so migrate
    # as nullable/defaulted and backfill existing rows to the default company.
    try:
        conn.execute(
            "ALTER TABLE transactions ADD COLUMN company_id INTEGER REFERENCES companies(id) DEFAULT 1"
        )
    except Exception:
        pass  # Column already exists

    # Migration: add for_accountant column for existing databases.
    try:
        conn.execute(
            "ALTER TABLE transactions ADD COLUMN for_accountant BOOLEAN NOT NULL DEFAULT FALSE"
        )
    except Exception:
        pass  # Column already exists

    # Seed companies before backfilling company_id so the FK target exists.
    companies_sql = COMPANIES_SQL.read_text()
    conn.executescript(companies_sql)

    conn.execute("UPDATE transactions SET company_id = 1 WHERE company_id IS NULL")

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

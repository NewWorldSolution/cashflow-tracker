"""
Idempotent database initialiser.
Run with: python db/init_db.py
Safe to run multiple times — no duplicate rows, no errors.
"""
import pathlib
import sqlite3

import bcrypt

try:
    import psycopg2.errors as psycopg2_errors
except ModuleNotFoundError:
    psycopg2_errors = None

DB_PATH = pathlib.Path("cashflow.db")
SCHEMA_PATH = pathlib.Path("db/schema.sql")
CATEGORIES_SQL = pathlib.Path("seed/categories.sql")
COMPANIES_SQL = pathlib.Path("seed/companies.sql")

USERS = [
    ("owner", "owner123"),
    ("assistant", "assistant123"),
    ("wife", "wife123"),
]


_PG_POST_SCHEMA_SQL = """
ALTER TABLE transactions
ADD CONSTRAINT chk_expense_vat_deductible
CHECK (
    direction != 'cash_out'
    OR vat_deductible_pct IS NOT NULL
);
"""


def _is_postgres(conn) -> bool:
    """Detect psycopg2 connections, including app.main's wrapper."""
    if type(conn).__name__ == "_PgConnectionWrapper":
        return True
    return type(conn).__module__.startswith("psycopg2")


def _execute(conn, sql: str, params=None):
    if hasattr(conn, "execute"):
        if params is None:
            return conn.execute(sql)
        return conn.execute(sql, params)

    cursor = conn.cursor()
    adapted = sql.replace("?", "%s") if _is_postgres(conn) else sql
    if params is None:
        cursor.execute(adapted)
    else:
        cursor.execute(adapted, params)
    return cursor


def _executescript(conn, sql: str) -> None:
    if hasattr(conn, "executescript"):
        conn.executescript(sql)
        return

    for statement in [s.strip() for s in sql.split(";\n") if s.strip()]:
        _execute(conn, statement)


def _prepare_schema_for_pg(sql: str) -> str:
    """Adapt SQLite schema SQL for PostgreSQL at apply time."""
    return sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")


def _split_schema_statements(sql: str) -> list[str]:
    """Split schema SQL into individual statements for psycopg2."""
    return [statement.strip() for statement in sql.split(";\n") if statement.strip()]


def _apply_pg_post_schema(conn) -> None:
    """Apply PostgreSQL-only post-schema DDL (idempotent)."""
    duplicate_object_error = getattr(psycopg2_errors, "DuplicateObject", None)
    try:
        _execute(conn, _PG_POST_SCHEMA_SQL)
        conn.commit()
    except Exception as exc:
        if duplicate_object_error and isinstance(exc, duplicate_object_error):
            conn.rollback()
            return
        raise


def _apply_schema(conn) -> None:
    schema = SCHEMA_PATH.read_text()
    if _is_postgres(conn):
        pg_schema = _prepare_schema_for_pg(schema)
        for statement in _split_schema_statements(pg_schema):
            _execute(conn, statement)
        conn.commit()
        _apply_pg_post_schema(conn)
    else:
        conn.executescript(schema)


def _table_exists(conn, table_name: str) -> bool:
    if _is_postgres(conn):
        row = _execute(
            conn,
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = ?",
            (table_name,),
        ).fetchone()
    else:
        row = _execute(
            conn,
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
    return row is not None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    if _is_postgres(conn):
        row = _execute(
            conn,
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = ? AND column_name = ?",
            (table_name, column_name),
        ).fetchone()
        return row is not None

    return any(
        row[1] == column_name for row in _execute(conn, f"PRAGMA table_info({table_name})")
    )


def _has_incompatible_pre_i8_schema(conn) -> bool:
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


def _reset_all_tables(conn) -> None:
    _executescript(
        conn,
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

    _apply_schema(conn)

    # Seed companies before backfilling company_id so the FK target exists.
    companies_sql = COMPANIES_SQL.read_text()
    _executescript(conn, companies_sql)

    # Seed categories
    categories_sql = CATEGORIES_SQL.read_text()
    _executescript(conn, categories_sql)

    # Seed users — hash passwords at runtime
    for username, plaintext_password in USERS:
        password_hash = bcrypt.hashpw(
            plaintext_password.encode(), bcrypt.gensalt()
        ).decode()
        _execute(
            conn,
            "INSERT INTO users (username, password_hash) VALUES (?, ?) "
            "ON CONFLICT DO NOTHING",
            (username, password_hash),
        )

    conn.commit()


if __name__ == "__main__":
    initialise_db()
    print("Database initialised.")

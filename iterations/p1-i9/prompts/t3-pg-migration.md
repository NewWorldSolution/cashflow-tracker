# I9-T3 — Schema Migration (SQLite → PostgreSQL)

**Branch:** `feature/p1-i9/t3-pg-migration`
**Base:** `feature/phase-1/iteration-9` (after T1 merged)
**Depends on:** I9-T1

---

## Goal

Make `db/schema.sql`, `db/init_db.py`, and the SQL service layer work correctly with both SQLite (dev/test) and PostgreSQL (production). After this task, `pytest -v` passes against SQLite and `DATABASE_URL=postgresql://... pytest -v` passes against PostgreSQL. The conditional `vat_deductible_pct` CHECK constraint is active on PostgreSQL.

This task touches three distinct problems:
1. **Schema syntax differences** between SQLite and PostgreSQL
2. **`init_db.py` dual-engine support** — introspection APIs differ completely
3. **SQL placeholder compatibility** — `?` (SQLite) vs `%s` (psycopg2)

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i9/prompt.md
db/schema.sql
db/init_db.py
seed/categories.sql
seed/companies.sql
app/main.py          ← understand _connect(), _is_postgres(), get_db() from T1
app/services/validation.py
app/services/transaction_service.py
app/services/auth_service.py
tests/conftest.py    ← if it exists
tests/test_init_db.py
```

---

## Deliverables

### 1. Single `db/schema.sql` with runtime adaptation

The iteration brief states the schema is identical between SQLite and PostgreSQL. Do NOT create a second schema file (`db/schema_pg.sql`). Keep one `db/schema.sql` and handle the two engine-specific differences in `init_db.py` at apply time.

**Difference 1 — AUTOINCREMENT → SERIAL:**

SQLite requires `INTEGER PRIMARY KEY AUTOINCREMENT`. PostgreSQL requires `SERIAL PRIMARY KEY`. The schema uses `AUTOINCREMENT` (existing SQLite syntax). At apply time, substitute for PostgreSQL:

```python
def _prepare_schema_for_pg(sql: str) -> str:
    """Adapt SQLite schema SQL for PostgreSQL at apply time."""
    return sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
```

This is a safe substitution — `AUTOINCREMENT` is a specific, bounded keyword that appears only in column definitions in our schema. `DEFAULT CURRENT_TIMESTAMP` and `BOOLEAN` work identically on both engines.

**Difference 2 — conditional CHECK constraint (go-live requirement per CLAUDE.md):**

SQLite does not support `ALTER TABLE ... ADD CONSTRAINT CHECK` after table creation. PostgreSQL does. Apply the constraint as a separate statement after schema creation, for PostgreSQL only:

```python
_PG_POST_SCHEMA_SQL = """
ALTER TABLE transactions
ADD CONSTRAINT chk_expense_vat_deductible
CHECK (
    direction != 'cash_out'
    OR vat_deductible_pct IS NOT NULL
);
"""
```

Run this in `_apply_schema()` after the CREATE TABLE statements, wrapped in a try/except on `DuplicateObject` so it is idempotent:

```python
import psycopg2.errors

def _apply_pg_post_schema(conn) -> None:
    """Apply PostgreSQL-only post-schema DDL (idempotent)."""
    try:
        conn.execute(_PG_POST_SCHEMA_SQL)
        conn.commit()
    except psycopg2.errors.DuplicateObject:
        conn.rollback()  # constraint already exists — safe to ignore
```

**Schema execution on PostgreSQL:**

psycopg2 has no `executescript()`. Execute the schema as individual CREATE TABLE statements. Since our `schema.sql` contains only DDL `CREATE TABLE IF NOT EXISTS` blocks separated by blank lines with semicolons, split on `;\n` (semicolon + newline) — not a bare `;` — which is safe for this controlled file:

```python
def _split_schema_statements(sql: str) -> list[str]:
    """Split schema SQL into individual statements for psycopg2.

    Splits on semicolon-newline, not bare semicolon, to avoid splitting
    inside string literals or inline comments. Safe for our DDL-only schema.
    """
    return [s.strip() for s in sql.split(";\n") if s.strip()]
```

### 2. Dual-engine `db/init_db.py`

The current `init_db.py` is deeply SQLite-specific:
- Uses `sqlite_master` for table existence checks
- Uses `PRAGMA table_info()` for column existence
- Uses `sqlite3.connect()` directly
- Uses `INSERT OR IGNORE` syntax
- Imports only `sqlite3`

Refactor `init_db.py` for dual-engine support:

**Engine detection:**
```python
def _is_postgres(conn) -> bool:
    """Detect psycopg2 connection, including the _PgConnectionWrapper from main.py."""
    # _PgConnectionWrapper (added by T3 in app/main.py) wraps a raw psycopg2 conn.
    # Check for it by name to avoid importing app code into db/init_db.py.
    if type(conn).__name__ == "_PgConnectionWrapper":
        return True
    return type(conn).__module__.startswith("psycopg2")
```

**Table existence (engine-aware):**
```python
def _table_exists(conn, table_name: str) -> bool:
    if _is_postgres(conn):
        row = conn.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = %s",
            (table_name,),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
    return row is not None
```

**Column existence (engine-aware):**
```python
def _column_exists(conn, table_name: str, column_name: str) -> bool:
    if _is_postgres(conn):
        row = conn.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = %s AND column_name = %s",
            (table_name, column_name),
        ).fetchone()
        return row is not None
    else:
        return any(
            row[1] == column_name
            for row in conn.execute(f"PRAGMA table_info({table_name})")
        )
```

**Schema loading (engine-aware):**
```python
SCHEMA_PATH = pathlib.Path("db/schema.sql")

def _apply_schema(conn) -> None:
    schema = SCHEMA_PATH.read_text()
    if _is_postgres(conn):
        pg_schema = _prepare_schema_for_pg(schema)
        for statement in _split_schema_statements(pg_schema):
            conn.execute(statement)
        conn.commit()
        _apply_pg_post_schema(conn)  # conditional CHECK constraint
    else:
        conn.executescript(schema)
```

**Seed data — rewrite seed files to use standard SQL:**

`INSERT OR IGNORE` is SQLite-only. The fix is to rewrite the seed files to use `INSERT INTO ... ON CONFLICT DO NOTHING`, which is standard SQL supported by both SQLite 3.24+ (released 2018) and PostgreSQL. No runtime string rewriting needed.

Update `seed/categories.sql` and `seed/companies.sql`:
- Remove `INSERT OR IGNORE INTO`
- Replace with `INSERT INTO`
- Append `ON CONFLICT DO NOTHING` before the statement's `;`

Example for `seed/companies.sql`:
```sql
-- Before:
INSERT OR IGNORE INTO companies (id, name, slug)
VALUES (...);

-- After:
INSERT INTO companies (id, name, slug)
VALUES (...)
ON CONFLICT DO NOTHING;
```

For the inline user INSERT in `init_db.py`, use the same pattern:
```python
conn.execute(
    "INSERT INTO users (username, password_hash) VALUES (?, ?) ON CONFLICT DO NOTHING",
    (username, password_hash),
)
```

This works on SQLite (via `_PgConnectionWrapper` which translates `?` → `%s`) and PostgreSQL alike. The `?` is translated by the wrapper — do not write `%s` here.

**Pre-I8 compatibility check (engine-aware):**

The `_has_incompatible_pre_i8_schema()` function uses `_table_exists` and `_column_exists` — once those are engine-aware, the incompatibility check works for both engines automatically. Verify this is the case.

**`_reset_all_tables()`:** `DROP TABLE IF EXISTS` works on both engines — no change needed.

### 3. SQL placeholder compatibility adapter in `app/main.py`

The service layer uses `?` placeholders throughout. psycopg2 requires `%s`. T1 intentionally left `_connect()` returning a raw psycopg2 connection — this task adds the wrapper that makes it service-layer compatible.

Add the `_PgConnectionWrapper` class in `app/main.py` and update `_connect()` to return it for PostgreSQL URLs:

```python
class _PgConnectionWrapper:
    """Wraps a psycopg2 connection to translate ? placeholders to %s.

    This lets service-layer code use ? (SQLite style) against both engines
    without modification.
    """
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql: str, params=None):
        adapted = sql.replace("?", "%s")
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(adapted, params)
        return cur

    def executescript(self, sql: str):
        # psycopg2 has no executescript — split and run each statement
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            self._conn.cursor().execute(stmt)
        self._conn.commit()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)
```

In `_connect()` for PostgreSQL, return `_PgConnectionWrapper(raw_conn)` instead of the raw connection. This way `get_db()`, `AuthGate`, and all service files receive an object that responds to `conn.execute(sql, params)` with `?` placeholders — transparently.

Update `_is_postgres()` to recognise the wrapper:

```python
def _is_postgres(conn) -> bool:
    if isinstance(conn, _PgConnectionWrapper):
        return True
    return type(conn).__module__.startswith("psycopg2")
```

### 4. Update `tests/conftest.py` (or `test_init_db.py`) for dual-engine

Add a `pg_db` fixture that skips gracefully if `DATABASE_URL` is not a PostgreSQL URL:

```python
import os
import pytest

PG_URL = os.getenv("DATABASE_URL", "")

@pytest.fixture
def pg_db():
    if not PG_URL.startswith(("postgresql://", "postgres://")):
        pytest.skip("PostgreSQL DATABASE_URL not set")
    import psycopg2
    conn = psycopg2.connect(PG_URL)
    from db.init_db import initialise_db
    initialise_db(conn)
    yield conn
    conn.close()
```

Add PostgreSQL-specific tests to `tests/test_init_db.py`:

- [ ] `test_pg_tables_created(pg_db)` — all 6 tables exist
- [ ] `test_pg_seed_categories(pg_db)` — 19 parent groups + 62 subcategories seeded
- [ ] `test_pg_seed_companies(pg_db)` — 4 companies seeded
- [ ] `test_pg_seed_users(pg_db)` — 3 users seeded
- [ ] `test_pg_vat_deductible_constraint(pg_db)` — INSERT of cash_out with `vat_deductible_pct = NULL` is rejected by the CHECK constraint

### 5. Run full test suite against SQLite

After all changes:

```bash
pytest -v
# Expected: all existing tests pass (SQLite path unchanged)
```

---

## Important Rules

- **One schema file** — do NOT create `db/schema_pg.sql`. Runtime adaptation via `_prepare_schema_for_pg()` keeps the single source of truth.
- **Do NOT change service layer SQL logic** — only add `_PgConnectionWrapper` in `main.py`
- **Rewrite seed files** to use `ON CONFLICT DO NOTHING` — this removes `INSERT OR IGNORE` from the source, which is cleaner than runtime adaptation
- **`_memory_keeper` (`:memory:`) pattern must still work** — SQLite tests depend on it
- **Do not break existing tests** — all 84+ tests must still pass against SQLite after this task

---

## Allowed Files

```text
db/schema.sql           ← no structural changes; AUTOINCREMENT stays for SQLite
db/init_db.py
seed/categories.sql     ← rewrite INSERT OR IGNORE → ON CONFLICT DO NOTHING
seed/companies.sql      ← rewrite INSERT OR IGNORE → ON CONFLICT DO NOTHING
app/main.py             ← add _PgConnectionWrapper, update _connect() and _is_postgres()
tests/conftest.py       ← create or modify
tests/test_init_db.py   ← add pg_ fixtures and tests
iterations/p1-i9/tasks.md
```

---

## Acceptance Criteria

- [ ] No `db/schema_pg.sql` — single schema file maintained
- [ ] `_prepare_schema_for_pg()` substitutes `AUTOINCREMENT` → `SERIAL` for PostgreSQL
- [ ] `chk_expense_vat_deductible` CHECK constraint applied after schema via `_apply_pg_post_schema()` (idempotent)
- [ ] `init_db.py` `_table_exists()` and `_column_exists()` use engine-appropriate introspection
- [ ] `_apply_schema()` uses `_split_schema_statements()` (splits on `;\n`) for PostgreSQL
- [ ] Seed files use `ON CONFLICT DO NOTHING` — no `INSERT OR IGNORE` remains
- [ ] `_PgConnectionWrapper` in `main.py` translates `?` → `%s` and returns `RealDictCursor` rows
- [ ] `_connect()` returns `_PgConnectionWrapper` for PostgreSQL URLs
- [ ] `_is_postgres()` in both `main.py` and `init_db.py` recognises the wrapper
- [ ] `get_db()` yields wrapper for PostgreSQL (service layer queries work end-to-end)
- [ ] `pytest -v` passes (SQLite path) — all existing tests green
- [ ] `DATABASE_URL=postgresql://... pytest -v` passes (PostgreSQL path) — all tests green
- [ ] PostgreSQL `vat_deductible_pct` CHECK constraint active and tested
- [ ] `ruff check .` passes

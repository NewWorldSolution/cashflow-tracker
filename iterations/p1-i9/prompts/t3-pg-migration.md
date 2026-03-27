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

### 1. PostgreSQL-compatible `db/schema.sql`

The current schema has SQLite-specific syntax that must be made dual-compatible.

**AUTOINCREMENT → SERIAL (PostgreSQL) / AUTOINCREMENT (SQLite):**
SQLite and PostgreSQL cannot share the same auto-increment syntax. The cleanest solution: keep `schema.sql` using standard SQL `INTEGER PRIMARY KEY` without `AUTOINCREMENT` — SQLite auto-increments any `INTEGER PRIMARY KEY` implicitly, and PostgreSQL handles this with `SERIAL` or `GENERATED ALWAYS AS IDENTITY`.

Use `SERIAL PRIMARY KEY` for PostgreSQL, `INTEGER PRIMARY KEY` for SQLite. Since `init_db.py` will handle engine-specific schema creation (see deliverable 2), create two schema files:

- `db/schema.sql` — SQLite version (current, minimal changes)
- `db/schema_pg.sql` — PostgreSQL version

**Changes in `db/schema_pg.sql`:**

```sql
-- Replace: id INTEGER PRIMARY KEY AUTOINCREMENT
-- With:    id SERIAL PRIMARY KEY

-- Replace: category_id INTEGER PRIMARY KEY
-- With:    category_id SERIAL PRIMARY KEY
```

**Timestamps:**
- SQLite: `DEFAULT CURRENT_TIMESTAMP` — works on both, keep as-is

**Boolean:**
- Both SQLite (0/1) and PostgreSQL (true/false) accept `BOOLEAN` column type — no change needed

**Add PostgreSQL conditional CHECK (go-live requirement per CLAUDE.md):**

Add to `db/schema_pg.sql` after the transactions table definition:

```sql
-- PostgreSQL only — enforces vat_deductible_pct NOT NULL on cash_out
-- Added at go-live per CLAUDE.md
ALTER TABLE transactions
ADD CONSTRAINT chk_expense_vat_deductible
CHECK (
    direction != 'cash_out'
    OR vat_deductible_pct IS NOT NULL
);
```

This constraint must NOT be in `db/schema.sql` (SQLite version) — SQLite does not support `ALTER TABLE ADD CONSTRAINT` with `CHECK` clauses after table creation.

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
    """Detect psycopg2 connection by module name."""
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
SCHEMA_PG_PATH = pathlib.Path("db/schema_pg.sql")

def _apply_schema(conn) -> None:
    if _is_postgres(conn):
        schema = SCHEMA_PG_PATH.read_text()
        # psycopg2 does not support executescript — execute statements one by one
        for statement in _split_sql(schema):
            conn.execute(statement)
        conn.commit()
    else:
        conn.executescript(SCHEMA_PATH.read_text())
```

**SQL statement splitter for PostgreSQL:**
```python
def _split_sql(sql: str) -> list[str]:
    """Split a SQL script into individual statements for psycopg2."""
    return [s.strip() for s in sql.split(";") if s.strip()]
```

**Seed data (INSERT OR IGNORE → ON CONFLICT DO NOTHING):**

`INSERT OR IGNORE` is SQLite-only. For PostgreSQL, the seed files need `ON CONFLICT DO NOTHING`. Since the seed files are plain SQL, create PostgreSQL-compatible versions or adapt them at runtime.

Preferred approach: adapt at init time, not separate files. In `initialise_db()`, detect engine and rewrite the INSERT statements:

```python
def _adapt_seed(sql: str, is_pg: bool) -> str:
    """Convert SQLite INSERT OR IGNORE to PostgreSQL ON CONFLICT DO NOTHING."""
    if is_pg:
        return sql.replace("INSERT OR IGNORE INTO", "INSERT INTO").replace(
            ");", ") ON CONFLICT DO NOTHING;"
        )
    return sql
```

Apply `_adapt_seed()` to the contents of `seed/categories.sql`, `seed/companies.sql`, and the inline user INSERT in `initialise_db()`.

For users, adapt the inline INSERT:
```python
# SQLite:
conn.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", ...)
# PostgreSQL:
conn.execute(
    "INSERT INTO users (username, password_hash) VALUES (%s, %s) ON CONFLICT DO NOTHING",
    ...
)
```

**Pre-I8 compatibility check (engine-aware):**

The `_has_incompatible_pre_i8_schema()` function uses `_table_exists` and `_column_exists` — once those are engine-aware, the incompatibility check works for both engines automatically. Verify this is the case.

**`_reset_all_tables()`:** `DROP TABLE IF EXISTS` works on both engines — no change needed.

### 3. SQL placeholder compatibility adapter in `app/main.py`

The service layer uses `?` placeholders throughout. psycopg2 requires `%s`. Rather than touching every service file, add a thin connection wrapper in `app/main.py`.

Add a `PgConnection` wrapper class that proxies `execute()` with automatic placeholder rewriting:

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

- **Do NOT change service layer SQL logic** — only add the `_PgConnectionWrapper` in `main.py`
- **Keep `db/schema.sql` working** — the SQLite version is unchanged for dev/test
- **`db/schema_pg.sql` is the production schema** — it adds `SERIAL` and the conditional CHECK
- **`INSERT OR IGNORE` stays in seed files** — adapt at runtime in `init_db.py`, do not modify the seed files themselves
- **`_memory_keeper` (`:memory:`) pattern must still work** — SQLite tests depend on it
- **Do not break existing tests** — all 84+ tests must still pass against SQLite after this task

---

## Allowed Files

```text
db/schema.sql
db/schema_pg.sql       ← create
db/init_db.py
app/main.py
tests/conftest.py      ← create or modify
tests/test_init_db.py  ← add pg_ fixtures and tests
iterations/p1-i9/tasks.md
```

---

## Acceptance Criteria

- [ ] `db/schema_pg.sql` created with SERIAL primary keys and conditional CHECK constraint
- [ ] `init_db.py` detects engine and uses engine-appropriate schema file
- [ ] `_table_exists()` and `_column_exists()` work on both SQLite and PostgreSQL
- [ ] Seed data inserts use `ON CONFLICT DO NOTHING` on PostgreSQL (adapted at runtime)
- [ ] `_PgConnectionWrapper` in `main.py` translates `?` → `%s` transparently
- [ ] `get_db()` returns wrapper for PostgreSQL connections (dict-like row access preserved)
- [ ] `pytest -v` passes (SQLite path) — all existing tests green
- [ ] `DATABASE_URL=postgresql://... pytest -v` passes (PostgreSQL path) — all tests green
- [ ] PostgreSQL `vat_deductible_pct` CHECK constraint active and tested
- [ ] `ruff check .` passes

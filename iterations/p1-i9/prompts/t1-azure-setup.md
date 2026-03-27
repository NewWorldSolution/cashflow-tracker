# I9-T1 — Azure Hosting + Database Setup

**Branch:** `feature/p1-i9/t1-azure-setup`
**Base:** `feature/phase-1/iteration-9`
**Depends on:** — (first task)

---

## Goal

Choose the Azure hosting model, provision Azure PostgreSQL, and implement dual-engine database support in the application so it can connect to SQLite (dev/test) and PostgreSQL (production) from the same codebase. After this task, the app starts and serves pages against both database engines, driven purely by the `DATABASE_URL` environment variable.

This task is **infrastructure and connection plumbing only**. Schema migration, seed data, and init_db changes are T3's scope. Application logic does not change.

---

## Read Before Starting

```text
CLAUDE.md
project.md
docs/architecture.md
iterations/p1-i9/prompt.md
app/main.py
db/init_db.py
db/schema.sql
requirements.txt
```

---

## Deliverables

### 1. Hosting model decision

Use **Azure App Service (Linux)** with a Python 3.11+ runtime. Document the decision in a short comment block at the top of `docs/deployment.md` (create the file if it doesn't exist — T5 will fill it in). One paragraph is enough for now:

- Hosting model chosen: Azure App Service (Linux)
- Runtime: Python 3.11+
- Rationale: simplest deployment for a 3-user internal tool; built-in SSL; no Docker required

### 2. Add PostgreSQL driver to requirements.txt

Add `psycopg2-binary>=2.9.0` to `requirements.txt`. Use `psycopg2-binary` (not `psycopg2`) for Azure App Service compatibility — no C compiler needed.

### 3. Implement dual-engine database abstraction in `app/main.py`

The current `main.py` is fully SQLite-specific. Replace the connection layer with an engine-aware abstraction.

**Current state:**
- `DATABASE_URL = os.getenv("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")` — SQLite path only
- `get_db()` returns `sqlite3.Connection`
- `_connect()` handles SQLite file + `:memory:` cases
- `AuthGate` calls `_connect()` directly

**Target state — engine detection:**

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cashflow.db")

def _is_postgres(url: str) -> bool:
    return url.startswith("postgresql://") or url.startswith("postgres://")
```

**Target state — connection factory:**

```python
import sqlite3
import psycopg2
import psycopg2.extras

_memory_keeper: sqlite3.Connection | None = None  # keep-alive for :memory:


def _connect(url: str):
    """Return a live database connection for the given URL.

    Returns sqlite3.Connection for SQLite URLs, psycopg2 connection for PostgreSQL.
    """
    if _is_postgres(url):
        conn = psycopg2.connect(url)
        conn.autocommit = False
        return conn

    # SQLite path — strip prefix
    sqlite_path = url.removeprefix("sqlite:///./").removeprefix("sqlite:///")
    global _memory_keeper
    if sqlite_path in (":memory:", ""):
        if _memory_keeper is None:
            _memory_keeper = sqlite3.connect(
                "file::memory:?cache=shared", uri=True, check_same_thread=False
            )
        return sqlite3.connect(
            "file::memory:?cache=shared", uri=True, check_same_thread=False
        )
    return sqlite3.connect(sqlite_path, check_same_thread=False)


def get_db():
    """FastAPI dependency — returns a live database connection.

    For SQLite: sets row_factory = sqlite3.Row.
    For PostgreSQL: uses RealDictCursor so rows behave like dicts.
    """
    if _is_postgres(DATABASE_URL):
        conn = _connect(DATABASE_URL)
        try:
            yield conn
        finally:
            conn.close()
    else:
        conn = _connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
```

**AuthGate** — update to use the same `_connect()` factory. For PostgreSQL connections, set a `RealDictCursor` as the cursor factory so rows behave dict-like:

```python
# inside AuthGate.dispatch
conn = _connect(DATABASE_URL)
if _is_postgres(DATABASE_URL):
    # rows accessed as dicts — psycopg2 default cursor returns tuples
    # use RealDictCursor so service layer code (conn.execute(...).fetchone()) works
    conn = psycopg2.connect(DATABASE_URL,
                            cursor_factory=psycopg2.extras.RealDictCursor)
else:
    conn.row_factory = sqlite3.Row
```

Simplify this into the `_connect()` factory — pass `cursor_factory` for PostgreSQL connections rather than duplicating the logic in `AuthGate`.

### 4. SQL placeholder compatibility

The current service layer uses SQLite's `?` placeholders. PostgreSQL uses `%s`. This is a **known issue** — do NOT fix it in this task. Add a comment in `main.py`:

```python
# NOTE: SQL placeholder style — SQLite uses ?, PostgreSQL uses %s.
# Service layer uses ? throughout. T3 (pg-migration) handles placeholder
# compatibility via a thin adapter or by patching the query layer.
```

This documents the problem for T3 without mixing concerns into this task.

### 5. Lifespan + eager init update

The lifespan function and `create_app()` eager init both call `_connect(DATABASE_URL)` then pass the connection to `initialise_db()`. This is fine — `initialise_db()` will be updated in T3 to handle both engines. No changes needed here except ensuring `_connect()` returns the right connection type.

### 6. Verify app starts

Run:
```bash
python -m uvicorn app.main:app --reload
```

App must start without errors against SQLite. PostgreSQL connectivity will be verified end-to-end in T3.

---

## Important Rules

- **No schema changes** — schema.sql is T3's scope
- **No init_db.py changes** — T3 handles dual-engine init
- **No SQL rewriting** — placeholder compatibility is T3's scope
- **No application logic changes** — validation, calculations, routes are frozen
- **psycopg2-binary only** — not `psycopg2`, to avoid C compiler dependency on Azure
- The `_memory_keeper` pattern for `:memory:` testing must be preserved for SQLite

---

## Allowed Files

```text
app/main.py
requirements.txt
docs/deployment.md      ← create (stub only — T5 fills it in)
iterations/p1-i9/tasks.md
```

---

## Acceptance Criteria

- [ ] `psycopg2-binary>=2.9.0` in `requirements.txt`
- [ ] `DATABASE_URL` read from environment, defaulting to `sqlite:///./cashflow.db`
- [ ] `_is_postgres()` helper correctly identifies PostgreSQL URLs
- [ ] `_connect()` returns `sqlite3.Connection` for SQLite URLs and `psycopg2` connection for PostgreSQL URLs
- [ ] `get_db()` dependency works for both engines (dict-like row access in both cases)
- [ ] `AuthGate` uses the updated `_connect()` factory
- [ ] `:memory:` SQLite path still works (test compatibility preserved)
- [ ] App starts without errors: `python -m uvicorn app.main:app --reload`
- [ ] `docs/deployment.md` stub created with hosting model decision
- [ ] Placeholder compatibility note comment added in `main.py`
- [ ] `ruff check .` passes
- [ ] Existing tests still pass: `pytest -v` (SQLite path unchanged)

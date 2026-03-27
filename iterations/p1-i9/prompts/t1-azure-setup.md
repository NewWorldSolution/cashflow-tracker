# I9-T1 — Azure Hosting + Database Setup

**Branch:** `feature/p1-i9/t1-azure-setup`
**Base:** `feature/phase-1/iteration-9`
**Depends on:** — (first task)

---

## Goal

Choose the Azure hosting model and lay the connection-layer infrastructure: engine detection, a dual-path `_connect()` factory, and the PostgreSQL driver. After this task the SQLite path is unchanged and all existing tests pass. The PostgreSQL path returns a raw psycopg2 connection — placeholder compatibility (`?` vs `%s`) and `init_db.py` dual-engine support are T3's scope, so **full end-to-end PostgreSQL execution is NOT expected in T1**.

This task is **URL detection + connection factory only**. No SQL runs against PostgreSQL in T1 except the `SELECT 1` in the health check (T4). Application logic does not change.

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

_memory_keeper: sqlite3.Connection | None = None  # keep-alive for :memory:


def _connect(url: str):
    """Return a live database connection for the given URL.

    Returns sqlite3.Connection for SQLite URLs.
    Returns a raw psycopg2 connection for PostgreSQL URLs.

    NOTE: The raw psycopg2 connection is NOT yet compatible with the service
    layer — it uses ? placeholders and sqlite3.Row-style access. T3 wraps
    this in _PgConnectionWrapper to solve both problems. T1 intentionally
    returns the raw connection so T3 has a clean foundation to wrap.
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

    SQLite: sets row_factory = sqlite3.Row (unchanged behaviour).
    PostgreSQL: returns the raw psycopg2 connection. Placeholder and row
    access compatibility is added by T3's _PgConnectionWrapper.
    """
    conn = _connect(DATABASE_URL)
    if not _is_postgres(DATABASE_URL):
        conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```

**AuthGate** — update to use `_connect()` instead of the old hardcoded `sqlite3.connect()`. Set `row_factory` for the SQLite path only:

```python
# inside AuthGate.dispatch
conn = _connect(DATABASE_URL)
if not _is_postgres(DATABASE_URL):
    conn.row_factory = sqlite3.Row
```

T3 will later replace these returned connections with `_PgConnectionWrapper` — `AuthGate` will not need further changes at that point.

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

App must start without errors against SQLite. PostgreSQL connectivity is verified end-to-end in T3 — do not attempt to run the app against PostgreSQL in this task.

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
- [ ] `_is_postgres(url: str)` helper correctly identifies both `postgresql://` and `postgres://`
- [ ] `_connect()` returns `sqlite3.Connection` for SQLite URLs and a raw `psycopg2` connection for PostgreSQL URLs
- [ ] `get_db()` sets `row_factory = sqlite3.Row` for SQLite; yields raw psycopg2 connection for PostgreSQL (T3 adds wrapper)
- [ ] `AuthGate` uses `_connect()` and sets `row_factory` for SQLite path only
- [ ] `:memory:` SQLite path still works (test compatibility preserved)
- [ ] `docs/deployment.md` stub created with hosting model decision
- [ ] Placeholder compatibility note comment in `main.py` — no `?` → `%s` rewriting (T3 scope)
- [ ] App starts without errors against SQLite: `python -m uvicorn app.main:app --reload`
- [ ] No attempt made to run app or service queries against PostgreSQL in this task
- [ ] `ruff check .` passes
- [ ] `pytest -v` passes (SQLite path unchanged)

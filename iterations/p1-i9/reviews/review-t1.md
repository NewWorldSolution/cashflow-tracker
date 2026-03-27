# Review — I9-T1: Azure Hosting + Database Setup
**Branch:** `feature/p1-i9/t1-azure-setup`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompts/t1-azure-setup.md`, `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `psycopg2-binary>=2.9.0` added to `requirements.txt` (binary variant — no C compiler dependency)
- `DATABASE_URL` env var read in `app/main.py` defaulting to `sqlite:///./cashflow.db`
- `_is_postgres(url: str) -> bool` helper added, checking both `postgresql://` and `postgres://`
- `_connect()` refactored: returns `sqlite3.Connection` for SQLite, raw `psycopg2` connection for PostgreSQL (with `autocommit = False`)
- `get_db()` sets `row_factory = sqlite3.Row` for SQLite; yields raw psycopg2 connection for PostgreSQL (T3 adds the `_PgConnectionWrapper` — full service-layer PostgreSQL execution is NOT in T1)
- `AuthGate` updated to use `_connect()`; sets `row_factory` for SQLite path only
- `:memory:` SQLite special case (`_memory_keeper` keep-alive) preserved for test compatibility
- Comment in `main.py` documenting the `?` vs `%s` placeholder problem — NOT fixed here (T3 scope)
- `docs/deployment.md` stub created noting: Azure App Service (Linux), Python 3.11+, brief rationale
- No `init_db.py` changes, no `schema.sql` changes, no `ENVIRONMENT`/secrets/config work, no health/logging/static/CI work
- **PostgreSQL end-to-end execution is deferred to T3** — T1 only establishes the connection factory skeleton

---

## Review Steps

1. **Diff scope** — confirm only these files appear:
   - `app/main.py`
   - `requirements.txt`
   - `docs/deployment.md` (stub only)
   - iteration planning files under `iterations/p1-i9/`
   Any other modified files need justification.

2. **`requirements.txt`**
   - `psycopg2-binary` present (not `psycopg2` — the non-binary build requires a C compiler unavailable on Azure App Service)
   - Version constraint `>=2.9.0`

3. **`app/main.py` — DATABASE_URL**
   - `DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cashflow.db")`
   - Must NOT use the old `.removeprefix("sqlite:///./")` pattern as the default value

4. **`app/main.py` — `_is_postgres()`**
   - Detects `postgresql://` and `postgres://` prefixes
   - Used consistently everywhere a branch on engine type is needed

5. **`app/main.py` — `_connect()`**
   - SQLite branch: handles `sqlite:///./` prefix stripping and the `:memory:` special case with `_memory_keeper`
   - PostgreSQL branch: calls `psycopg2.connect(url)` and sets `autocommit = False`; returns raw connection (NOT a wrapper — that is T3's job)

6. **`app/main.py` — `get_db()`**
   - SQLite path: sets `conn.row_factory = sqlite3.Row`, yields connection
   - PostgreSQL path: yields the raw psycopg2 connection without RealDictCursor — T3 replaces this with `_PgConnectionWrapper`
   - Both paths `yield conn` and `finally: conn.close()`

7. **`app/main.py` — `AuthGate`**
   - Uses `_connect(DATABASE_URL)` (not a hardcoded `sqlite3.connect(...)`)
   - Sets `row_factory = sqlite3.Row` for SQLite path only; no cursor factory changes for PostgreSQL

8. **Placeholder comment**
   - A comment in `main.py` explicitly documents that service layer uses `?` placeholders, PostgreSQL needs `%s`, and T3 handles this
   - The service layer SQL must NOT have been modified to use `%s` in this task

9. **`docs/deployment.md`**
   - File exists (stub)
   - States: hosting model = Azure App Service (Linux), runtime = Python 3.11+
   - Does NOT contain a full runbook (T5 scope) or secrets

10. **Run tests and lint:**

```bash
pytest -v
ruff check .
```

Expected: all existing tests pass (SQLite path is unchanged), ruff clean.

---

## Required Output Format

### 1. Verdict

```text
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```text
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/main.py`, `requirements.txt`, `docs/deployment.md`, and iteration planning files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] `psycopg2-binary>=2.9.0` in `requirements.txt` (binary, not `psycopg2`)
- [PASS|FAIL] `DATABASE_URL` defaults to `sqlite:///./cashflow.db`
- [PASS|FAIL] `_is_postgres()` correctly identifies both `postgresql://` and `postgres://`
- [PASS|FAIL] `_connect()` returns `sqlite3.Connection` for SQLite and psycopg2 connection for PostgreSQL
- [PASS|FAIL] `get_db()` sets `row_factory` for SQLite; yields raw psycopg2 connection for PostgreSQL (wrapper is T3)
- [PASS|FAIL] `AuthGate` uses `_connect()` and sets `row_factory` for SQLite only
- [PASS|FAIL] `:memory:` SQLite path preserved (`_memory_keeper` pattern intact)
- [PASS|FAIL] `?` vs `%s` placeholder compatibility note present — no premature fix in service layer
- [PASS|FAIL] `docs/deployment.md` stub created with hosting model decision
- [PASS|FAIL] no `db/init_db.py` or `db/schema.sql` changes
- [PASS|FAIL] no `ENVIRONMENT` / secrets / `.env.example` work
- [PASS|FAIL] no health endpoint, logging, WhiteNoise, or CI/CD work
- [PASS|FAIL] `pytest -v` passes
- [PASS|FAIL] `ruff check .` passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

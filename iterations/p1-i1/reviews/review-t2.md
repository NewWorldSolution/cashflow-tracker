# Review — I1-T2: FastAPI Skeleton
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i1/t2-fastapi`
**PR target:** `feature/phase-1/iteration-1`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/__init__.py           ← empty package init
app/main.py               ← FastAPI app factory, session middleware, get_db(), opening balance gate
app/routes/__init__.py    ← empty package init
```

### Required behaviour

1. `SECRET_KEY` not set → `RuntimeError` at import time with descriptive message
2. `get_db()` → FastAPI dependency yielding `sqlite3.Connection` with `row_factory = sqlite3.Row`, closed in `finally`
3. Opening balance gate → redirect (302) to `/settings/opening-balance` for any request path not in the exempt list, when `opening_balance` key is absent from the settings table
4. `/settings/opening-balance` is exempt from the gate
5. Session middleware uses `SECRET_KEY` from env
6. `create_app(database_url=None)` function exists for test injection
7. No validation logic in `app/main.py` — infrastructure only

---

## Architecture principles to check

| # | Principle |
|---|-----------|
| 5 | No silent failures — `SECRET_KEY` missing must raise, not default silently |
| 6 | Identity — session will store `users.id` (integer); `get_db()` enables FK resolution |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i1/t2-fastapi
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-1
# Expected: app/__init__.py, app/main.py, app/routes/__init__.py only
```

### Step 3 — SECRET_KEY guard

Read `app/main.py`. Find where `SECRET_KEY` is loaded.

```bash
grep -n "SECRET_KEY" app/main.py
```

The check must:
- Occur at module load time (not inside a request handler)
- Raise a descriptive exception (`RuntimeError` or equivalent)
- Never fall back to a hardcoded default key

If `SECRET_KEY` defaults to a string literal = `CHANGES REQUIRED` (critical).

### Step 4 — get_db() contract

Read the `get_db` function. Verify:
- Uses `yield` (FastAPI generator dependency)
- Sets `conn.row_factory = sqlite3.Row`
- Has a `try/finally` block that calls `conn.close()`

```bash
grep -n "row_factory\|finally\|conn.close\|yield" app/main.py
```

### Step 5 — Opening balance gate

Read the gate implementation. Verify:
- Returns a `RedirectResponse(url="/settings/opening-balance", status_code=302)` when balance is missing
- The gate is registered as a dependency — not hardcoded inside each route
- `/settings/opening-balance` is exempt

```bash
grep -n "RedirectResponse\|opening.balance\|exempt" app/main.py
```

### Step 6 — Session middleware

```bash
grep -n "SessionMiddleware\|add_middleware" app/main.py
```

Verify `SessionMiddleware` is added with `secret_key=SECRET_KEY` (the env variable), not a literal.

### Step 7 — No validation logic

Read `app/main.py` in full. It must contain no business rules (no VAT checks, no category checks, no `logged_by` logic). Infrastructure only.

### Step 8 — Test the SECRET_KEY guard

```bash
# Unset SECRET_KEY and try to import
SECRET_KEY= python -c "from app.main import app" 2>&1
# Expected: RuntimeError or similar with a message about SECRET_KEY
```

### Step 9 — Test the gate

```bash
SECRET_KEY=test-key python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app, raise_server_exceptions=True)
r = client.get('/', follow_redirects=False)
print(r.status_code, r.headers.get('location'))
# Expected: 302, /settings/opening-balance
"
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every item implemented correctly with file and line references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: app/main.py:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/__init__.py`, `app/main.py`, `app/routes/__init__.py`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] Missing SECRET_KEY raises at import time with descriptive message
- [PASS|FAIL] App starts normally with SECRET_KEY set
- [PASS|FAIL] get_db() yields connection with row_factory = sqlite3.Row, closes in finally
- [PASS|FAIL] Any non-exempt path redirects (302) to /settings/opening-balance when balance not set
- [PASS|FAIL] /settings/opening-balance is exempt from the gate
- [PASS|FAIL] No validation logic in app/main.py
- [PASS|FAIL] create_app() accepts database_url override for testing
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# Review — I2-T4: Middleware + Base Template
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i2/t4-middleware`
**PR target:** `feature/phase-1/iteration-2`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/main.py              ← AuthGate replaces OpeningBalanceGate; auth + dashboard routers registered
app/templates/base.html  ← nav with username and POST logout button
```

### AuthGate requirements

| Requirement | Detail |
|-------------|--------|
| Replaces | `OpeningBalanceGate` fully removed, `AuthGate` in its place |
| Single middleware | NOT added alongside old middleware — one combined class only |
| EXEMPT_PATHS | `/settings/opening-balance`, `/auth/login`, `/auth/logout`, `/favicon.ico` |
| EXEMPT_PREFIXES | `/static`, `/docs`, `/openapi.json` |
| `_is_exempt()` | Normalises trailing slash; uses `normalised.startswith()` for prefix checks |
| Evaluation order | Opening balance first, then auth |
| DB connection | Single `conn` with `try/finally conn.close()` for both checks |
| No inline SQL | Calls `get_opening_balance(conn)` and `get_current_user(request, conn)` from auth_service |
| `row_factory` | `conn.row_factory = sqlite3.Row` set after `_connect()` |
| Attaches user | `request.state.user = user` before `call_next` |

---

## Architecture principles to check

| # | Principle | Check |
|---|-----------|-------|
| 5 | No silent failures — no `except: pass` in middleware | grep |
| 8 | auth_service is single source of truth — no inline user lookup or SQL in middleware | grep |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i2/t4-middleware
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-2
# Expected: app/main.py and app/templates/base.html only
```

### Step 3 — OpeningBalanceGate fully removed

```bash
grep -n "OpeningBalanceGate" app/main.py
# Expected: no output — class must not exist anywhere in the file
```

If any reference to `OpeningBalanceGate` remains: `CHANGES REQUIRED`.

### Step 4 — Single AuthGate, not two middlewares

```bash
grep -n "add_middleware" app/main.py
```

Must show exactly two calls:
1. `app.add_middleware(SessionMiddleware, ...)`
2. `app.add_middleware(AuthGate)`

If there are three or more `add_middleware` calls: `CHANGES REQUIRED` (critical — ordering is reversed).

### Step 5 — EXEMPT_PATHS and EXEMPT_PREFIXES

```bash
grep -n "EXEMPT_PATHS\|EXEMPT_PREFIXES" app/main.py
```

Verify:
- `EXEMPT_PATHS` is a set containing: `/settings/opening-balance`, `/auth/login`, `/auth/logout`, `/favicon.ico`
- `EXEMPT_PREFIXES` is a tuple containing: `/static`, `/docs`, `/openapi.json`

### Step 6 — _is_exempt() uses normalised path for prefix check

Read `_is_exempt()`. Verify:
- Trailing slash normalised: `normalised = path.rstrip("/") or "/"`
- Exact match uses `normalised`
- Prefix check uses `normalised.startswith(prefix)` — NOT `path.startswith(prefix)`

```bash
grep -n "startswith\|normalised\|rstrip" app/main.py
```

### Step 7 — Single connection, try/finally

Read `AuthGate.dispatch`. Verify:
- One `conn = _connect(DATABASE_URL)` call
- `conn.row_factory = sqlite3.Row` set immediately after
- `try` block contains both `get_opening_balance(conn)` and `get_current_user(request, conn)`
- `finally: conn.close()` — no second `_connect()` call inside the try block

```bash
grep -n "_connect\|conn.close\|row_factory\|try\|finally" app/main.py
```

If `_connect()` is called more than once in `dispatch`: `CHANGES REQUIRED` (connection leak).

### Step 8 — No inline SQL in middleware

```bash
grep -n "SELECT\|INSERT\|UPDATE\|DELETE" app/main.py
```

No raw SQL should appear in `AuthGate.dispatch`. Middleware must delegate to `get_opening_balance`
and `get_current_user` from `app.services.auth_service`.

### Step 9 — Router registration

```bash
grep -n "include_router\|auth_router\|dashboard_router" app/main.py
```

Both `auth_router` and `dashboard_router` must be registered in `create_app()`.

### Step 10 — 11 existing tests still pass

```bash
pytest -v tests/test_init_db.py
# Expected: 11 passed, 0 failed
```

### Step 11 — Auth gate functional check

```bash
python -c "
import os; os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app, raise_server_exceptions=True, follow_redirects=False)
# Set opening balance
client.post('/settings/opening-balance', data={'opening_balance': '50000', 'as_of_date': '2026-01-01'})
# No session -> redirect to /auth/login
r = client.get('/')
assert r.status_code == 302 and '/auth/login' in r.headers['location'], \
    f'Auth gate failed: {r.status_code} {r.headers.get(\"location\")}'
print('auth gate: OK')
"
```

### Step 12 — base.html nav

```bash
grep -n "logout\|Sign out\|username\|request.state.user" app/templates/base.html
```

Verify:
- Nav with `{% if request.state.user %}` guard
- Username displayed: `request.state.user["username"]`
- Logout is a `<form method="post" action="/auth/logout">` — not an `<a href>` link

### Step 13 — No silent failures

```bash
grep -n "except.*pass\|except:$" app/main.py
# Expected: no output (OperationalError in OpeningBalanceGate was acceptable; AuthGate uses auth_service instead)
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
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/main.py` and `app/templates/base.html`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] App starts without error when SECRET_KEY is set
- [PASS|FAIL] OpeningBalanceGate fully removed
- [PASS|FAIL] AuthGate replaces it — exactly one AuthGate in add_middleware
- [PASS|FAIL] EXEMPT_PATHS: all 4 paths present (/settings/opening-balance, /auth/login, /auth/logout, /favicon.ico)
- [PASS|FAIL] EXEMPT_PREFIXES: /static, /docs, /openapi.json
- [PASS|FAIL] _is_exempt() uses normalised.startswith() for prefix checks
- [PASS|FAIL] Single conn with try/finally in AuthGate.dispatch — no connection leak
- [PASS|FAIL] conn.row_factory = sqlite3.Row set after _connect()
- [PASS|FAIL] No inline SQL in AuthGate — calls get_opening_balance() and get_current_user()
- [PASS|FAIL] auth_router and dashboard_router registered in create_app()
- [PASS|FAIL] GET / with no session → 302 → /auth/login (after opening balance set)
- [PASS|FAIL] base.html nav: username displayed, POST logout button
- [PASS|FAIL] Logout button is <form method="post"> — not a link
- [PASS|FAIL] Nav hidden when request.state.user not set (login page etc.)
- [PASS|FAIL] 11 existing tests still pass
- [PASS|FAIL] Scope: only app/main.py and app/templates/base.html modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

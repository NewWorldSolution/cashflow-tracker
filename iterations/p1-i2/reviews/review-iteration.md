# QA Review — P1-I2: Authentication (Full Iteration)
**Reviewer:** Claude Code (QA agent)
**Branch:** `feature/phase-1/iteration-2`
**PR target:** `main`
**Trigger:** Run this review only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i2/tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 2. You did not implement any of this code. Your job is to verify the complete iteration is correct before it merges to `main`. Individual task reviews (review-t1 through review-t5) verified each task in isolation. This review verifies the whole.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

A `PASS` here authorises the PR from `feature/phase-1/iteration-2` → `main`.

---

## What this iteration was supposed to deliver

1. Auth service layer (`app/services/auth_service.py`) — 5 functions, parameterised queries, bcrypt UTF-8
2. Login route (`GET/POST /auth/login`) with exact error message contract
3. Logout route (`POST /auth/logout`) — POST-only, session cleared
4. Placeholder dashboard (`GET /`) — confirms authenticated access
5. Login template (`app/templates/auth/login.html`) — extends base.html, password type="password"
6. `AuthGate` middleware replacing `OpeningBalanceGate` — single combined gate, correct evaluation order
7. `base.html` nav — username display and POST logout button for authenticated users
8. 25 passing tests (11 P1-I1 + 14 new), ruff clean

---

## Architecture principles — every one must hold

| # | Principle | Grep check |
|---|-----------|------------|
| 5 | No silent failures | `grep -rn "except.*pass\|except:$" app/ tests/` → no output |
| 6 | Identity via integer FK — session stores `users.id` integer | `grep -rn "session\[.user_id.\]" app/` → only integer assignment |
| 8 | auth_service is single source of truth | `grep -rn "checkpw\|SELECT.*users" app/main.py app/routes/` → no output |

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-2
git pull origin feature/phase-1/iteration-2
```

Confirm all task branches are merged:

```bash
git log --oneline --graph | head -25
# All 5 task branches should appear as merged commits
```

### Step 2 — Full test suite

```bash
pytest -v
# Expected: 25 passed (11 P1-I1 + 14 new auth), 0 failed, exit code 0
# Any failure: CHANGES REQUIRED immediately

ruff check .
# Expected: no issues, exit code 0
```

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Files that MUST appear in the diff (changed or added relative to main):

```
# New implementation files
app/routes/auth.py
app/routes/dashboard.py
app/services/__init__.py
app/services/auth_service.py
app/templates/auth/login.html
app/templates/dashboard.html
tests/test_auth.py

# Modified implementation files
app/main.py
app/templates/base.html

# Iteration spec files (added when iteration was bootstrapped)
iterations/p1-i2/prompt.md
iterations/p1-i2/tasks.md
iterations/p1-i2/prompts/t1-auth-service.md
iterations/p1-i2/prompts/t2-auth-routes.md
iterations/p1-i2/prompts/t3-login-template.md
iterations/p1-i2/prompts/t4-middleware.md
iterations/p1-i2/prompts/t5-tests.md
iterations/p1-i2/reviews/review-t1.md
iterations/p1-i2/reviews/review-t2.md
iterations/p1-i2/reviews/review-t3.md
iterations/p1-i2/reviews/review-t4.md
iterations/p1-i2/reviews/review-t5.md
iterations/p1-i2/reviews/review-iteration.md
```

Files that must NOT appear in the diff (P1-I1 frozen — unchanged):

```
db/schema.sql
db/init_db.py
seed/categories.sql
seed/users.sql
app/routes/settings.py
tests/test_init_db.py
```

Any frozen file appearing as modified = scope violation. Any unexpected new file = scope violation.

### Step 4 — Architecture checks

```bash
# No silent failures
grep -rn "except.*pass\|except:$" app/ tests/
# Expected: no output

# No inline auth logic in middleware or routes (auth_service is single source)
grep -rn "checkpw\|bcrypt" app/main.py app/routes/
# Expected: no output — these must only appear in app/services/auth_service.py

# No raw SQL for user lookup outside auth_service
grep -rn "SELECT.*FROM users" app/main.py app/routes/
# Expected: no output

# No hard deletes
grep -rn "DELETE FROM\|\.delete(" app/ tests/
# Expected: no output (test_deleted_user uses DELETE — acceptable in tests only)

# No plaintext password comparison
grep -rn "password.*==" app/
# Expected: no output

# Session stores integer only
grep -rn "session\[.user_id.\]" app/
# Verify: only assignment is session["user_id"] = user["id"] (integer FK)
# Never: session["user_id"] = user["username"] or any string
```

### Step 5 — OpeningBalanceGate fully removed

```bash
grep -rn "OpeningBalanceGate" app/
# Expected: no output — must be completely gone
```

### Step 6 — Single AuthGate, correct structure

```bash
grep -n "add_middleware" app/main.py
# Expected: exactly 2 calls — SessionMiddleware and AuthGate
```

Read `AuthGate.dispatch`. Verify single connection pattern:

```bash
grep -n "_connect\|conn.close\|row_factory" app/main.py
```

There must be exactly one `_connect()` call inside `dispatch`, and `conn.row_factory = sqlite3.Row` must be set after it.

### Step 7 — EXEMPT_PATHS complete

```bash
grep -n "EXEMPT_PATHS\|EXEMPT_PREFIXES" app/main.py
```

`EXEMPT_PATHS` must include all 4: `/settings/opening-balance`, `/auth/login`, `/auth/logout`, `/favicon.ico`.
`EXEMPT_PREFIXES` must include `/static`, `/docs`, `/openapi.json`.

### Step 8 — Password field type

```bash
grep -n "type=" app/templates/auth/login.html
```

Password field must use `type="password"` — never `type="text"`.

### Step 9 — Logout is POST

```bash
grep -n "logout" app/templates/base.html
# Must find <form method="post" action="/auth/logout"> — not <a href>

grep -n "@router\." app/routes/auth.py | grep logout
# Must find @router.post — not @router.get
```

### Step 10 — End-to-end flows

```bash
python -c "
import os; os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app

app = create_app(database_url=':memory:')
client = TestClient(app, raise_server_exceptions=True, follow_redirects=False)

# 1. No balance set → opening balance gate fires first
r = client.get('/')
assert r.status_code == 302 and '/settings/opening-balance' in r.headers['location'], \
    f'Opening balance gate failed: {r.status_code}'

# 2. Set opening balance
r = client.post('/settings/opening-balance',
    data={'opening_balance': '50000', 'as_of_date': '2026-01-01'})
assert r.status_code == 302

# 3. Balance set, no session → auth gate fires
r = client.get('/')
assert r.status_code == 302 and '/auth/login' in r.headers['location'], \
    f'Auth gate failed: {r.status_code}'

# 4. Login with valid credentials
r = client.post('/auth/login', data={'username': 'owner', 'password': 'owner123'})
assert r.status_code == 302 and r.headers['location'] == '/', \
    f'Login redirect failed: {r.status_code} {r.headers.get(\"location\")}'

# 5. Authenticated → dashboard accessible
r = client.get('/', cookies=r.cookies)
assert r.status_code == 200, f'Dashboard failed: {r.status_code}'
assert 'owner' in r.text, 'Username not shown in dashboard'

# 6. SANDBOX banner present
assert 'SANDBOX' in r.text, 'SANDBOX banner missing'

print('All end-to-end flows: OK')
"
```

### Step 11 — Login error messages

```bash
python -c "
import os; os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app

app = create_app(database_url=':memory:')
client = TestClient(app, raise_server_exceptions=True, follow_redirects=False)
client.post('/settings/opening-balance', data={'opening_balance': '50000', 'as_of_date': '2026-01-01'})

r = client.post('/auth/login', data={'username': '', 'password': ''})
assert 'Username and password are required' in r.text, 'Empty fields error missing'

r = client.post('/auth/login', data={'username': 'nobody', 'password': 'x'})
assert 'Invalid credentials' in r.text, 'Wrong username error missing'

r = client.post('/auth/login', data={'username': 'owner', 'password': 'wrong'})
assert 'Invalid credentials' in r.text, 'Wrong password error missing'

print('Login error messages: OK')
"
```

### Step 12 — Frozen P1-I1 files unchanged

```bash
git diff main -- db/schema.sql db/init_db.py seed/categories.sql seed/users.sql app/routes/settings.py
# Expected: no output — these files must not be modified
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

Full list with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Architecture Violations

One section per principle. `None.` if clean.

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] pytest: 25 passed (11 P1-I1 + 14 new), 0 failed
- [PASS|FAIL] ruff clean
- [PASS|FAIL] OpeningBalanceGate fully removed
- [PASS|FAIL] AuthGate: single middleware, correct evaluation order (balance → auth)
- [PASS|FAIL] EXEMPT_PATHS: all 4 paths; EXEMPT_PREFIXES: all 3 prefixes
- [PASS|FAIL] Single conn with try/finally in AuthGate — no connection leak
- [PASS|FAIL] No inline SQL or bcrypt in middleware or routes
- [PASS|FAIL] session["user_id"] stores integer — never username string
- [PASS|FAIL] session.clear() before session["user_id"] on login
- [PASS|FAIL] Password type="password" in login.html — never type="text"
- [PASS|FAIL] Logout uses POST — never GET
- [PASS|FAIL] Error messages do not reveal which field caused login failure
- [PASS|FAIL] Nav shows username and POST logout when authenticated; hidden on exempt routes
- [PASS|FAIL] SANDBOX banner on every page (inherited from base.html)
- [PASS|FAIL] No silent failures (no except: pass)
- [PASS|FAIL] P1-I1 frozen files unchanged (schema.sql, init_db.py, categories.sql, users.sql, settings.py)
- [PASS|FAIL] Scope: only expected files modified vs main
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

### 7. Final Recommendation

```
approve (merge feature/phase-1/iteration-2 → main)
| request changes (specific fixes required first)
| block (fundamental issue — approach must be reconsidered)
```

One sentence explaining the recommendation.

---

## If PASS — post-merge steps

```bash
# After merge to main is approved:
git checkout main
git pull origin main

# Update project.md — add what P1-I2 delivered under "What is built"
# Update iterations/p1-i2/tasks.md — set Status: ✔ COMPLETE, Last updated: today
```

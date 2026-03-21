# QA Review — P1-I1: Foundation (Full Iteration)
**Reviewer:** Claude Code (QA agent)
**Branch:** `feature/phase-1/iteration-1`
**PR target:** `main`
**Trigger:** Run this review only after ALL tasks (T1–T5) show ✅ DONE in `tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 1. You did not implement any of this code. Your job is to verify the complete iteration is correct before it merges to `main`. Individual task reviews (review-t1 through review-t5) verified each task in isolation. This review verifies the whole.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

A `PASS` here authorises the PR from `feature/phase-1/iteration-1` → `main`.

---

## What this iteration was supposed to deliver

1. A working FastAPI app that starts without error when `SECRET_KEY` is set
2. SQLite database with 5 tables, 22 categories, 3 bcrypt-hashed users
3. Idempotent `db/init_db.py` — safe to run twice
4. Opening balance setup page at `/settings/opening-balance`
5. Hard redirect gate — any other route redirects to opening balance until it is set
6. Settings audit trail — every write to settings creates a row in settings_audit
7. SANDBOX banner on every page
8. 11 passing tests, ruff clean

---

## Architecture principles — every one must hold

| # | Principle | Grep check |
|---|-----------|------------|
| 1 | No derived value columns in schema | `grep -r "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" db/schema.sql` → no output |
| 3 | No hard deletes | `grep -rn "DELETE FROM\|\.delete(" app/` → no output |
| 5 | No silent failures | `grep -rn "except.*pass\|except:$" app/ tests/` → no output |
| 7 | No stored derived values | already covered by #1 |

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-1
git pull origin feature/phase-1/iteration-1
```

Confirm all task branches are merged:
```bash
git log --oneline --graph | head -20
# All 5 task branches should appear as merged commits
```

### Step 2 — Full test suite

```bash
pytest -v
# Expected: 11 passed, 0 failed, exit code 0
# If any fail: CHANGES REQUIRED immediately

ruff check .
# Expected: no issues, exit code 0
```

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected files (and only these):
```
.env.example
.gitignore
app/__init__.py
app/main.py
app/routes/__init__.py
app/routes/settings.py
app/templates/base.html
app/templates/settings/opening_balance.html
db/__init__.py
db/init_db.py
db/schema.sql
requirements.txt
seed/__init__.py
seed/categories.sql
seed/users.sql
tests/__init__.py
tests/test_init_db.py
```

Any file outside this list = scope violation.

### Step 4 — Architecture checks

```bash
# No CHECK constraint on vat_rate
grep "CHECK.*vat_rate" db/schema.sql
# Expected: no output

# No derived value columns
grep -i "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" db/schema.sql
# Expected: no output

# No hard deletes
grep -rn "DELETE FROM\|\.delete(" app/ tests/
# Expected: no output (except test teardown via DROP — that is acceptable)

# No silent failures
grep -rn "except.*pass\|except:$" app/ tests/
# Expected: no output

# No free-text categories
grep -rn "category[^_]" app/routes/ 2>/dev/null
# Expected: no string-typed category values — only category_id integers
```

### Step 5 — SECRET_KEY guard

```bash
python -c "from app.main import app" 2>&1
# Expected: RuntimeError or ImportError mentioning SECRET_KEY
# (because SECRET_KEY is not in the test environment)
```

### Step 6 — Idempotency

```bash
python db/init_db.py
python db/init_db.py
python -c "
import sqlite3
c = sqlite3.connect('cashflow.db')
print('categories:', c.execute('SELECT COUNT(*) FROM categories').fetchone()[0])
print('users:', c.execute('SELECT COUNT(*) FROM users').fetchone()[0])
"
# Expected: categories: 22, users: 3
```

### Step 7 — Bcrypt verification

```bash
python -c "
import sqlite3
c = sqlite3.connect('cashflow.db')
for r in c.execute('SELECT username, password_hash FROM users'):
    assert r[1].startswith('\$2b\$'), f'Plaintext detected: {r[0]}'
    print(f'{r[0]}: OK')
"
```

### Step 8 — Opening balance gate (end-to-end)

```bash
SECRET_KEY=test-key python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app

app = create_app(database_url=':memory:')
client = TestClient(app, raise_server_exceptions=True)

# Gate: no balance set → redirect
r = client.get('/', follow_redirects=False)
assert r.status_code == 302 and '/settings/opening-balance' in r.headers['location'], \
    f'Gate failed: {r.status_code}'

# Exempt: /settings/opening-balance accessible
r = client.get('/settings/opening-balance')
assert r.status_code == 200, f'Exempt path blocked: {r.status_code}'

# SANDBOX banner present
assert 'SANDBOX' in r.text, 'SANDBOX banner missing'

# POST valid data
r = client.post('/settings/opening-balance',
    data={'opening_balance': '50000', 'as_of_date': '2026-01-01'},
    follow_redirects=False)
assert r.status_code == 302, f'Valid POST failed: {r.status_code}'

# POST invalid data
r = client.post('/settings/opening-balance',
    data={'opening_balance': '-1', 'as_of_date': '2026-01-01'})
assert r.status_code == 400, f'Invalid POST not rejected: {r.status_code}'

print('All gate checks: OK')
"
```

### Step 9 — SANDBOX banner

```bash
SECRET_KEY=test-key python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app)
r = client.get('/settings/opening-balance')
assert 'SANDBOX' in r.text
assert 'test environment' in r.text
assert 'Data may be discarded' in r.text
print('SANDBOX banner: OK')
"
```

### Step 10 — .env protection

```bash
cat .gitignore | grep "\.env"
# Expected: .env present
git ls-files .env
# Expected: no output — .env must not be tracked
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
- [PASS|FAIL] pytest: 11 passed, 0 failed
- [PASS|FAIL] ruff clean
- [PASS|FAIL] db/init_db.py idempotent (runs twice, no duplicates)
- [PASS|FAIL] All 5 tables present
- [PASS|FAIL] 22 categories, 3 bcrypt-hashed users
- [PASS|FAIL] Opening balance saves to settings + audit row
- [PASS|FAIL] Gate redirects non-exempt routes when balance not set
- [PASS|FAIL] SANDBOX banner on every page
- [PASS|FAIL] SECRET_KEY missing → startup failure
- [PASS|FAIL] .env gitignored
- [PASS|FAIL] No vat_rate CHECK in schema
- [PASS|FAIL] No hard deletes
- [PASS|FAIL] No silent failures
- [PASS|FAIL] Scope: only expected files modified vs main
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

### 7. Final Recommendation

```
approve (merge feature/phase-1/iteration-1 → main)
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
git branch -d feature/phase-1/iteration-1

# Update project.md — add what P1-I1 delivered
# Update iterations/p1-i1/tasks.md — set Status: ✔ COMPLETE
```

# Review — I1-T3: Opening Balance Route
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i1/t3-balance`
**PR target:** `feature/phase-1/iteration-1`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### File

```
app/routes/settings.py    ← GET and POST /settings/opening-balance
```

One file only. Any other file created = scope violation.

### Required behaviour

1. `GET /settings/opening-balance` → render `settings/opening_balance.html` with `current_balance`, `current_date`, `error=None`
2. `POST /settings/opening-balance` with valid data → save to settings table, write audit rows to settings_audit, redirect to `/`
3. `POST` with `opening_balance <= 0` → return template with `status_code=400`, error shown inline, form not reset
4. `POST` with malformed `as_of_date` (not ISO 8601 YYYY-MM-DD) → 400 with inline error
5. `settings_audit.old_value` → `NULL` on first write (not empty string)
6. Both keys (`opening_balance` and `as_of_date`) saved and audited in one request
7. No validation logic outside this file — no business rules in `app/main.py`

---

## Architecture principles to check

| # | Principle |
|---|-----------|
| 5 | No silent failures — validation errors surfaced explicitly, not swallowed |
| 8 | Validation in service layer — for this iteration, the route itself is acceptable since there is no service layer yet, but the logic must not leak to `app/main.py` or templates |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i1/t3-balance
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-1
# Expected: app/routes/settings.py only
```

Any other file = scope violation.

### Step 3 — Read the file in full

Read `app/routes/settings.py`. Count lines. Understand the complete implementation before filing findings.

### Step 4 — Validation logic check

```bash
grep -n "except.*pass\|except:$" app/routes/settings.py
# Expected: no output
```

```bash
grep -n "opening_balance\|as_of_date" app/main.py 2>/dev/null
# Expected: no validation logic in main.py — infrastructure only
```

### Step 5 — old_value NULL check

Read the POST handler. Find where `settings_audit` is written. Verify:
- `old_value` is fetched from `settings` before the INSERT/UPDATE
- If the key does not exist yet, `old_value` is `None` (Python) → stored as `NULL` (SQLite)
- Not stored as `""` or `"0"` or any default

```bash
grep -n "old_value\|INSERT INTO settings_audit" app/routes/settings.py
```

### Step 6 — Form preservation on error

Read the error branch of the POST handler. Verify:
- On 400, the template is returned (not a redirect)
- `current_balance` and `current_date` are populated from the submitted values (not wiped)
- `status_code=400` is set on the `TemplateResponse`

### Step 7 — Functional test

```bash
# Run a live test against the actual app
SECRET_KEY=test-key python -m pytest -x -q 2>/dev/null || true

# Or manual test
SECRET_KEY=test-key python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app)

# Test: negative balance rejected
r = client.post('/settings/opening-balance',
    data={'opening_balance': '-100', 'as_of_date': '2026-01-01'})
print('negative:', r.status_code)  # Expected: 400

# Test: malformed date rejected
r = client.post('/settings/opening-balance',
    data={'opening_balance': '1000', 'as_of_date': '21-03-2026'})
print('bad date:', r.status_code)  # Expected: 400

# Test: valid data
r = client.post('/settings/opening-balance',
    data={'opening_balance': '50000', 'as_of_date': '2026-01-01'},
    follow_redirects=False)
print('valid:', r.status_code)  # Expected: 302
"
```

### Step 8 — Hard delete check

```bash
grep -in "delete from\|\.delete\b" app/routes/settings.py
# Expected: no output
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

File and line references for everything correct.

### 3. Problems Found

```
- severity: critical | major | minor
  file: app/routes/settings.py:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/routes/settings.py`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] GET renders form with current_balance, current_date, error=None
- [PASS|FAIL] POST with valid data saves opening_balance and as_of_date to settings
- [PASS|FAIL] POST with valid data writes 2 audit rows to settings_audit
- [PASS|FAIL] First write: settings_audit.old_value is NULL (not empty string)
- [PASS|FAIL] POST with opening_balance = 0 → 400 with inline error
- [PASS|FAIL] POST with opening_balance = -100 → 400
- [PASS|FAIL] POST with as_of_date = "21-03-2026" → 400
- [PASS|FAIL] POST with as_of_date = "2026-01-01" → 302 redirect to /
- [PASS|FAIL] Error response preserves submitted field values (form not reset)
- [PASS|FAIL] No except: pass
- [PASS|FAIL] No validation logic in app/main.py
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

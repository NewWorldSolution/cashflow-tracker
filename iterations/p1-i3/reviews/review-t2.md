# Review — I3-T2: Transaction Routes
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i3/t2-routes`
**PR target:** `feature/phase-1/iteration-3`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/routes/transactions.py
app/main.py                  ← transactions router registration only
```

### Required behaviour

- `GET /transactions/new`
- `POST /transactions/new`
- `GET /transactions/`
- `GET /categories`

Routes must use `require_auth`, `validate_transaction`, and `calculations.py` correctly without re-implementing business rules inline.

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i3/t2-routes
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-3
# Expected: app/routes/transactions.py and app/main.py only
```

### Step 3 — Router import

```bash
python -c "from app.routes.transactions import router; print('router imports ok')"
```

### Step 4 — app/main.py change scope

```bash
git diff feature/phase-1/iteration-3 -- app/main.py
```

Verify only transactions router registration changed.

### Step 5 — POST flow

Read `POST /transactions/new` and verify:
- `require_auth(request)` used
- `logged_by` comes from session user
- `validate_transaction(data, db)` called
- validation failures return 422 with `errors` and `form_data`
- valid save uses explicit INSERT column list

### Step 6 — Normalisation boundary

Verify invalid user input cannot raise before validation runs.
String cleanup in the route is fine; conversion errors must surface as validation errors, not uncaught exceptions.

### Step 7 — List query and derived fields

Verify:
- `WHERE t.is_active = TRUE`
- `ORDER BY t.created_at DESC`
- `LIMIT 20`
- derived values attached in Python, not stored

### Step 8 — Categories JSON shape

Verify `/categories` returns:
- `category_id`
- `name`
- `label`
- `direction`
- `default_vat_rate`
- `default_vat_deductible_pct`

### Step 9 — Ruff

```bash
ruff check app/routes/transactions.py app/main.py
# Expected: clean
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

Files modified outside `app/routes/transactions.py` and `app/main.py`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] Router imports without error
- [PASS|FAIL] app/main.py only registers transactions router
- [PASS|FAIL] POST /transactions/new uses require_auth and validate_transaction
- [PASS|FAIL] logged_by comes from session, not form input
- [PASS|FAIL] Validation failures return 422 with errors + form_data
- [PASS|FAIL] Valid save uses explicit INSERT column list
- [PASS|FAIL] GET /transactions/ lists only active rows ordered by created_at DESC limit 20
- [PASS|FAIL] /categories JSON shape matches form.js contract
- [PASS|FAIL] Derived values are computed in Python, not stored
- [PASS|FAIL] Ruff clean
- [PASS|FAIL] Scope: only app/routes/transactions.py and app/main.py modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

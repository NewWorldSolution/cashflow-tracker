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

Verify only transactions router registration was added. No other changes to `app/main.py`.

### Step 5 — require_auth and logged_by source

```bash
grep -n "require_auth" app/routes/transactions.py
# Expected: called on every route handler that is not /categories (which is protected by AuthGate)

grep -n "logged_by" app/routes/transactions.py
# Must be assigned from session user, not from form data
# Expected pattern: logged_by = user["id"]  or  data["logged_by"] = user["id"]
# Must NOT see: logged_by = data.get("logged_by") or Form(...) for logged_by
```

### Step 6 — POST flow — validate_transaction called

Read `POST /transactions/new`. Verify:
- `require_auth(request)` is called first
- `validate_transaction(data, db)` is called with the normalised data dict and the live `db`
- On validation failure: re-renders `transactions/create.html` with `status_code=422`, passing `errors` and `form_data`

```bash
grep -n "validate_transaction\|status_code=422\|form_data" app/routes/transactions.py
# Expected: all three present
```

### Step 7 — No derived values in INSERT

Read the INSERT statement in `POST /transactions/new`. Verify that `vat_amount`, `net_amount`, `vat_reclaimable`, and `effective_cost` are NOT in the column list.

```bash
grep -n "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" app/routes/transactions.py
# If any appear in an INSERT context: CHANGES REQUIRED
# They may appear in GET /transactions/ for computation — that is fine
```

### Step 8 — Explicit INSERT column list

Read the INSERT statement. The column list must be explicit (no `INSERT INTO transactions VALUES (?,...)`). Verify it matches the spec:

```
INSERT INTO transactions (date, amount, direction, category_id, payment_method,
    vat_rate, income_type, vat_deductible_pct, description, logged_by)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

### Step 9 — Normalisation boundary: cast AFTER validation

Read the data normalisation code before `validate_transaction` is called. Verify:
- `date`, `amount`, `vat_rate`, `category_id`, `vat_deductible_pct` are passed as **strings** to `validate_transaction`
- Casting to `Decimal`, `float`, `int` happens only **after** `validate_transaction` returns `[]`

```bash
grep -n "Decimal\|int(data\|float(data" app/routes/transactions.py
# Expected: cast lines appear AFTER the `if errors:` block, not before validate_transaction
```

### Step 10 — List query: is_active, ORDER, LIMIT

Read `GET /transactions/`. Verify:

```bash
grep -n "is_active\|ORDER BY\|LIMIT\|created_at" app/routes/transactions.py
# Expected:
# WHERE t.is_active = TRUE (or 1)
# ORDER BY t.created_at DESC
# LIMIT 20
```

### Step 11 — Derived values computed in Python, not stored

Read `GET /transactions/`. Verify `vat_amount` and `effective_cost` (or similar) are computed per row in Python using `calculations.py`, not fetched from a stored column.

```bash
grep -n "from app.services.calculations import\|vat_amount\|effective_cost" app/routes/transactions.py
# Expected: import from calculations, used in list route to compute va/ec per row
```

### Step 12 — /categories JSON shape

Read `GET /categories`. Verify the JSON response contains exactly these fields per row:

```
category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct
```

```bash
grep -n "category_id\|default_vat_rate\|default_vat_deductible_pct" app/routes/transactions.py
# Expected: all three present in /categories response
```

### Step 13 — No SQL injection

```bash
grep -n "f\".*SELECT\|f'.*SELECT\|%.*SELECT\|\.format.*SELECT\|f\".*INSERT\|f'.*INSERT" app/routes/transactions.py
# Expected: no output — parameterised queries only
```

### Step 14 — Ruff

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
- [PASS|FAIL] app/main.py only registers transactions router — no other changes
- [PASS|FAIL] POST /transactions/new calls require_auth
- [PASS|FAIL] logged_by comes from session user id, not form input
- [PASS|FAIL] validate_transaction(data, db) called with live db
- [PASS|FAIL] Validation failures return 422 with errors + form_data
- [PASS|FAIL] No derived values (vat_amount/net_amount/vat_reclaimable/effective_cost) in INSERT
- [PASS|FAIL] INSERT uses explicit column list
- [PASS|FAIL] date/amount/vat_rate passed as strings to validate_transaction; cast only after validation passes
- [PASS|FAIL] GET /transactions/ filters WHERE is_active = TRUE, ORDER BY created_at DESC, LIMIT 20
- [PASS|FAIL] Derived values computed in Python via calculations.py, not stored/fetched
- [PASS|FAIL] /categories JSON shape has all 6 required fields
- [PASS|FAIL] No SQL string interpolation — parameterised queries only
- [PASS|FAIL] Ruff clean
- [PASS|FAIL] Scope: only app/routes/transactions.py and app/main.py modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

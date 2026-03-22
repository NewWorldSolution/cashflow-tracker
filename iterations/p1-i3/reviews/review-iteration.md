# QA Review — P1-I3: Transaction Capture (Full Iteration)
**Reviewer:** Claude Code (QA agent)
**Branch:** `feature/phase-1/iteration-3`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i3/tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 3. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What this iteration was supposed to deliver

1. Transaction validation service (`app/services/validation.py`)
2. VAT calculation service (`app/services/calculations.py`)
3. Transaction create/list/category routes (`app/routes/transactions.py`, `app/main.py`)
4. Create template (`app/templates/transactions/create.html`)
5. List template and `form.js` (`app/templates/transactions/list.html`, `static/form.js`)
6. Full regression-safe tests (`tests/test_validation.py`, `tests/test_transactions.py`)
7. No schema changes and no stored derived values

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-3
git pull origin feature/phase-1/iteration-3
```

### Step 2 — Full suite and lint

```bash
pytest -v
# Expected: 61 passed, 0 failed

ruff check .
# Expected: clean
```

### Step 3 — Scope verification

```bash
git diff --name-only main
```

**Expected files (all must be present):**
```
app/services/validation.py
app/services/calculations.py
app/services/__init__.py          (only if it did not exist before)
app/routes/transactions.py
app/main.py
app/templates/transactions/create.html
app/templates/transactions/list.html
static/form.js
tests/test_validation.py
tests/test_transactions.py
iterations/p1-i3/tasks.md
```

**Must NOT be modified (frozen P1-I1/P1-I2 files):**
```
db/schema.sql
db/init_db.py
seed/categories.sql
seed/users.sql
app/routes/auth.py
app/routes/settings.py
app/services/auth_service.py
app/templates/base.html
tests/test_auth.py
tests/test_init_db.py
```

Any frozen file appearing in the diff = `BLOCKED`.

### Step 4 — Architecture checks

```bash
grep -rn "except.*pass\|except:$" app/ tests/
# Expected: no output — no silent failures
```

```bash
grep -rn "password.*==" app/
# Expected: no output — no plaintext password comparison
```

```bash
grep -rn "checkpw\|bcrypt" app/routes/ app/main.py
# Expected: no output — auth logic stays in auth_service.py only
```

```bash
grep -rn "anthropic\|openai\|claude\|llm" app/services/ app/routes/
# Expected: no output — no LLM calls in logic layers
```

```bash
grep -rn "DELETE FROM\|\.delete(" app/ tests/
# Expected: no output — soft-delete only; no hard deletes
```

### Step 5 — No stored derived values

Read the INSERT statement in `app/routes/transactions.py`. Verify none of these columns appear in the INSERT:

```bash
grep -n "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" app/routes/transactions.py
# If any appear in an INSERT context: CHANGES REQUIRED
# They may appear in GET /transactions/ for computation — that is fine; inspect the context
```

Also verify `app/services/calculations.py` contains no database writes:

```bash
grep -n "execute\|INSERT\|UPDATE\|conn\|db\." app/services/calculations.py
# Expected: no output
```

### Step 6 — Validation rules in service layer only

```bash
grep -rn "vat_rate.*not in\|income_type.*None\|vat_deductible_pct.*None\|category_id.*FK\|direction.*income\|direction.*expense" app/routes/
# Expected: no output — business rules must NOT be re-implemented in routes
# validate_transaction in app/services/validation.py is the single source of truth
```

### Step 7 — logged_by always from session

```bash
grep -n "logged_by" app/routes/transactions.py
# Expected: assigned from session user (user["id"] or similar)
# Must NOT be read from form data
grep -n "Form.*logged_by\|logged_by.*Form\|data\[.logged_by.\].*form\|request\.form.*logged_by" app/routes/transactions.py
# Expected: no output
```

### Step 8 — End-to-end flow

Verify by code inspection (no need to run the server):

- `GET /transactions/new`: requires auth, returns 200 with create template
- `POST /transactions/new` invalid: returns 422 with errors and preserved form_data
- `POST /transactions/new` valid: inserts row and redirects 302 to `/transactions/`
- `GET /transactions/`: filters `WHERE is_active = TRUE`, `ORDER BY created_at DESC`, `LIMIT 20`; derived values attached in Python
- `GET /categories`: returns JSON with all 6 required fields per category row

### Step 9 — /categories JSON contract for form.js

```bash
grep -n "default_vat_rate\|default_vat_deductible_pct\|category_id\|\"name\"\|\"label\"\|\"direction\"" app/routes/transactions.py
# Expected: all 6 fields present in /categories response
# form.js depends on this shape — missing field breaks auto-defaults
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

One section per principle if needed. If clean: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] pytest: 61 passed, 0 failed
- [PASS|FAIL] ruff clean
- [PASS|FAIL] Validation rules enforced in service layer only — not re-implemented in routes
- [PASS|FAIL] No stored derived values (vat_amount/net_amount/vat_reclaimable/effective_cost not in INSERT)
- [PASS|FAIL] /transactions/new create flow works (GET 200, invalid POST 422 with errors, valid POST 302)
- [PASS|FAIL] /transactions/ recent list works (is_active filter, created_at DESC, LIMIT 20)
- [PASS|FAIL] /categories JSON shape matches form.js contract (all 6 fields)
- [PASS|FAIL] Multiple validation errors shown together (no early exit on first error)
- [PASS|FAIL] logged_by always comes from session user id — not injectable via form
- [PASS|FAIL] No silent failures (no except: pass)
- [PASS|FAIL] No LLM calls in services or routes
- [PASS|FAIL] No hard deletes in app code
- [PASS|FAIL] Frozen P1-I1/P1-I2 files unchanged
- [PASS|FAIL] Scope: only expected P1-I3 files differ from main
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# QA Review — P1-I4: Corrections, Hardening & Acceptance
**Reviewer:** Claude Code (QA agent)
**Branch:** `feature/phase-1/iteration-4`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T4) show ✅ DONE in `iterations/p1-i4/tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 4. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What this iteration was supposed to deliver

1. Transaction service for detail lookup and soft-delete execution
2. Five new detail/void/correct routes
3. Detail and void templates, plus minimal create/list template updates
4. Calculation unit tests and void/correct route tests
5. No hard deletes, no stored derived values, no form-driven identity fields

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-4
git pull origin feature/phase-1/iteration-4
```

### Step 2 — Full suite and lint

```bash
pytest -v
# Expected: 81 passed, 0 failed

ruff check .
# Expected: clean
```

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected implementation files (all must be present):

```text
app/services/transaction_service.py
app/routes/transactions.py
app/templates/transactions/detail.html
app/templates/transactions/void.html
app/templates/transactions/create.html
app/templates/transactions/list.html
tests/test_calculations.py
tests/test_transactions.py
iterations/p1-i4/tasks.md
```

Iteration planning/docs files will also appear in the diff — this is expected and matches the P1-I1/I2/I3 pattern:

```text
iterations/p1-i4/prompt.md
iterations/p1-i4/prompts/t1-transaction-service.md
iterations/p1-i4/prompts/t2-routes.md
iterations/p1-i4/prompts/t3-templates.md
iterations/p1-i4/prompts/t4-tests.md
iterations/p1-i4/reviews/review-t1.md  (and review-t2/t3/t4/iteration)
iterations/p1-i4/run.md
```

**Must NOT be modified (frozen P1-I1/P1-I2/P1-I3 files):**

```text
db/schema.sql
db/init_db.py
seed/categories.sql
seed/users.sql
app/routes/auth.py
app/routes/settings.py
app/services/auth_service.py
app/services/validation.py
app/services/calculations.py
app/templates/base.html
tests/test_auth.py
tests/test_init_db.py
tests/test_validation.py
```

Any frozen file appearing in the diff = `BLOCKED`.

### Step 4 — Architecture checks

```bash
grep -rn "DELETE FROM\|\.delete(" app/ tests/
# Expected: only pre-existing match in tests/test_auth.py:172 (frozen file, simulates deleted user)
# Any match in app/ code = BLOCKED

grep -rn "voided_by.*Form\|Form.*voided_by\|logged_by.*Form\|Form.*logged_by" app/routes/
# Expected: no output

grep -n "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" app/routes/transactions.py
# These will appear in the GET /transactions/ list handler (computing derived values for display)
# and the import line — both are CORRECT and pre-existing from P1-I3.
# ONLY flag if they appear in an INSERT statement context.

grep -n "execute\|INSERT\|UPDATE\|conn\|db\." app/services/calculations.py
# Expected: no output
```

### Step 5 — End-to-end flow by code inspection

Verify:

- detail route returns 200 or 404
- void GET/POST flow behaves correctly
- correct GET/POST flow behaves correctly
- list still filters inactive rows
- no hard delete logic appears in the app flow

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

If none: `None.`

### 5. Acceptance Criteria Check

- [PASS|FAIL] pytest: 81 passed, 0 failed
- [PASS|FAIL] ruff clean
- [PASS|FAIL] transaction_service added and used correctly
- [PASS|FAIL] detail/void/correct routes work by code inspection
- [PASS|FAIL] no stored derived values in INSERTs
- [PASS|FAIL] no hard deletes in app code
- [PASS|FAIL] voided_by and logged_by always from session — not injectable via form
- [PASS|FAIL] create/list template updates present
- [PASS|FAIL] detail and void templates present
- [PASS|FAIL] new tests added and aligned with iteration scope
- [PASS|FAIL] frozen P1-I1/I2/I3 files unchanged
- [PASS|FAIL] scope: only expected P1-I4 implementation + iteration docs differ from main

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

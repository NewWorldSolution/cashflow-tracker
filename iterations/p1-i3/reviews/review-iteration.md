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

1. Transaction validation service
2. VAT calculation service
3. Transaction create/list/category routes
4. Create template
5. List template and `form.js`
6. Full regression-safe tests
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

Must include expected P1-I3 files and must not include frozen P1-I1/P1-I2 files such as:
- `db/schema.sql`
- `db/init_db.py`
- `seed/categories.sql`
- `seed/users.sql`
- `app/routes/auth.py`
- `app/routes/settings.py`
- `app/services/auth_service.py`
- `app/templates/base.html`
- `tests/test_auth.py`
- `tests/test_init_db.py`

### Step 4 — Architecture checks

```bash
grep -rn "except.*pass\|except:$" app/ tests/
grep -rn "password.*==" app/
grep -rn "checkpw\|bcrypt" app/routes/ app/main.py
grep -rn "DELETE FROM\|\.delete(" app/ tests/
```

Expected:
- no silent failures
- no plaintext password comparison
- no inline auth logic in routes/main
- no hard deletes in app code

### Step 5 — No stored derived values

Review transaction insert/save logic. Verify `vat_amount`, `net_amount`, `vat_reclaimable`, and `effective_cost` are never inserted into the database and are computed at query/render time only.

### Step 6 — End-to-end flow

Verify:
- authenticated GET `/transactions/new` returns 200
- invalid POST returns 422 with preserved input and multiple errors
- valid POST saves and redirects to `/transactions/`
- list shows active rows only, newest first
- `/categories` returns the expected JSON shape

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
- [PASS|FAIL] Validation rules enforced in service layer only
- [PASS|FAIL] No stored derived values
- [PASS|FAIL] /transactions/new create flow works
- [PASS|FAIL] /transactions/ recent list works
- [PASS|FAIL] /categories JSON shape matches form.js contract
- [PASS|FAIL] Multiple validation errors shown together
- [PASS|FAIL] logged_by always comes from session user id
- [PASS|FAIL] Frozen P1-I1/P1-I2 files unchanged
- [PASS|FAIL] Scope: only expected P1-I3 files differ from main
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

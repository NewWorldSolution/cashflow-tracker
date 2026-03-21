# Review — I1-T5: Tests + Ruff + PR Ready
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i1/t5-tests`
**PR target:** `feature/phase-1/iteration-1`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Your specific job here: verify that tests actually test what they claim to test. A test that passes but masks a real bug is a `CHANGES REQUIRED` finding.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
tests/__init__.py          ← empty
tests/test_init_db.py      ← 11 tests
```

Two files only. No other files modified.

### Required tests — all 11 must exist

| Test function | What it must verify |
|---|---|
| `test_init_db_creates_all_tables` | All 5 tables exist after init |
| `test_init_db_is_idempotent` | Runs init twice, verifies no duplicate rows |
| `test_categories_count_is_22` | Exactly 22 rows in categories |
| `test_categories_income_count_is_4` | 4 income direction rows |
| `test_categories_expense_count_is_18` | 18 expense direction rows |
| `test_users_count_is_3` | Exactly 3 user rows |
| `test_users_passwords_are_hashed` | All `password_hash` values start with `$2b$` |
| `test_opening_balance_saves_to_settings` | Queries DB directly — not just checks status code |
| `test_opening_balance_writes_audit_row` | Asserts `old_value IS NULL` on first write |
| `test_opening_balance_rejects_negative` | 400 for negative balance |
| `test_missing_opening_balance_redirects` | 302 to `/settings/opening-balance` when not set |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i1/t5-tests
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-1
# Expected: tests/__init__.py, tests/test_init_db.py only
```

### Step 3 — Run tests

```bash
pytest -v tests/test_init_db.py
# Expected: 11 passed, 0 failed, exit code 0
```

If any test fails: `CHANGES REQUIRED` immediately.

### Step 4 — Ruff

```bash
ruff check .
# Expected: exit code 0, no issues
```

### Step 5 — Audit each test for assertion strength

Read `tests/test_init_db.py` in full. For each test, answer:

**test_init_db_is_idempotent**
- Does it call `initialise_db()` twice?
- Does it query row counts after the second run?
- A test that only calls init once cannot verify idempotency.

**test_users_passwords_are_hashed**
- Does it check `h.startswith("$2b$")` or equivalent?
- Checking `password_hash IS NOT NULL` alone is NOT sufficient — plaintext would pass that check.

**test_opening_balance_saves_to_settings**
- Does it query the database directly after the POST?
- A test that only checks `response.status_code == 302` does NOT verify the DB was written.

**test_opening_balance_writes_audit_row**
- Does it assert `old_value IS NULL` (not just that a row exists)?
- A test that only checks row count would pass even if `old_value` is wrong.

**test_missing_opening_balance_redirects**
- Does it use `follow_redirects=False`?
- Does it check `response.headers["location"]` contains `/settings/opening-balance`?
- A test using `follow_redirects=True` cannot verify the redirect itself.

### Step 6 — Check for silent exception swallowing

```bash
grep -n "except.*pass\|except:$" tests/test_init_db.py
# Expected: no output
```

### Step 7 — Fixture isolation

Read the fixtures. Verify:
- `db` fixture uses `:memory:` — no test writes to the real database
- `client` fixture uses `tmp_path` or equivalent — each test gets a fresh database
- Tests do not share state across runs

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

### 3. Problems Found

```
- severity: critical | major | minor
  file: tests/test_init_db.py:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Missing or Weak Tests

```
- test: test_function_name (missing | weak assertion)
  issue: what the assertion fails to verify
  suggestion: what a correct assertion would look like
```

If all tests are present and strong: `None.`

### 5. Scope Violations

Files modified outside `tests/__init__.py` and `tests/test_init_db.py`.

If none: `None.`

### 6. Acceptance Criteria Check

```
- [PASS|FAIL] All 11 required test functions exist by exact name
- [PASS|FAIL] pytest exits 0 with 11 passed, 0 failed
- [PASS|FAIL] ruff check . exits 0
- [PASS|FAIL] test_init_db_is_idempotent calls init twice
- [PASS|FAIL] test_users_passwords_are_hashed checks $2b$ prefix
- [PASS|FAIL] test_opening_balance_saves_to_settings queries DB, not just status code
- [PASS|FAIL] test_opening_balance_writes_audit_row asserts old_value is NULL
- [PASS|FAIL] test_missing_opening_balance_redirects uses follow_redirects=False
- [PASS|FAIL] Fixture isolation: in-memory db and tmp_path used
```

### 7. Exact Fixes Required

Numbered list. If PASS: `None.`

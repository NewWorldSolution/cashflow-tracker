# Review — I3-T5: Tests + Ruff + PR Ready
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i3/t5-tests`
**PR target:** `feature/phase-1/iteration-3`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
tests/test_validation.py
tests/test_transactions.py
iterations/p1-i3/tasks.md
```

### Required suite size

- 22 validation tests
- 14 route tests
- 61 total after merge (25 P1-I2 + 36 new P1-I3)

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i3/t5-tests
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-3
# Expected: tests/test_validation.py, tests/test_transactions.py, iterations/p1-i3/tasks.md only
```

### Step 3 — Test counts

```bash
grep -c "^def test_" tests/test_validation.py
# Expected: 22

grep -c "^def test_" tests/test_transactions.py
# Expected: 14
```

### Step 4 — Fixture shape

```bash
grep -n "^@pytest.fixture" tests/test_transactions.py
grep -n "def client\|def logged_out_client" tests/test_transactions.py
# Expected: exactly two fixtures — client and logged_out_client
# No third fixture (no fresh_client, no unauthenticated_client, etc.)
```

Verify `client` fixture:
- Sets opening balance (POST /settings/opening-balance)
- Logs in as owner (POST /auth/login)
- Exposes `c.db_path` attribute for direct db access tests

```bash
grep -n "opening-balance\|auth/login\|db_path" tests/test_transactions.py
# Expected: all three in the client fixture
```

Verify `logged_out_client` fixture:
- Sets opening balance
- Does NOT log in (no `/auth/login` call)

```bash
grep -n "logged_out_client" tests/test_transactions.py
# Expected: fixture definition and usage in test_unauthenticated_create_redirects
```

### Step 5 — Full suite

```bash
pytest -v
# Expected: 61 passed, 0 failed
```

### Step 6 — Ruff

```bash
ruff check .
# Expected: clean
```

### Step 7 — Spot checks: required test names present

```bash
grep -n "def test_multiple_errors_returned_together\|def test_expense_vat_rate_override_accepted\|def test_direction_category_match_accepted\|def test_invalid_date_format_rejected" tests/test_validation.py
# Expected: all four present
# test_expense_vat_rate_override_accepted verifies category VAT default is a suggestion not a constraint
# test_multiple_errors_returned_together verifies no early exit on first error
```

```bash
grep -n "def test_logged_by_set_from_session_not_form\|def test_transaction_list_ordered_by_created_at\|def test_unauthenticated_create_redirects" tests/test_transactions.py
# Expected: all three present
```

### Step 8 — logged_by forgery test verifies session value

Read `test_logged_by_set_from_session_not_form`. Verify:
- Posts a form with `logged_by=999` (or any non-owner id) in the form data
- Checks the saved row's `logged_by` value against the owner's actual session id
- Does NOT just check `!= 999` — must verify it equals the expected owner id

### Step 9 — unauthenticated redirect uses logged_out_client

```bash
grep -n "logged_out_client" tests/test_transactions.py
# Expected: used in test_unauthenticated_create_redirects
# Must NOT use the main `client` fixture (which is authenticated)
```

Verify the redirect target:
```bash
grep -n "auth/login" tests/test_transactions.py
# Expected: assertion that redirect location contains /auth/login
```

### Step 10 — Multiple errors test is a true multi-error test

Read `test_multiple_errors_returned_together` in `test_validation.py`. Verify:
- Two or more validation rules are violated simultaneously
- `len(errors) >= 2` is asserted (not just `errors != []`)

### Step 11 — tasks.md updated

```bash
grep -n "DONE\|COMPLETE\|I3-T5" iterations/p1-i3/tasks.md
# Expected: I3-T5 marked ✅ DONE and iteration status ✔ COMPLETE
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

Files modified outside `tests/test_validation.py`, `tests/test_transactions.py`, and `iterations/p1-i3/tasks.md`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] 22 validation tests present
- [PASS|FAIL] 14 transaction route tests present
- [PASS|FAIL] Fixtures: client and logged_out_client only (no third fixture)
- [PASS|FAIL] client fixture: opening balance set, logged in as owner, c.db_path accessible
- [PASS|FAIL] logged_out_client fixture: opening balance set, NOT logged in
- [PASS|FAIL] pytest -v passes with 61 total tests
- [PASS|FAIL] ruff check . clean
- [PASS|FAIL] test_multiple_errors_returned_together asserts len(errors) >= 2
- [PASS|FAIL] test_expense_vat_rate_override_accepted confirms VAT override is allowed
- [PASS|FAIL] test_logged_by_set_from_session_not_form verifies session id wins over form injection
- [PASS|FAIL] test_unauthenticated_create_redirects uses logged_out_client and checks /auth/login
- [PASS|FAIL] test_transaction_list_ordered_by_created_at verifies DESC order
- [PASS|FAIL] tasks.md marks I3-T5 DONE and iteration COMPLETE
- [PASS|FAIL] Scope: only allowed test files + tasks.md modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

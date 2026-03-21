# Review — I2-T5: Tests + Ruff + PR Ready
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i2/t5-tests`
**PR target:** `feature/phase-1/iteration-2`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
tests/test_auth.py               ← 14 new auth tests
iterations/p1-i2/tasks.md        ← status update only (I2-T5 DONE, iteration COMPLETE)
```

No other files. Existing files must not be modified.

### Required tests (14 total)

```
test_login_page_loads
test_login_success_redirects
test_login_sets_session_user_id
test_login_wrong_password
test_login_wrong_username
test_login_empty_fields
test_login_does_not_reveal_field
test_logout_clears_session
test_logout_must_be_post
test_protected_route_unauthenticated
test_protected_route_authenticated
test_authenticated_user_skips_login
test_opening_balance_gate_before_auth
test_deleted_user_treated_as_unauthenticated
```

### Required fixtures

```python
client(tmp_path)       ← fresh db, opening balance PRE-SET
fresh_client(tmp_path) ← fresh db, NO opening balance set
```

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i2/t5-tests
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-2
# Expected: tests/test_auth.py and iterations/p1-i2/tasks.md only
# Any other file = scope violation
```

### Step 3 — All 14 tests present

```bash
grep -c "^def test_" tests/test_auth.py
# Expected: 14

grep "^def test_" tests/test_auth.py
# Verify all 14 names match the spec exactly
```

### Step 4 — Two fixtures present

```bash
grep -n "^@pytest.fixture" tests/test_auth.py
# Expected: 2 fixtures
grep -n "def client\|def fresh_client" tests/test_auth.py
```

Verify `client` pre-sets opening balance before yielding. Verify `fresh_client` does NOT set opening balance.

### Step 5 — Full test suite passes

```bash
pytest -v
# Expected: 25 passed (11 P1-I1 + 14 new), 0 failed, exit code 0
```

If any test fails: `CHANGES REQUIRED` immediately.

### Step 6 — Ruff clean

```bash
ruff check .
# Expected: no issues, exit code 0
```

### Step 7 — Key test correctness checks

#### test_login_sets_session_user_id

This test must verify the session stores an integer, not just that login redirects.
Read the test. It should follow the login redirect and check that the dashboard renders correctly
(confirms user["id"] integer was stored, not username string).

#### test_login_does_not_reveal_field

Must compare error messages for wrong username vs wrong password. Verify the test checks that
both return the same message (`"Invalid credentials"`) — not just that each returns an error.

#### test_logout_must_be_post

Must verify `GET /auth/logout` returns 405.

```bash
grep -A5 "def test_logout_must_be_post" tests/test_auth.py
```

#### test_opening_balance_gate_before_auth

Must use `fresh_client` fixture (no opening balance). Must assert redirect goes to
`/settings/opening-balance`, not `/auth/login`.

```bash
grep -A8 "def test_opening_balance_gate_before_auth" tests/test_auth.py
```

#### test_deleted_user_treated_as_unauthenticated

Must:
1. Log in successfully (establishing a session)
2. Delete the user from the database directly via sqlite3
3. Hit a protected route with the stale session
4. Assert 302 redirect to `/auth/login`

```bash
grep -A15 "def test_deleted_user_treated_as_unauthenticated" tests/test_auth.py
```

If the test only sets `session["user_id"]` to a random integer without actually using a real
login + delete flow: acceptable, but verify the protected route response is still a redirect.

### Step 8 — No hardcoded database paths

```bash
grep -n "cashflow.db\|test.db" tests/test_auth.py
```

DB path must come from `tmp_path` — never hardcoded.

### Step 9 — tasks.md status update

```bash
grep "COMPLETE\|I2-T5.*DONE" iterations/p1-i2/tasks.md
# Expected: Status updated to ✔ COMPLETE, I2-T5 marked ✅ DONE
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

Files modified outside `tests/test_auth.py` and `iterations/p1-i2/tasks.md`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] pytest -v: 25 passed (11 P1-I1 + 14 new), exit code 0
- [PASS|FAIL] ruff check .: clean, exit code 0
- [PASS|FAIL] All 14 test names match spec exactly
- [PASS|FAIL] Two fixtures: client (balance pre-set) and fresh_client (no balance)
- [PASS|FAIL] test_login_sets_session_user_id verifies integer session (not just redirect)
- [PASS|FAIL] test_login_does_not_reveal_field compares both error messages
- [PASS|FAIL] test_logout_must_be_post verifies 405 on GET
- [PASS|FAIL] test_opening_balance_gate_before_auth uses fresh_client, asserts /settings/opening-balance redirect
- [PASS|FAIL] test_deleted_user_treated_as_unauthenticated logs in, deletes user, asserts /auth/login redirect
- [PASS|FAIL] No hardcoded database paths
- [PASS|FAIL] tasks.md: I2-T5 ✅ DONE, iteration ✔ COMPLETE
- [PASS|FAIL] Scope: only tests/test_auth.py and tasks.md modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

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
- 61 total after merge

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

### Step 7 — Spot checks

Verify:
- multiple-errors-together validation test exists
- logged_by-forgery route test exists
- list ordering test exists
- unauthenticated redirect test uses `logged_out_client`

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
- [PASS|FAIL] Fixtures: client and logged_out_client only
- [PASS|FAIL] pytest -v passes with 61 total tests
- [PASS|FAIL] ruff check . clean
- [PASS|FAIL] Validation suite covers multiple-errors-together
- [PASS|FAIL] Route suite verifies logged_by comes from session, not form input
- [PASS|FAIL] Route suite verifies unauthenticated create redirects to /auth/login
- [PASS|FAIL] Route suite verifies transaction list ordering
- [PASS|FAIL] tasks.md marks I3-T5 DONE and iteration COMPLETE
- [PASS|FAIL] Scope: only allowed test files + tasks.md modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

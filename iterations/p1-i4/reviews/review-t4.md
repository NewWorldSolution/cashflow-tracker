# Review — I4-T4: Tests + Close
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i4/t4-tests`
**PR target:** `feature/phase-1/iteration-4`

---

## Reviewer Role

Review only the changes in this task branch. Report problems precisely; do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `tests/test_calculations.py` with 10 new unit tests
- `tests/test_transactions.py` extended with 10 void/correct route tests
- `iterations/p1-i4/tasks.md` closed when green

---

## Review steps

1. Confirm scope is limited to the two test files plus `iterations/p1-i4/tasks.md`.
2. Verify there are exactly 10 tests in `test_calculations.py`.
3. Verify there are exactly 10 new void/correct route tests in `test_transactions.py`.
4. Confirm no new fixtures were added if the prompt forbids them.
5. Run:

```bash
pytest -v
ruff check .
```

Expected total after merge: **81 passed**.

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside the two test files plus `iterations/p1-i4/tasks.md`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] scope limited to the allowed files
- [PASS|FAIL] 10 calculation tests added
- [PASS|FAIL] 10 void/correct route tests added
- [PASS|FAIL] pytest -v passes with 81 total tests
- [PASS|FAIL] ruff clean
- [PASS|FAIL] tasks.md marks I4-T4 done and iteration complete

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

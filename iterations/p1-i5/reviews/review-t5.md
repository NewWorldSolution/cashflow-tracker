# Review — I5-T5: Flash Messages + Tests
**Branch:** `feature/p1-i5/t5-flash-tests`
**PR target:** `feature/phase-1/iteration-5`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/routes/transactions.py` — flash messages after create, void, correct
- Modified: `app/main.py` — flash middleware/context processor if needed
- Modified: `app/templates/base.html` — flash rendering adjustment if needed
- Extended: `tests/test_transactions.py` — 4 new flash tests

---

## Review steps

1. Confirm diff scope is limited to allowed files.
2. Verify flash set before redirect in: POST create, POST void, POST correct, POST opening balance.
3. Verify flash messages match spec: "Transaction saved successfully.", "Transaction voided.", "Transaction corrected. Original has been voided.", "Opening balance updated."
4. Verify flash pop happens in Python (middleware/context processor), not in Jinja2 template.
5. Verify 4 new tests: `test_flash_after_create`, `test_flash_after_void`, `test_flash_after_correct`, `test_flash_clears_after_display`.
6. Verify no business logic changes in routes — only flash message additions.
7. Run:

```bash
pytest -v   # Expected: 98 passed (94 existing + 4 new)
ruff check .
```

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

Files modified outside the allowed files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] flash after create with correct message
- [PASS|FAIL] flash after void with correct message
- [PASS|FAIL] flash after correct with correct message
- [PASS|FAIL] flash pop in Python, not Jinja2
- [PASS|FAIL] 4 new tests added and passing
- [PASS|FAIL] flash clears after one display (tested)
- [PASS|FAIL] no business logic changes
- [PASS|FAIL] total 98 tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

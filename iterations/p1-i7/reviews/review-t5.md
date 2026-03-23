# Review — I7-T5: Company + Accountant Tests
**Branch:** `feature/p1-i7/t5-tests`
**PR target:** `feature/phase-1/iteration-7`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Extended: `tests/test_transactions.py` — company and `for_accountant` coverage for final I7 behavior
- Extended: `tests/test_init_db.py` — migration/backfill coverage

---

## Review steps

1. Confirm diff scope is limited to `tests/test_transactions.py` and `tests/test_init_db.py`.
2. Verify migration/backfill tests cover:
   - companies table creation
   - company seed idempotency
   - `company_id` migration
   - `for_accountant` migration
   - backfill to company `id = 1`
3. Verify transaction tests cover successful create with a valid `company_id`.
4. Verify transaction tests cover invalid or missing `company_id`.
5. Verify transaction tests cover creating a transaction with `for_accountant = true`.
6. Verify transaction tests cover correction preserving/updating company.
7. Verify transaction tests cover correction preserving/updating `for_accountant`.
8. Verify transaction tests cover company filtering behavior.
9. Verify HTML assertions reflect final product behavior:
   - short company labels in list/filter/form
   - full company label in detail
   - always-visible accountant Yes/No in list/detail
   - `Logged by` removed from list
10. Verify tests use final company keys: `sp`, `ltd`, `ff`, `private`.
11. Run:

```bash
pytest -v
ruff check .
```

---

## Required output format

### 1. Verdict

```text
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```text
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `tests/test_transactions.py` and `tests/test_init_db.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to `tests/test_transactions.py` and `tests/test_init_db.py`
- [PASS|FAIL] migration/backfill tests cover T1 behavior
- [PASS|FAIL] tests cover valid `company_id` create flow
- [PASS|FAIL] tests cover invalid or missing `company_id`
- [PASS|FAIL] tests cover `for_accountant = true` create flow
- [PASS|FAIL] tests cover correction preserving/updating company
- [PASS|FAIL] tests cover correction preserving/updating `for_accountant`
- [PASS|FAIL] tests cover company filtering behavior
- [PASS|FAIL] tests assert final short/full company label behavior
- [PASS|FAIL] tests assert always-visible accountant Yes/No behavior
- [PASS|FAIL] tests assert `Logged by` removed from list
- [PASS|FAIL] tests use final company keys (`sp`, `ltd`, `ff`, `private`)
- [PASS|FAIL] full pytest suite passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

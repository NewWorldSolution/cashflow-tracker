# Review — I6-T5: voided_at Timestamp
**Branch:** `feature/p1-i6/t5-voided-at`
**PR target:** `feature/phase-1/iteration-6`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `db/schema.sql` — add `voided_at TIMESTAMP` column after `voided_by`
- Modified: `db/init_db.py` — idempotent migration for existing databases
- Modified: `app/services/transaction_service.py` — `void_transaction()` sets `voided_at = CURRENT_TIMESTAMP`
- Modified: `app/routes/transactions.py` — correct flow sets `voided_at` on original
- Modified: `app/templates/transactions/detail.html` — display `voided_at` for voided transactions
- Extended: `tests/test_transactions.py` — 3 new tests

---

## Review steps

1. Confirm diff scope matches allowed files only. No changes to `validation.py`, `calculations.py`, `form.js`, or any template other than `detail.html`.
2. Verify `db/schema.sql`: `voided_at TIMESTAMP` column exists after `voided_by`, nullable, no default.
3. Verify `db/init_db.py`: migration uses `ALTER TABLE transactions ADD COLUMN voided_at TIMESTAMP` wrapped in try/except (idempotent).
4. Verify `app/services/transaction_service.py`: `void_transaction()` UPDATE sets `voided_at = CURRENT_TIMESTAMP` alongside `is_active = 0, void_reason, voided_by`.
5. Verify `app/routes/transactions.py`: correct flow UPDATE sets `voided_at = CURRENT_TIMESTAMP` on the original transaction.
6. Verify `app/templates/transactions/detail.html`: `voided_at` displayed in void details section with `{% if t.voided_at %}` guard.
7. Verify test `test_voided_at_set_on_void` — voids a transaction and checks `voided_at IS NOT NULL`.
8. Verify test `test_voided_at_set_on_correct` — corrects a transaction and checks original's `voided_at IS NOT NULL`.
9. Verify test `test_voided_at_null_on_active` — creates a transaction and checks `voided_at IS NULL`.
10. Run:

```bash
pytest -v   # all 98 existing + 3 new tests must pass (101 total)
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

Files modified outside allowed list.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `voided_at TIMESTAMP` column in schema.sql (after voided_by)
- [PASS|FAIL] migration in init_db.py is idempotent
- [PASS|FAIL] `void_transaction()` sets `voided_at = CURRENT_TIMESTAMP`
- [PASS|FAIL] correct flow sets `voided_at` on original transaction
- [PASS|FAIL] detail.html displays `voided_at` for voided transactions
- [PASS|FAIL] `voided_at` is NULL for active transactions
- [PASS|FAIL] test: voided_at set on void
- [PASS|FAIL] test: voided_at set on correct
- [PASS|FAIL] test: voided_at null on active
- [PASS|FAIL] 3 new tests pass
- [PASS|FAIL] all 98 existing tests still pass (101 total)
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

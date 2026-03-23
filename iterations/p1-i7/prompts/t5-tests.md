# I7-T5 — Tests

**Branch:** `feature/p1-i7/t5-tests` (from `feature/phase-1/iteration-7`)
**PR target:** `feature/phase-1/iteration-7`
**Depends on:** I7-T1 ✅ DONE, I7-T2 ✅ DONE, I7-T3 ✅ DONE, I7-T4 ✅ DONE

---

## Goal

Add test coverage for the final I7 behavior:

- company seed/migration/backfill
- company create/correct/list/dashboard behavior
- short/full company labels
- `for_accountant` create/display/correction behavior
- `Logged by` removed from list

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i7/tasks.md
iterations/p1-i7/prompt.md
db/init_db.py
app/routes/transactions.py
app/routes/dashboard.py
tests/test_transactions.py
tests/test_init_db.py
```

---

## Allowed Files

```text
tests/test_transactions.py
tests/test_init_db.py
```

Do NOT modify application code in this task.

---

## What to Implement

### 1. `tests/test_init_db.py`

Cover migration/backfill behavior:

- companies table exists
- companies are seeded exactly once
- migration adds `company_id` to legacy schema
- migration adds `for_accountant` to legacy schema
- legacy rows are backfilled to company `id = 1`
- migration remains idempotent

### 2. `tests/test_transactions.py`

Cover final product behavior:

- create with valid `company_id`
- create fails without company
- create fails with invalid company
- create with `for_accountant = true`
- correct flow preserves or changes company
- correct flow can change `for_accountant`
- list filter by company
- dashboard filter by company if that behavior is testable in current suite
- detail shows full company label
- list/dashboard/form use short company labels where existing tests assert HTML
- list shows accountant Yes/No field
- detail shows accountant Yes/No field
- list no longer shows `Logged by`

Use final company keys and labels:

- `sp`
- `ltd`
- `ff`
- `private`

---

## Acceptance Check

```bash
ruff check .
pytest -v
```

- [ ] migration/backfill tests exist in `tests/test_init_db.py`
- [ ] create/correct company tests exist
- [ ] accountant create/correction tests exist
- [ ] company filter tests exist
- [ ] list/detail rendering assertions match final short/full label behavior
- [ ] list assertions reflect removed `Logged by`
- [ ] all tests pass
- [ ] ruff clean

# I6-T5 — voided_at Timestamp

**Branch:** `feature/p1-i6/t5-voided-at` (from `feature/phase-1/iteration-6`)
**PR target:** `feature/phase-1/iteration-6`
**Depends on:** — (independent, can run in parallel with T1–T4)

---

## Goal

Record and display when a transaction was voided. This was deferred from I5 because it requires a schema change.

---

## Read Before Starting

```
CLAUDE.md
db/schema.sql                                  (current schema)
app/services/transaction_service.py            (void_transaction function)
app/routes/transactions.py                     (correct flow voiding)
app/templates/transactions/detail.html         (void details section)
tests/test_transactions.py                     (existing void/correct tests)
```

---

## Allowed Files

```
db/schema.sql                                  ← modify
db/init_db.py                                  ← modify
app/services/transaction_service.py            ← modify
app/routes/transactions.py                     ← modify
app/templates/transactions/detail.html         ← modify
tests/test_transactions.py                     ← extend
```

Do NOT modify `validation.py`, `calculations.py`, `form.js`, or any other template.

---

## What to Implement

### 1. Schema change — `db/schema.sql`

Add `voided_at` column to the transactions table:

```sql
voided_at                  TIMESTAMP,
```

Place it after `voided_by` in the CREATE TABLE statement. Nullable, no default — only set when voiding.

### 2. Migration — `db/init_db.py`

Add migration logic for existing databases that don't have the column yet:

```python
# After schema creation, handle migration for existing DBs
try:
    conn.execute("ALTER TABLE transactions ADD COLUMN voided_at TIMESTAMP")
except Exception:
    pass  # Column already exists
```

This must be idempotent — safe to run multiple times.

### 3. Service change — `app/services/transaction_service.py`

In `void_transaction()`, set `voided_at` alongside the other void fields:

Find the UPDATE statement that sets `is_active = 0, void_reason = ?, voided_by = ?` and add `voided_at = CURRENT_TIMESTAMP`.

Read the current function to understand its exact structure before modifying.

### 4. Route change — `app/routes/transactions.py`

In `post_correct_transaction()`, the UPDATE that voids the original transaction also needs `voided_at = CURRENT_TIMESTAMP`:

Find the line:
```python
"SET is_active = 0, void_reason = 'Corrected', voided_by = ?, replacement_transaction_id = ? "
```

Add `voided_at = CURRENT_TIMESTAMP` to it.

### 5. Template change — `app/templates/transactions/detail.html`

In the void details section (inside the `{% if not t.is_active %}` block), add voided_at display.

If T2 has already extracted strings, use `{{ t('voided_at') }}`. If T2 hasn't run yet, use the hardcoded English label "Voided at" — T2 will extract it later.

```html
{% if t.voided_at %}
<dt>Voided at</dt><dd>{{ t.voided_at }}</dd>
{% endif %}
```

### 6. New tests — `tests/test_transactions.py`

Add 3 tests:

```python
def test_voided_at_set_on_void(client):
    """Voiding a transaction sets voided_at timestamp."""
    # Create a transaction, then void it
    # Verify voided_at is not NULL in the database

def test_voided_at_set_on_correct(client):
    """Correcting a transaction sets voided_at on the original."""
    # Create a transaction, then correct it
    # Verify the original's voided_at is not NULL

def test_voided_at_null_on_active(client):
    """Active transactions have voided_at = NULL."""
    # Create a transaction
    # Verify voided_at is NULL
```

Follow the pattern of existing tests in the file for setup (creating transactions, logging in, etc.).

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all 98 existing + 3 new tests must pass (101 total)
```

- [ ] `voided_at TIMESTAMP` column in schema.sql
- [ ] Migration in init_db.py handles existing DBs
- [ ] `void_transaction()` sets `voided_at = CURRENT_TIMESTAMP`
- [ ] Correct flow sets `voided_at` on the original transaction
- [ ] Detail page displays `voided_at` for voided transactions
- [ ] `voided_at` is NULL for active transactions
- [ ] 3 new tests pass
- [ ] All 98 existing tests still pass
- [ ] ruff clean

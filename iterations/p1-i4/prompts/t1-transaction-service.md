# I4-T1 — Transaction Service

**Owner:** Codex  
**Branch:** `feature/p1-i4/t1-transaction-service` (from `feature/phase-1/iteration-4`)  
**PR target:** `feature/phase-1/iteration-4`

---

## Goal

Add the transaction service layer for transaction detail lookup and soft-delete execution. This task is service-only: no routes, no templates, no tests.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i4/prompt.md
app/routes/transactions.py
app/services/validation.py
app/services/calculations.py
```

---

## Allowed Files

```
app/services/transaction_service.py
```

Do NOT modify any other file.

---

## What to Implement

Create `app/services/transaction_service.py` with:

```python
get_transaction(transaction_id: int, db: sqlite3.Connection) -> dict | None
void_transaction(transaction_id: int, void_reason: str, voided_by: int, db: sqlite3.Connection) -> None
```

### `get_transaction`

- Fetch a single transaction by id.
- Include joined fields:
  - `category_label`
  - `logged_by_username`
  - `voided_by_username` via `LEFT JOIN`
- Return a plain `dict` or `None`.

### `void_transaction`

- Raise `ValueError` if:
  - the transaction does not exist
  - the transaction is already voided
  - `void_reason.strip()` is empty
- On success:
  - `UPDATE transactions SET is_active=0, void_reason=?, voided_by=? WHERE id=?`
- Do not call `db.commit()`.

---

## Acceptance Check

```bash
python -c "from app.services.transaction_service import get_transaction, void_transaction; print('ok')"
ruff check app/services/transaction_service.py
```

# I4-T2 — Void/Correct Routes

**Owner:** Claude Code  
**Branch:** `feature/p1-i4/t2-routes` (from `feature/phase-1/iteration-4`)  
**PR target:** `feature/phase-1/iteration-4`  
**Depends on:** I4-T1 ✅ DONE

---

## Goal

Extend `app/routes/transactions.py` with detail, void, and correct flows. No templates are created in this task.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i4/prompt.md
iterations/p1-i4/prompts/t1-transaction-service.md
app/routes/transactions.py
app/services/validation.py
app/services/transaction_service.py
```

---

## Allowed Files

```
app/routes/transactions.py
```

Do NOT modify any other file.

---

## Routes to Implement

```text
GET  /transactions/{id}
GET  /transactions/{id}/void
POST /transactions/{id}/void
GET  /transactions/{id}/correct
POST /transactions/{id}/correct
```

### Required behavior

- All routes require `require_auth(request)`.
- Detail: `get_transaction(id, db)` and return 404 if missing.
- Void GET: return 404 if missing or already voided.
- Void POST:
  - read and strip `void_reason`
  - call `void_transaction(id, void_reason, user["id"], db)`
  - on `ValueError`, re-render `transactions/void.html` with `errors`, `form_data`, status 422
  - commit and redirect to `/transactions/` on success
- Correct GET:
  - return 404 if missing or already voided
  - pre-fill `create.html` using original transaction values
  - pass `form_action=f"/transactions/{id}/correct"`
- Correct POST:
  - normalise fields identically to `POST /transactions/new`
  - set `logged_by` from session, never from form
  - reuse `validate_transaction(data, db)`
  - on errors, re-render `create.html` with `errors`, `form_data`, `form_action`, status 422
  - on success:
    1. insert replacement transaction with explicit column list
    2. fetch `last_insert_rowid()`
    3. void original with `void_reason='Corrected'`, `voided_by=user["id"]`, `replacement_transaction_id=new_id`
    4. commit
    5. redirect 302 to `/transactions/`

### Guardrails

- Do not store derived values.
- Do not read `voided_by` or `logged_by` from form input.
- Do not duplicate field validation rules already owned by `validate_transaction`.
- Do not duplicate void precondition checks outside `void_transaction` for POST.

---

## Acceptance Check

```bash
python -c "from app.routes.transactions import router; print('ok')"
ruff check app/routes/transactions.py
```

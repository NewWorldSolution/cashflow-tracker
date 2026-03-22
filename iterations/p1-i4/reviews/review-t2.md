# Review — I4-T2: Void/Correct Routes
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i4/t2-routes`
**PR target:** `feature/phase-1/iteration-4`

---

## Reviewer Role

Review only the changes in this task branch. Report problems precisely; do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Extend `app/routes/transactions.py` with:
  - `GET /transactions/{id}`
  - `GET /transactions/{id}/void`
  - `POST /transactions/{id}/void`
  - `GET /transactions/{id}/correct`
  - `POST /transactions/{id}/correct`

Key contracts:
- auth required on all routes
- POST void uses `void_transaction`
- POST correct reuses `validate_transaction`
- no derived values stored
- `logged_by` and `voided_by` come from session only

---

## Review steps

1. Confirm scope is `app/routes/transactions.py` only.
2. Inspect each new route for auth and 404 behavior.
3. Verify POST void catches `ValueError` and re-renders with status 422.
4. Verify correct POST normalises like create POST, reuses `validate_transaction`, inserts replacement row, voids original, commits, redirects.
5. Confirm no `DELETE` statements and no derived values in INSERT.
6. Run:

```bash
python -c "from app.routes.transactions import router; print('ok')"
ruff check app/routes/transactions.py
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

Files modified outside `app/routes/transactions.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to transactions.py
- [PASS|FAIL] all five routes added
- [PASS|FAIL] all routes require auth
- [PASS|FAIL] POST void uses void_transaction and handles ValueError with 422 re-render
- [PASS|FAIL] POST correct reuses validate_transaction
- [PASS|FAIL] POST correct inserts replacement, links original via replacement_transaction_id, and commits
- [PASS|FAIL] no derived values stored in INSERT
- [PASS|FAIL] logged_by and voided_by come from session only
- [PASS|FAIL] import check passes
- [PASS|FAIL] ruff check passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

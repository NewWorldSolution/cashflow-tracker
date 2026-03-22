# P1-I4 — Corrections, Hardening & Acceptance
## Task Board

**Status:** ⏳ WAITING
**Last updated:** 2026-03-22 — branch created, iteration ready to start
**Iteration branch:** `feature/phase-1/iteration-4` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-4` → `main` ← QA agent approves before merge

---

## Dependency Map

```
I4-T1 (transaction service: get_transaction + void_transaction)
  └── I4-T2 (void/correct routes)
        └── I4-T3 (void/correct templates)
              └── I4-T4 (tests + close)
```

Sequential: each task depends on the previous one being ✅ DONE.

---

## Tasks

| ID    | Title                              | Owner       | Status     | Depends on | Branch                                    |
|-------|------------------------------------|-------------|------------|------------|-------------------------------------------|
| I4-T1 | Transaction service                | Codex       | ⏳ WAITING | —          | `feature/p1-i4/t1-transaction-service`    |
| I4-T2 | Void/correct routes                | Claude Code | ⏳ WAITING | I4-T1      | `feature/p1-i4/t2-routes`                |
| I4-T3 | Void/correct templates             | Claude Code | ⏳ WAITING | I4-T2      | `feature/p1-i4/t3-templates`             |
| I4-T4 | Tests + ruff + PR ready            | Codex       | ⏳ WAITING | I4-T3      | `feature/p1-i4/t4-tests`                 |

---

## Prompts & Reviews

| Task  | Implementation prompt                                    | Review prompt                              | Reviewer    |
|-------|----------------------------------------------------------|--------------------------------------------|-------------|
| I4-T1 | `iterations/p1-i4/prompts/t1-transaction-service.md`    | `iterations/p1-i4/reviews/review-t1.md`   | Claude Code |
| I4-T2 | `iterations/p1-i4/prompts/t2-routes.md`                 | `iterations/p1-i4/reviews/review-t2.md`   | Codex       |
| I4-T3 | `iterations/p1-i4/prompts/t3-templates.md`              | `iterations/p1-i4/reviews/review-t3.md`   | Codex       |
| I4-T4 | `iterations/p1-i4/prompts/t4-tests.md`                  | `iterations/p1-i4/reviews/review-t4.md`   | Claude Code |
| —     | —                                                        | `iterations/p1-i4/reviews/review-iteration.md` | Claude Code (QA) |

---

## Task Details

### I4-T1 — Transaction service (Codex)

**Goal:** Pure service layer. No routes, no templates. Database access only.

**Read first:** `iterations/p1-i4/prompts/t1-transaction-service.md`

**Allowed files:**
```
app/services/transaction_service.py    ← create new
```

**Functions to implement:**
```python
get_transaction(transaction_id: int, db: sqlite3.Connection) -> dict | None
    # SELECT t.*, c.label AS category_label, u.username AS logged_by_username,
    #        vb.username AS voided_by_username
    # FROM transactions t
    # JOIN categories c ON t.category_id = c.category_id
    # JOIN users u ON t.logged_by = u.id
    # LEFT JOIN users vb ON t.voided_by = vb.id
    # WHERE t.id = ?
    # Returns dict (row converted to plain dict) or None if not found

void_transaction(transaction_id: int, void_reason: str, voided_by: int, db: sqlite3.Connection) -> None
    # Preconditions (raise ValueError with message if violated):
    #   1. Transaction must exist
    #   2. Transaction must be active (is_active = TRUE)
    #   3. void_reason must be non-empty after strip()
    # UPDATE transactions SET is_active=0, void_reason=?, voided_by=? WHERE id=?
    # Does NOT commit — caller commits
```

**Acceptance check:**
```bash
python -c "from app.services.transaction_service import get_transaction, void_transaction; print('ok')"
```

**Done when:** Both functions importable; ruff clean; PR open → `feature/phase-1/iteration-4`.

---

### I4-T2 — Void/correct routes (Claude Code)

**Goal:** Five new route handlers wired to `transaction_service`. No templates created in this task.

**Depends on:** I4-T1 ✅ DONE

**Read first:** `iterations/p1-i4/prompts/t2-routes.md`

**Allowed files:**
```
app/routes/transactions.py    ← extend only
```

**Routes to implement:**
```
GET  /transactions/{id}           → detail view
GET  /transactions/{id}/void      → void confirmation form
POST /transactions/{id}/void      → execute void; redirect to /transactions/
GET  /transactions/{id}/correct   → pre-filled create form
POST /transactions/{id}/correct   → validate; insert new; void original; redirect to /transactions/
```

**Key contracts:**
- All routes require auth via `require_auth(request)`
- `voided_by` always from `user["id"]` — never from form
- `void_transaction` raises `ValueError` → catch, re-render void.html with error, status 422
- Correct POST: INSERT → last_insert_rowid → UPDATE original → commit → redirect 302
- 404 for missing transactions and for void/correct on already-voided transactions

**Acceptance check:**
```bash
python -c "from app.routes.transactions import router; print('ok')"
```

**Done when:** Router imports without error; ruff clean; PR open → `feature/phase-1/iteration-4`.

---

### I4-T3 — Void/correct templates (Claude Code)

**Goal:** Two new templates, two single-line modifications to existing templates.

**Depends on:** I4-T2 ✅ DONE

**Read first:** `iterations/p1-i4/prompts/t3-templates.md`

**Allowed files:**
```
app/templates/transactions/detail.html    ← create new
app/templates/transactions/void.html      ← create new
app/templates/transactions/create.html    ← one-line change: form_action variable
app/templates/transactions/list.html      ← one-line change: date cell links to detail
```

**Requirements:**
- `detail.html`: all fields display-only; conditional sections for income/expense; active → shows void/correct links; voided → shows void_reason, voided_by, replacement link if set
- `void.html`: transaction summary, void_reason text input, submit button, cancel link back to detail
- `create.html`: `<form ... action="{{ form_action | default('/transactions/new') }}">`
- `list.html`: `<td><a href="/transactions/{{ t.id }}">{{ t.date }}</a></td>`

**Acceptance check:**
```bash
python -c "
from fastapi.templating import Jinja2Templates
t = Jinja2Templates(directory='app/templates')
print('templates loadable ok')
"
```

**Done when:** Templates render without Jinja2 errors; ruff N/A; PR open → `feature/phase-1/iteration-4`.

---

### I4-T4 — Tests + ruff + PR ready (Codex)

**Goal:** Full test suite green, ruff clean, iteration closed.

**Depends on:** I4-T3 ✅ DONE

**Read first:** `iterations/p1-i4/prompts/t4-tests.md` and `iterations/p1-i4/prompt.md` "Tests Required" section.

**Allowed files:**
```
tests/test_calculations.py       ← create new (10 tests)
tests/test_transactions.py       ← extend (+10 tests)
iterations/p1-i4/tasks.md        ← status update only
```

**Test counts:**
- `tests/test_calculations.py`: 10 tests (direct unit tests, no DB)
- `tests/test_transactions.py`: +10 tests (void/correct route tests)
- Total after merge: **81 passed** (61 P1-I1/I2/I3 + 20 new P1-I4)

**Fixture note:** Use the existing `client` fixture from `test_transactions.py` for all new route tests. No new fixtures needed.

**Closure steps:**
1. `pytest` — 81 passed, exit code 0
2. `ruff check .` — clean, exit code 0
3. `git diff --name-only feature/phase-1/iteration-4` — only allowed files
4. `gh pr create --base feature/phase-1/iteration-4`
5. Update this file: I4-T4 status → ✅ DONE, iteration Status → ✔ COMPLETE

**Done when:** All tests pass; ruff clean; PR open → `feature/phase-1/iteration-4`.

---

## Agent Rules

1. **Read this file first.** Find your task. Confirm status is WAITING before starting.
2. **Update status to IN PROGRESS** before writing a line of code.
3. **Check dependencies.** Never start if any dep is not ✅ DONE.
4. **Branch:** check out `feature/phase-1/iteration-4` first, then create your task branch from it. No worktrees needed — tasks are sequential.
5. **PR targets the iteration branch**, not `main`. One task per PR.
6. **After completing:** set status to ✅ DONE. Add one-line note: what you produced.
7. **Never touch another agent's task.** Add notes under your own task only.
8. **If blocked:** set status to 🚫 BLOCKED with reason. Stop and wait.
9. **No `except: pass`, no stored derived values, no `voided_by` from form.**
10. **`void_transaction` is the single source of truth** for void precondition checks. Routes must not re-implement void rules inline.
11. **Read your task prompt file:** `iterations/p1-i4/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-4` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

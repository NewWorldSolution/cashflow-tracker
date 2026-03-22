# P1-I3 — Transaction Capture: Entry Form, Validation, Recent List
## Task Board

**Status:** ⏳ WAITING
**Last updated:** 2026-03-22 — branch created, iteration ready to start
**Iteration branch:** `feature/phase-1/iteration-3` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-3` → `main` ← QA agent approves before merge

---

## Dependency Map

```
I3-T1 (service layer: validation + calculations)
  ├── I3-T2 (transaction routes)    ──┐
  └── I3-T3 (create template)      ──┴──► I3-T4 (list template + form.js) ──► I3-T5 (tests + close)
```

T2 and T3 run in parallel once T1 is DONE.
T4 must wait for both T2 and T3 to be DONE.
T5 closes the iteration — runs last.

---

## Tasks

| ID    | Title                                      | Owner       | Status     | Depends on   | Branch                              |
|-------|--------------------------------------------|-------------|------------|--------------|-------------------------------------|
| I3-T1 | Service layer (validation + calculations)  | Codex       | ⏳ WAITING | —            | `feature/p1-i3/t1-services`         |
| I3-T2 | Transaction routes                         | Claude Code | ⏳ WAITING | I3-T1        | `feature/p1-i3/t2-routes`           |
| I3-T3 | Create template                            | Codex       | ⏳ WAITING | I3-T1        | `feature/p1-i3/t3-create-template`  |
| I3-T4 | List template + form.js                   | Claude Code | ⏳ WAITING | I3-T2, I3-T3 | `feature/p1-i3/t4-list-and-js`      |
| I3-T5 | Tests + ruff + PR ready                    | Codex       | ⏳ WAITING | I3-T4        | `feature/p1-i3/t5-tests`            |

---

## Prompts & Reviews

| Task  | Implementation prompt                            | Review prompt                             | Reviewer    |
|-------|--------------------------------------------------|-------------------------------------------|-------------|
| I3-T1 | `iterations/p1-i3/prompts/t1-services.md`        | `iterations/p1-i3/reviews/review-t1.md`  | Claude Code |
| I3-T2 | `iterations/p1-i3/prompts/t2-routes.md`          | `iterations/p1-i3/reviews/review-t2.md`  | Codex       |
| I3-T3 | `iterations/p1-i3/prompts/t3-create-template.md` | `iterations/p1-i3/reviews/review-t3.md`  | Claude Code |
| I3-T4 | `iterations/p1-i3/prompts/t4-list-and-js.md`     | `iterations/p1-i3/reviews/review-t4.md`  | Claude Code |
| I3-T5 | `iterations/p1-i3/prompts/t5-tests.md`           | `iterations/p1-i3/reviews/review-t5.md`  | Claude Code |
| —     | —                                                | `iterations/p1-i3/reviews/review-iteration.md` | Claude Code (QA) |

---

## Task Details

### I3-T1 — Service layer: validation + calculations (Codex)

**Goal:** Pure service layer. No routes, no templates. Business logic only.

**Allowed files:**
```
app/services/validation.py
app/services/calculations.py
app/services/__init__.py     ← ensure package marker exists (may already exist)
```

**Functions to implement:**

```python
# app/services/validation.py

validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]
  # Enforces ALL rules from transaction_validator skill.
  # Returns list of error strings. Empty = valid. Never raises.
  # Rules (from prompt.md):
  #  1. date required
  #  2. direction in ('income', 'expense')
  #  3. amount must be positive Decimal
  #  4. category_id must be valid FK in categories table
  #  5. category direction must match transaction direction
  #  6. payment_method in ('cash', 'card', 'transfer')
  #  7. vat_rate in (0, 5, 8, 23)
  #  8. income_type = 'internal' → vat_rate must be 0
  #  9. income_type required when direction = 'income'
  # 10. income_type must be None when direction = 'expense'
  # 11. vat_deductible_pct required when direction = 'expense' (NOT NULL)
  # 12. vat_deductible_pct must be None when direction = 'income'
  # 13. vat_deductible_pct in (0, 50, 100) if present
  # 14. description required (non-empty) when category is 'other_expense' or 'other_income'
  # 15. logged_by must be a valid integer FK in users table

# app/services/calculations.py

vat_amount(gross: Decimal, vat_rate: float) -> Decimal
  # gross * (vat_rate / (100 + vat_rate))
  # Round to 2 decimal places

net_amount(gross: Decimal, vat_rate: float) -> Decimal
  # gross - vat_amount(gross, vat_rate)

vat_reclaimable(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal
  # vat_amount(gross, vat_rate) * (vat_deductible_pct / 100)

effective_cost(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal
  # gross - vat_reclaimable(gross, vat_rate, vat_deductible_pct)
```

**Architecture rules:**
- `validate_transaction` is the ONLY place any validation rule is enforced — routes must not re-implement rules inline
- Parameterised queries only for any DB lookups — never string interpolation
- `calculations.py` contains NO database access — pure math functions only
- No `except: pass`, no silent defaults

**Acceptance check:**
```bash
python -c "from app.services.validation import validate_transaction; from app.services.calculations import vat_amount, net_amount, vat_reclaimable, effective_cost; print('imports ok')"
```

---

### I3-T2 — Transaction routes (Claude Code)

**Goal:** Three route handlers: create form, create POST, transaction list. Plus `/categories` JSON endpoint.

**Depends on:** I3-T1 (validation.py and calculations.py must exist and be importable)

**Allowed files:**
```
app/routes/transactions.py
app/main.py                    ← register transactions router only; no other changes
```

**Routes to implement:**
```
GET  /transactions/new     → render create.html (empty form, categories loaded)
POST /transactions/new     → validate, save on success / re-render with errors on failure
GET  /transactions/        → render list.html (last 20 active transactions)
GET  /categories           → JSON list of all categories with defaults
```

**POST /transactions/new exact sequence:**
```
1. require_auth(request) → user
2. Read form fields (all as Form(default="") or Form(default=None))
3. logged_by = user["id"]  ← from session, never from form input
4. errors = validate_transaction(data, db)
5. if errors: re-render create.html with errors + preserved form_data; return 422
6. if valid: INSERT INTO transactions; redirect to /transactions/ (302)
```

**Acceptance check:**
- Router imports without error
- GET /transactions/new returns 200 for authenticated user

---

### I3-T3 — Create template (Codex)

**Goal:** Full transaction entry form. All fields, inline errors, preserved input, guardrails.

**Depends on:** I3-T1 (knows error message contract and field names)

**Allowed files:**
```
app/templates/transactions/create.html
app/templates/transactions/__init__.py   ← empty if needed (probably not)
```

**Template requirements:**
```
- Extends base.html (inherits SANDBOX banner and nav)
- Form action: POST /transactions/new
- All form fields: date, direction, amount, category_id, payment_method, vat_rate,
  income_type, vat_deductible_pct, description
- Persistent label on amount: "Enter gross amount (VAT included)"
- Card payment reminder element (hidden by default — form.js shows/hides it):
  "Log gross amount. Card commission is logged separately at month end from terminal invoice"
- income_type row: hidden by default (form.js shows when direction=income)
- vat_deductible_pct row: hidden by default (form.js shows when direction=expense)
- description required indicator: "(required)" shown only for other_expense / other_income (via JS)
- Error display: inline list of all errors, above the form, only when errors list is non-empty
- Input values preserved on error (form_data dict passed from route handler)
- Link to /transactions/ (back to list)
- <script src="/static/form.js"> included at bottom
```

**Acceptance check:**
- Template renders without Jinja2 errors when errors=[] and form_data={}
- Template renders with error list when errors=["error 1", "error 2"]
- Amount field has persistent label visible

---

### I3-T4 — List template + form.js (Claude Code)

**Goal:** Transaction list page and client-side form behaviour.

**Depends on:** I3-T2 (routes exist), I3-T3 (create template exists)

**Allowed files:**
```
app/templates/transactions/list.html
static/form.js
```

**list.html requirements:**
```
- Extends base.html
- Shows last 20 active transactions in a table
- Columns: date, category label, direction, amount (gross), payment method, logged by (username)
- Empty state message when no transactions
- Link to /transactions/new ("New transaction")
- No JS required for list page
```

**form.js requirements:**
```
- On load: fetch /categories → build lookup map
- On category change: set vat_rate and vat_deductible_pct from defaults
- On income_type = internal: force vat_rate to 0, disable vat_rate field
- On income_type = external: re-enable vat_rate field
- On direction = income: show income_type row, hide vat_deductible_pct row
- On direction = expense: show vat_deductible_pct row, hide income_type row
- On payment_method = card: show card reminder div
- On payment_method ≠ card: hide card reminder div
- Vanilla JS only — no import, no require, no frameworks
```

**Acceptance check:**
- list.html renders without Jinja2 errors when transactions=[]
- form.js has no syntax errors (check with: node --check static/form.js)

---

### I3-T5 — Tests + ruff + PR ready (Codex)

**Goal:** Full test suite green, ruff clean, iteration closed.

**Depends on:** I3-T4 (all implementation complete)

**Allowed files:**
```
tests/test_validation.py
tests/test_transactions.py
iterations/p1-i3/tasks.md    ← status update only (closure step)
```

**Fixture requirements:**
```python
# Reuse client fixture pattern from test_auth.py:
# - client(tmp_path): opening balance pre-set, authenticated as 'owner'
# - Use same db_path attribute pattern: c.db_path = db_path

# fresh_client from test_auth.py pattern (opening balance set, NOT authenticated):
# - For test_unauthenticated_create_redirects
```

**Tests to implement:**

See "Tests Required" section in prompt.md for the full list of 18 validation tests and 12 route tests.

**Closure steps:**
1. `pytest` — all tests pass (25 P1-I2 + new P1-I3 tests), exit code 0
2. `ruff check .` — clean, exit code 0
3. `git diff --name-only feature/phase-1/iteration-3` — only allowed files
4. `gh pr ready feature/phase-1/iteration-3`
5. Update this file: Status → ✔ COMPLETE, Last updated → today

---

## Agent Rules

1. **Read this file first.** Find your task. Confirm status is WAITING before starting.
2. **Update status to IN PROGRESS** before writing a line of code.
3. **Check dependencies.** Never start if any dep is not ✅ DONE.
4. **Worktree:** check out `feature/phase-1/iteration-3` first, then create your task branch from it.
5. **PR targets the iteration branch**, not `main`. One task per PR.
6. **After completing:** set status to ✅ DONE. Add one-line note: what you produced.
7. **Never touch another agent's task.** Add notes under your own task only.
8. **If blocked:** set status to 🚫 BLOCKED with reason. Stop and wait.
9. **No `except: pass`, no stored derived values, no free-text categories, no logged_by from form.**
10. **validation.py is the single source of truth** for all transaction validation. Routes and templates must not re-implement any rule inline.
11. Read your task prompt: `iterations/p1-i3/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency or bootstrap |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-3` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

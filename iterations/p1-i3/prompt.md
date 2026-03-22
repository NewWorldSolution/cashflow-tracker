# cashflow-tracker Task Prompt — P1-I3: Transaction Capture

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/validation.py → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores the actual gross cash; VAT is extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or any reporting layer |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly; block the save, never default silently |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost` are computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point; route handlers and templates call it, never re-implement it |

---

## Repository State

- **Iteration branch:** `feature/phase-1/iteration-3`
- **Base branch:** `main` (P1-I2 merged 2026-03-22)
- **Tests passing:** 25 (11 P1-I1 + 14 P1-I2)
- **Ruff:** clean
- **Last completed iteration:** P1-I2 — Authentication (login/logout, session protection, AuthGate)
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I3 |
| Title | Transaction Capture — Entry Form, Validation, Recent List |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 3 — Transaction Capture |
| Feature branch | `feature/phase-1/iteration-3` |
| Depends on | P1-I2 (authenticated session, `require_auth`, `request.state.user`) |
| Blocks | P1-I4 (Corrections, Hardening & Acceptance) |
| PR scope | Task branches PR into `feature/phase-1/iteration-3`. The iteration branch PRs into `main` as one final PR. Do not combine iterations. Do not push partial work. |

---

## Task Goal

This iteration adds the transaction entry form, all server-side validation rules, VAT-derived calculations (for display only — never stored), and a recent transaction list. After P1-I3, authenticated users can log income and expense transactions with all VAT rules enforced, see category-triggered auto-defaults, and review the last 20 active transactions.

**Execution model:** This iteration uses 5 task branches executed by multiple agents per tasks.md. If you are an individual agent, read your task prompt file (`iterations/p1-i3/prompts/t[N]-[name].md`) — it contains the precise scope and acceptance criteria for your task. This file is the full reference; task prompt files are the execution guides.

---

## Files to Read Before Starting

### Mandatory — read these for every task, in this order

```
CLAUDE.md                                              ← constitution — read first, always
project.md                                             ← current state and what this iteration delivers
skills/cash-flow/schema/SKILL.md                       ← full table structure — transactions schema
skills/cash-flow/transaction_validator/SKILL.md        ← every validation rule — single source of truth
skills/cash-flow/form_logic/SKILL.md                   ← field visibility, auto-defaults, guardrails
skills/cash-flow/error_handling/SKILL.md               ← inline errors, preserve form input, all errors shown
skills/cash-flow/deterministic_logic/SKILL.md          ← no LLM anywhere in this iteration
```

### Task-specific

```
docs/concept.md                                        ← full category list (4 income, 18 expense) with VAT defaults
docs/architecture.md                                   ← VAT formulas (canonical source — use exactly as written)
```

---

## What P1-I2 Established (Contracts This Iteration Must Respect)

```python
# Authentication — already wired, do not modify
# AuthGate middleware: all routes except /settings/opening-balance, /auth/login, /auth/logout
#   are protected. Auth is guaranteed for any non-exempt route.
# /categories, /transactions/new, /transactions/ are all protected by AuthGate — no special
# handling needed in route handlers; middleware guarantees it.

# Available in app/services/auth_service.py — use as-is:
from app.services.auth_service import require_auth

# Usage in P1-I3 routes:
@router.get("/transactions/new")
async def new_transaction(request: Request, db=Depends(get_db)):
    user = require_auth(request)   # reads request.state.user set by AuthGate
    # user["id"] is available for logged_by field

# Available in app/main.py — use as-is, do not reimport or redefine:
def get_db() -> sqlite3.Connection: ...   # returns a live db connection

# Session contract (established P1-I1, unchanged):
# session['user_id'] = users.id (integer)
```

---

## Existing Code This Task Builds On

```
app/main.py              ← register transactions router here; do not modify middleware or AuthGate
app/templates/base.html  ← already has SANDBOX banner, nav, logout — do not modify
```

Do not rewrite files that already exist. Make only the changes specified for this iteration.

---

## What to Build

### New files

```
app/services/validation.py
  ← validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]
  ← This is the ONLY enforcement point for ALL transaction rules.
  ← Route handlers call this function; they do not re-implement any rule inline.
  ← db is the live connection passed from the route handler — do not open a new connection inside.

app/services/calculations.py
  ← vat_amount(gross: Decimal, vat_rate: float) -> Decimal
  ← net_amount(gross: Decimal, vat_rate: float) -> Decimal
  ← vat_reclaimable(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal
  ← effective_cost(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal
  ← All return Decimal. None of these values are ever stored in the database.
  ← Used only by the list route (to show derived columns in the transaction list).

app/routes/transactions.py
  ← GET  /transactions/new     — render create form (empty form, categories loaded)
  ← POST /transactions/new     — validate, save, redirect to /transactions/ on success
  ← GET  /transactions/        — render list of last 20 active transactions with derived columns
  ← GET  /categories           — JSON: list of all categories (used by form.js)

app/templates/transactions/create.html
  ← extends base.html
  ← full transaction entry form (all fields per spec below)
  ← inline error display, all errors shown together, form input preserved on error
  ← gross amount label persistent: "Enter gross amount (VAT included)"
  ← card payment reminder element (hidden by default — form.js manages visibility)
  ← income_type row hidden by default (form.js shows when direction=income)
  ← vat_deductible_pct row hidden by default (form.js shows when direction=expense)
  ← description required indicator hidden by default (form.js shows for other_expense/other_income)

app/templates/transactions/list.html
  ← extends base.html
  ← shows last 20 active transactions
  ← includes derived columns (vat_amount, effective_cost)
  ← link to /transactions/new

static/form.js
  ← category auto-defaults, field locking, field visibility, card reminder
  ← vanilla JS only — no frameworks, no build step

tests/test_validation.py
  ← validation rule tests (see "Tests Required" section)

tests/test_transactions.py
  ← route-level tests (see "Tests Required" section)
```

### Modified files

```
app/main.py
  ← register transactions router only
  ← no other changes

app/services/__init__.py
  ← ensure package marker exists (already exists from P1-I2 — check before creating)
```

### Files that must NOT be modified

```
db/schema.sql                    ← frozen after P1-I1
db/init_db.py                    ← frozen after P1-I1
seed/categories.sql              ← frozen after P1-I1
seed/users.sql                   ← frozen after P1-I1
app/routes/auth.py               ← P1-I2 deliverable — do not touch
app/routes/dashboard.py          ← P1-I2 deliverable — do not touch
app/routes/settings.py           ← P1-I1 deliverable — do not touch
app/services/auth_service.py     ← P1-I2 deliverable — do not touch
app/templates/base.html          ← P1-I2 deliverable — do not touch
app/templates/auth/login.html    ← P1-I2 deliverable — do not touch
app/templates/dashboard.html     ← P1-I2 deliverable — do not touch
tests/test_auth.py               ← P1-I2 deliverable — do not touch
tests/test_init_db.py            ← P1-I1 deliverable — do not touch
```

---

## Transaction Form — Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `date` | date (YYYY-MM-DD) | today | Required |
| `direction` | radio: income / expense | — | Required |
| `amount` | decimal | — | Required. Always gross. Persistent label: "Enter gross amount (VAT included)" |
| `category_id` | dropdown (from categories table) | — | Required. Integer FK only. |
| `payment_method` | select: cash / card / transfer | — | Required. Card triggers reminder. |
| `vat_rate` | select: 0 / 5 / 8 / 23 | auto-filled from category | Required. Forced to 0 when income_type=internal. Override of category default is allowed for all other cases. |
| `income_type` | select: internal / external | — | Shown only for income rows. Required for income. |
| `vat_deductible_pct` | select: 0 / 50 / 100 | auto-filled from category | Shown only for expense rows. Required for expense. Override of category default is allowed. |
| `description` | textarea | — | Optional (required indicator shown for other_expense / other_income). |

---

## Data Normalisation (applied before validation)

Before calling `validate_transaction`, the route handler must normalise raw form data:

```python
# 1. Strip whitespace from all string fields
# 2. Convert empty strings to None for optional fields:
#    income_type, vat_deductible_pct, description → None if empty string
# 3. Convert numeric fields:
#    amount: Decimal(str(raw_amount))   ← NEVER Decimal(float(...))
#    vat_rate: float(raw_vat_rate)
#    vat_deductible_pct: float(raw) if not None
#    category_id: int(raw_category_id)
# 4. logged_by = user["id"]  ← from session, never from form input
# 5. is_active = True         ← default, not a form field
# 6. date: accept as string (YYYY-MM-DD) — validate format in validate_transaction
```

---

## Validation Rules — All Mandatory (enforced in validation.py only)

```python
# validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]
# Returns a list of human-readable error strings. Empty list = valid.
# Never raises — catches conversion errors and adds them to the error list.
# db is the live connection passed from the caller — do not open a new connection inside.

# Rules (all must be checked; collect ALL errors before returning):
# 1.  date required; must be parseable as YYYY-MM-DD
# 2.  direction must be 'income' or 'expense'
# 3.  amount must be positive Decimal (> 0); reject zero, negative, non-numeric
# 4.  category_id must be an integer present in categories table — free-text rejected
#     Use: SELECT category_id, direction, name FROM categories WHERE category_id = ?
# 5.  Category direction must match transaction direction
#     e.g. income transaction cannot use an expense-only category
# 6.  payment_method must be 'cash', 'card', or 'transfer'
# 7.  vat_rate must be in (0, 5, 8, 23) — no other values accepted
# 8.  income_type = 'internal' → vat_rate MUST be 0 (hard rule — reject any other value)
# 9.  income_type required when direction = 'income' (None is not permitted)
# 10. income_type must be None when direction = 'expense'
# 11. vat_deductible_pct required when direction = 'expense' (None not permitted)
# 12. vat_deductible_pct must be None when direction = 'income'
# 13. vat_deductible_pct must be in (0, 50, 100) if present
# 14. description required (non-empty string) when category name is 'other_expense' or 'other_income'
# 15. logged_by must be an integer present in users table (SELECT id FROM users WHERE id = ?)

# Important: category VAT default is a SUGGESTION, not a constraint.
# A user may select a category with default_vat_rate=23 and submit vat_rate=5 — this is valid.
# The only VAT override restriction is rule 8 (internal income → must be 0).
```

---

## VAT Calculations — Canonical Formulas (from docs/architecture.md)

These are the exact formulas to implement in `calculations.py`. Do not use shorthands.

```python
from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal('0.01')

def vat_amount(gross: Decimal, vat_rate: float) -> Decimal:
    # gross - (gross / (1 + vat_rate/100))
    rate = Decimal(str(vat_rate))
    result = gross - (gross / (1 + rate / 100))
    return result.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def net_amount(gross: Decimal, vat_rate: float) -> Decimal:
    # gross - vat_amount
    return (gross - vat_amount(gross, vat_rate)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def vat_reclaimable(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal:
    # vat_amount * vat_deductible_pct / 100
    va = vat_amount(gross, vat_rate)
    result = va * Decimal(str(vat_deductible_pct)) / 100
    return result.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

def effective_cost(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal:
    # net_amount + (vat_amount * (1 - vat_deductible_pct / 100))
    # Canonical formula from architecture.md — not a shorthand
    va = vat_amount(gross, vat_rate)
    na = net_amount(gross, vat_rate)
    pct = Decimal(str(vat_deductible_pct))
    result = na + (va * (1 - pct / 100))
    return result.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
```

**Rules:**
- All intermediate calculations use `Decimal` — never `float`
- Input conversion: `Decimal(str(float_or_string))` — never `Decimal(float(...))`
- All results rounded to 2 decimal places with `ROUND_HALF_UP`
- These functions are pure — no DB access, no side effects

---

## Route Logic — Exact Behaviour

### GET /transactions/new

```
→ require_auth(request) — get user from request.state.user
→ fetch all categories from db ordered by direction, label
→ render create.html with:
    - categories list
    - defaults: date=today (date.today().isoformat()), all other fields empty
    - errors=[] (no errors on fresh load)
    - form_data={} (no preserved values)
```

### POST /transactions/new

```
→ require_auth(request) — get user from request.state.user
→ read all form fields using Form(default="") or Form(default=None)
→ normalise: strip strings, empty string → None for optional fields, cast numeric types
→ set data["logged_by"] = user["id"]  ← from session, NEVER from form input
→ set data["is_active"] = True
→ errors = validate_transaction(data, db)
→ if errors:
    re-fetch categories (needed to re-render dropdown)
    re-render create.html with:
    - categories list
    - errors list (ALL errors shown at once — not one at a time)
    - form_data = normalised submitted values (preserved so user sees what they typed)
    return status_code=422
→ if valid:
    INSERT INTO transactions (
        date, amount, direction, category_id, payment_method,
        vat_rate, income_type, vat_deductible_pct, description, logged_by
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    # is_active defaults to TRUE in schema; created_at defaults to CURRENT_TIMESTAMP
    redirect to /transactions/  ← 302
```

### GET /transactions/

```
→ require_auth(request) — get user from request.state.user
→ SELECT last 20 active transactions:
    SELECT t.*, c.label AS category_label, u.username AS logged_by_username
    FROM transactions t
    JOIN categories c ON t.category_id = c.category_id
    JOIN users u ON t.logged_by = u.id
    WHERE t.is_active = TRUE
    ORDER BY t.created_at DESC
    LIMIT 20
→ for each row, compute derived fields using calculations.py:
    vat_amt = vat_amount(Decimal(str(row["amount"])), row["vat_rate"])
    eff_cost = effective_cost(...) for expense rows (income rows: not applicable / show dash)
→ pass transactions + derived fields to list.html
```

### GET /categories

```
→ SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct
    FROM categories
    ORDER BY direction, label
→ return JSONResponse([
    {
        "category_id": <int>,
        "name": <str>,           ← internal code e.g. "petrol"
        "label": <str>,          ← display name e.g. "Paliwo"
        "direction": <str>,      ← "income" or "expense"
        "default_vat_rate": <float>,
        "default_vat_deductible_pct": <float | null>
    },
    ...
  ])
→ AuthGate protects this route — no special auth handling in the route handler
```

---

## Form.js — Required Behaviour

```javascript
// On DOMContentLoaded:
// 1. Fetch /categories → build lookup map: { category_id: {default_vat_rate, default_vat_deductible_pct, direction, name} }
//    (response structure guaranteed by /categories route — see exact field names above)

// On category change:
// 2. Set vat_rate select to category default_vat_rate
// 3. If direction=expense: set vat_deductible_pct select to category default_vat_deductible_pct
// 4. If category.default_vat_deductible_pct is null → do not change vat_deductible_pct

// On income_type change:
// 5. If income_type = "internal" → set vat_rate to "0", disable vat_rate field
// 6. If income_type = "external" → re-enable vat_rate field (user may override)
// 7. Clear the lock if user changes income_type back to "external"

// On direction change:
// 8. Show income_type row (id="income-type-row") only when direction = "income"
// 9. Show vat_deductible_pct row (id="vat-deductible-row") only when direction = "expense"
// 10. On switch: clear income_type and vat_deductible_pct values; re-enable vat_rate if locked

// On payment_method change:
// 11. Show card reminder (id="card-reminder") when payment_method = "card"
// 12. Hide card reminder otherwise

// On category change (secondary):
// 13. Show description required indicator (id="desc-required") when category name is
//     "other_expense" or "other_income"
// 14. Hide otherwise
```

---

## Tests Required

### tests/test_validation.py — validation rule coverage

Each test calls `validate_transaction(data, db)` directly. Uses an in-memory SQLite db seeded with categories and users.

```python
def test_valid_income_transaction_accepted()          # returns []
def test_valid_expense_transaction_accepted()         # returns []
def test_internal_income_vat_zero_accepted()          # income_type=internal, vat_rate=0 → accepted
def test_internal_income_nonzero_vat_rejected()       # income_type=internal, vat_rate=23 → error
def test_expense_vat_rate_override_accepted()         # category default 23%, user sets 5% → accepted
def test_expense_without_vat_deductible_pct_rejected()
def test_income_with_vat_deductible_pct_rejected()
def test_income_without_income_type_rejected()        # income_type=None on income row → error
def test_expense_with_income_type_rejected()          # income_type set on expense row → error
def test_other_expense_without_description_rejected()
def test_other_income_without_description_rejected()
def test_other_expense_with_description_accepted()
def test_invalid_category_id_rejected()              # category_id not in table
def test_direction_category_mismatch_rejected()      # income transaction with expense category
def test_direction_category_match_accepted()         # income transaction with income category → []
def test_invalid_vat_rate_rejected()                 # vat_rate=7
def test_invalid_payment_method_rejected()           # payment_method='cheque'
def test_invalid_vat_deductible_pct_rejected()       # vat_deductible_pct=75
def test_zero_amount_rejected()
def test_negative_amount_rejected()
def test_invalid_date_format_rejected()              # date='not-a-date'
def test_multiple_errors_returned_together()         # two invalid fields → both errors in list
```

### tests/test_transactions.py — route-level coverage

```python
def test_create_form_loads(client)
    # GET /transactions/new → 200

def test_create_transaction_success_redirects(client)
    # POST /transactions/new with valid data → 302 redirect to /transactions/

def test_create_transaction_saves_to_db(client)
    # After POST, query db — transaction row exists with all correct values

def test_logged_by_set_from_session_not_form(client)
    # POST with a forged logged_by in form data → saved row uses session user id

def test_create_transaction_shows_all_errors(client)
    # POST with two invalid fields → 422, both errors present in response text

def test_form_input_preserved_on_error(client)
    # POST with description="test note" and one invalid field → "test note" present in response

def test_internal_income_vat_rate_enforced(client)
    # POST with income_type=internal and vat_rate=23 → 422

def test_other_expense_description_required(client)
    # POST other_expense without description → 422

def test_transaction_list_loads(client)
    # GET /transactions/ → 200

def test_transaction_list_shows_recent(client)
    # Create transaction, then GET /transactions/ → row visible in response

def test_transaction_list_excludes_inactive(client)
    # Insert inactive transaction directly in db → not visible in GET /transactions/

def test_transaction_list_ordered_by_created_at(client)
    # Insert two transactions → list shows them in created_at DESC order

def test_categories_endpoint_returns_json(client)
    # GET /categories → 200, JSON array, each item has category_id/name/label/direction/default_vat_rate

def test_unauthenticated_create_redirects(logged_out_client)
    # GET /transactions/new without session → redirect to /auth/login
    # (logged_out_client: opening balance set, NOT authenticated — separate fixture)
```

---

## What NOT to Do

- Do not modify `db/schema.sql` — schema is frozen after P1-I1
- Do not add columns to the transactions table
- Do not store `vat_amount`, `net_amount`, `vat_reclaimable`, or `effective_cost` in the database
- Do not implement void/correct flow — that is P1-I4
- Do not implement monthly summary or reporting — that is Phase 2
- Do not use `except: pass` or any silent exception swallowing
- Do not implement any LLM extraction or suggestions
- Do not add JavaScript frameworks — vanilla JS only
- Do not accept `category_id` as a free-text string
- Do not set `logged_by` from form input — always from session
- Do not open new database connections inside `validate_transaction` — use the passed `db`
- Do not use `float` arithmetic for monetary calculations — use `Decimal` throughout
- Do not add `/categories` to EXEMPT_PATHS — AuthGate already protects it correctly
- Do not modify frozen P1-I1 / P1-I2 files

---

## Handoff: What P1-I4 Needs From This Iteration

```python
# Transaction create and list are functional.
# validate_transaction() is the single enforcement point — P1-I4 uses it too.

# P1-I4 will add:
# - GET  /transactions/<id>         — detail view
# - POST /transactions/<id>/void    — soft-delete with void_reason
# - POST /transactions/<id>/correct — void + pre-fill create form

# P1-I4 must import and use validate_transaction from this iteration.
# P1-I4 must not re-implement any validation rules.
```

---

## Execution Workflow (single-agent path)

This workflow applies if a single agent is executing the full iteration. For multi-agent execution, see `iterations/p1-i3/tasks.md` — each task uses its own branch and PR.

### Step 0 — Branch setup (single agent only)

```bash
git checkout main
git pull origin main
git checkout -b feature/phase-1/iteration-3
git push -u origin feature/phase-1/iteration-3

gh pr create \
  --base main \
  --head feature/phase-1/iteration-3 \
  --title "P1-I3: Transaction Capture — Entry Form, Validation, Recent List" \
  --body "Work in progress. See iterations/p1-i3/prompt.md for full task spec." \
  --draft
```

### Step 1 — Verify baseline

```bash
pytest
# Expected: 25 tests pass (P1-I2 baseline), exit code 0

ruff check .
# Expected: clean, exit code 0
```

### Step 2 — Implement in order

1. `app/services/validation.py`
2. `app/services/calculations.py`
3. `app/routes/transactions.py`
4. `app/templates/transactions/create.html`
5. `app/templates/transactions/list.html`
6. `static/form.js`
7. `tests/test_validation.py` + `tests/test_transactions.py`

### Step 3 — Test and lint

```bash
pytest
# Must pass: all 25 P1-I2 tests + all new P1-I3 tests. Zero failures.

ruff check .
# Must be clean.
```

### Step 4 — Verify scope

```bash
git diff --name-only main
```

Every file in the output must be in the allowed list.

---

## Definition of Done

This iteration is complete when ALL of the following are true:

- [ ] GET `/transactions/new` renders form with all required fields for authenticated users
- [ ] POST `/transactions/new` with valid data saves transaction and redirects to list
- [ ] POST `/transactions/new` with invalid data re-renders with ALL errors shown, input preserved, 422
- [ ] `logged_by` is always `users.id` from session — never from form input, never null
- [ ] `income_type = internal` with any `vat_rate ≠ 0` is rejected server-side
- [ ] Expense row without `vat_deductible_pct` is rejected server-side
- [ ] `other_expense` / `other_income` without description is rejected server-side
- [ ] VAT rate override of category default is accepted (only internal rule restricts it)
- [ ] Category auto-defaults fire on category change (form.js + `/categories` endpoint)
- [ ] Card payment reminder shown/hidden by form.js
- [ ] Gross amount label "Enter gross amount (VAT included)" persistent at all times
- [ ] GET `/transactions/` shows last 20 active transactions, `created_at DESC`, with derived columns
- [ ] Inactive transactions not shown in list
- [ ] Derived values (vat_amount, effective_cost) displayed but never stored in DB
- [ ] All test_validation.py tests pass (22 tests)
- [ ] All test_transactions.py tests pass (14 tests)
- [ ] 25 P1-I2 regression tests still pass
- [ ] Ruff clean
- [ ] Only allowed files modified
- [ ] No LLM calls anywhere
- [ ] No `Decimal(float(...))` — all monetary Decimal conversions via `Decimal(str(...))`

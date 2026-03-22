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
docs/architecture.md                                   ← VAT formulas (vat_amount, net_amount, vat_reclaimable, effective_cost)
```

---

## What P1-I2 Established (Contracts This Iteration Must Respect)

```python
# Authentication — already wired, do not modify
# AuthGate middleware: all routes except /settings/opening-balance, /auth/login, /auth/logout
#   are protected. Auth is guaranteed for any route not in EXEMPT_PATHS.

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
app/main.py              ← register transactions router here; do not modify middleware
app/templates/base.html  ← already has SANDBOX banner, nav, logout — do not modify
```

Do not rewrite files that already exist. Make only the changes specified for this iteration.

---

## What to Build

### New files

```
app/services/validation.py
  ← validate_transaction(data: dict, db) → list[str]  (returns list of error strings, empty = valid)
  ← This is the single enforcement point for ALL transaction rules.
  ← Route handlers call this function; they do not re-implement any rule inline.

app/services/calculations.py
  ← vat_amount(gross: Decimal, vat_rate: float) → Decimal
  ← net_amount(gross: Decimal, vat_rate: float) → Decimal
  ← vat_reclaimable(gross: Decimal, vat_rate: float, vat_deductible_pct: float) → Decimal
  ← effective_cost(gross: Decimal, vat_rate: float, vat_deductible_pct: float) → Decimal
  ← All return Decimal. None of these values are ever stored in the database.
  ← For P1-I3: used for form preview display only (passed to template context).

app/routes/transactions.py
  ← GET  /transactions/new     — render create form (empty, or re-render with errors + preserved input)
  ← POST /transactions/new     — validate, save, redirect to /transactions/ on success
  ← GET  /transactions/        — render list of last 20 active transactions
  ← GET  /categories           — JSON: list of all categories with defaults (used by form.js auto-defaults)

app/templates/transactions/create.html
  ← extends base.html
  ← full transaction entry form (all fields per spec)
  ← inline error display, all errors shown together, form input preserved on error
  ← gross amount label persistent: "Enter gross amount (VAT included)"
  ← card payment reminder shown/hidden via JS (form.js)
  ← income_type field shown only for income rows (via JS)
  ← vat_deductible_pct shown only for expense rows (via JS)
  ← description required indicator shown when category is other_expense or other_income (via JS)

app/templates/transactions/list.html
  ← extends base.html
  ← shows last 20 active transactions (WHERE is_active = TRUE ORDER BY created_at DESC)
  ← columns: date, category label, direction, amount (gross), payment method, logged by (username)
  ← link to /transactions/new

static/form.js
  ← category auto-defaults: on category change, fetch /categories and set vat_rate and vat_deductible_pct
  ← field locking: income_type = internal → vat_rate forced to 0 and field greyed out
  ← field visibility: income_type shown only when direction = income
  ← field visibility: vat_deductible_pct shown only when direction = expense
  ← card reminder: shown/hidden based on payment_method = card
  ← vanilla JS only — no frameworks, no build step

tests/test_validation.py
  ← all validation rule tests listed in "Tests Required" section below

tests/test_transactions.py
  ← route-level tests listed in "Tests Required" section below
```

### Modified files

```
app/main.py
  ← register transactions router only
  ← no other changes

app/services/__init__.py
  ← ensure package marker exists (may already exist from P1-I2)
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
| `date` | date | today | Required |
| `direction` | radio: income / expense | — | Required |
| `amount` | decimal | — | Required. Always gross. Persistent label: "Enter gross amount (VAT included)" |
| `category_id` | dropdown (from categories table) | — | Required. Integer FK only. |
| `payment_method` | select: cash / card / transfer | — | Required. Card triggers reminder. |
| `vat_rate` | select: 0 / 5 / 8 / 23 | auto-filled from category | Required. Forced to 0 when income_type=internal. |
| `income_type` | select: internal / external | — | Shown only for income rows. Required for income. |
| `vat_deductible_pct` | select: 0 / 50 / 100 | auto-filled from category | Shown only for expense rows. Required for expense. |
| `description` | textarea | — | Optional (required indicator shown for other_expense / other_income). |

---

## Validation Rules — All Mandatory (enforced in validation.py only)

```python
# validate_transaction(data: dict, db) → list[str]
# Returns a list of error strings. Empty list = valid. Never raises — always returns.

# Rules:
# 1. date is required
# 2. direction must be 'income' or 'expense'
# 3. amount must be positive Decimal — reject zero, negative, non-numeric
# 4. category_id must be an integer present in categories table — free-text rejected
# 5. category direction must match transaction direction — can't post income amount to expense category
# 6. payment_method must be 'cash', 'card', or 'transfer'
# 7. vat_rate must be in (0, 5, 8, 23) — no other values accepted
# 8. income_type = 'internal' → vat_rate MUST be 0 — reject any other value
# 9. income_type required when direction = 'income' — NULL rejected
# 10. income_type must be None when direction = 'expense' — cannot be set on expense rows
# 11. vat_deductible_pct required when direction = 'expense' — NULL rejected
# 12. vat_deductible_pct must be None when direction = 'income' — cannot be set on income rows
# 13. vat_deductible_pct must be in (0, 50, 100) if present
# 14. description required (non-empty string) when category is 'other_expense' or 'other_income'
# 15. logged_by must be a valid integer present in users table — never a name string
#     (set from session by route handler — never from form input)
```

---

## VAT Calculations — Display Only, Never Stored

```python
# From docs/architecture.md — exact formulas:
# vat_amount      = gross * (vat_rate / (100 + vat_rate))
# net_amount      = gross - vat_amount
# vat_reclaimable = vat_amount * (vat_deductible_pct / 100)
# effective_cost  = gross - vat_reclaimable

# For P1-I3: compute these in the route handler after successful save and pass to list template
# for display. Also compute as preview in the create form response on GET (with sample values).
# NEVER store these in the database. They are always re-derived at query time.
```

---

## Route Logic — Exact Behaviour

### GET /transactions/new

```
→ require_auth(request) — get user from request.state.user
→ fetch all categories from db (for dropdown)
→ render create.html with:
    - categories list
    - defaults: date=today, all other fields empty
    - errors=[] (no errors on fresh load)
    - form_data={} (no preserved values)
```

### POST /transactions/new

```
→ require_auth(request) — get user from request.state.user
→ read all form fields
→ set logged_by = user["id"]  ← from session, never from form input
→ validate_transaction(data, db) → errors
→ if errors:
    re-render create.html with:
    - categories list
    - errors list (all shown together — not one at a time)
    - form_data = submitted values (preserved so user sees what they typed)
    return 422
→ if valid:
    INSERT INTO transactions (...) VALUES (...)
    redirect to /transactions/  ← 302 redirect to list page
```

### GET /transactions/

```
→ require_auth(request) — get user from request.state.user
→ SELECT last 20 active transactions joined with categories and users:
    SELECT t.*, c.label AS category_label, u.username AS logged_by_username
    FROM transactions t
    JOIN categories c ON t.category_id = c.category_id
    JOIN users u ON t.logged_by = u.id
    WHERE t.is_active = TRUE
    ORDER BY t.created_at DESC
    LIMIT 20
→ compute derived fields for display (vat_amount, net_amount, vat_reclaimable, effective_cost)
→ render list.html with transactions
```

### GET /categories

```
→ SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct
    FROM categories
    ORDER BY direction, label
→ return JSONResponse
→ Used by form.js to populate auto-defaults on category selection
→ No auth required (category data is not sensitive — but AuthGate already protects all non-exempt routes)
```

---

## Form.js — Required Behaviour

```javascript
// On DOMContentLoaded:
// 1. Fetch /categories and build a lookup map: { category_id: {default_vat_rate, default_vat_deductible_pct, direction, name} }

// On category change:
// 2. Set vat_rate select to category default_vat_rate
// 3. Set vat_deductible_pct select to category default_vat_deductible_pct
// 4. If direction=expense and category default_vat_deductible_pct is null → do not set (leave as-is)

// On income_type change:
// 5. If income_type = internal → set vat_rate to 0, disable vat_rate field, add visual cue (greyed out)
// 6. If income_type = external → re-enable vat_rate field, remove visual cue

// On direction change:
// 7. Show income_type row only when direction = income
// 8. Show vat_deductible_pct row only when direction = expense
// 9. If switching direction → clear income_type / vat_deductible_pct values

// On payment_method change:
// 10. Show card reminder when payment_method = card
// 11. Hide card reminder otherwise

// On category change (secondary check):
// 12. If category is other_expense or other_income → show "(required)" indicator next to description
// 13. Otherwise hide required indicator
```

---

## Tests Required

### tests/test_validation.py — validation rule coverage

```python
# Each test calls validate_transaction(data, db) directly with an in-memory db.

def test_valid_income_transaction_accepted()
def test_valid_expense_transaction_accepted()
def test_internal_income_vat_rate_zero_accepted()
def test_internal_income_nonzero_vat_rate_rejected()
def test_expense_without_vat_deductible_pct_rejected()
def test_income_with_vat_deductible_pct_rejected()
def test_expense_without_income_type_accepted()      # income_type should be None on expense
def test_income_without_income_type_rejected()       # income_type is required on income
def test_other_expense_without_description_rejected()
def test_other_income_without_description_rejected()
def test_other_expense_with_description_accepted()
def test_invalid_category_id_rejected()             # non-existent FK
def test_invalid_vat_rate_rejected()                # e.g. vat_rate=7
def test_invalid_payment_method_rejected()          # e.g. payment_method='cheque'
def test_invalid_vat_deductible_pct_rejected()      # e.g. vat_deductible_pct=75
def test_zero_amount_rejected()
def test_negative_amount_rejected()
def test_direction_category_mismatch_rejected()     # income direction + expense category
```

### tests/test_transactions.py — route-level coverage

```python
# Uses same client fixture as test_auth.py (opening balance pre-set, authenticated session).

def test_create_form_loads(client)
    # GET /transactions/new → 200

def test_create_transaction_success(client)
    # POST /transactions/new with valid data → 302 redirect to /transactions/

def test_create_transaction_saves_to_db(client)
    # After POST, query db — transaction row exists with correct values

def test_logged_by_set_from_session_not_form(client)
    # logged_by in db matches session user id — not any value submitted in form

def test_create_transaction_validation_error(client)
    # POST with invalid data → 422, errors shown in response, form re-rendered with input preserved

def test_internal_income_vat_rate_enforced(client)
    # POST with income_type=internal and vat_rate=23 → 422, rejected

def test_other_expense_description_required(client)
    # POST other_expense without description → 422, rejected

def test_transaction_list_loads(client)
    # GET /transactions/ → 200

def test_transaction_list_shows_recent(client)
    # Create transaction, then GET /transactions/ → transaction visible in response

def test_transaction_list_excludes_inactive(client)
    # Mark transaction inactive, GET /transactions/ → not visible

def test_categories_endpoint_returns_json(client)
    # GET /categories → 200, JSON with category list

def test_unauthenticated_create_redirects(fresh_client)
    # GET /transactions/new without session → redirect to /auth/login
    # (fresh_client has opening balance set but no authenticated session)
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
- Do not modify frozen P1-I1 / P1-I2 files

---

## Handoff: What P1-I4 Needs From This Iteration

```python
# Transaction service available:
# Transactions are stored and queryable.
# validate_transaction() is the single enforcement point.

# P1-I4 will add:
# - GET  /transactions/<id>         — detail view
# - POST /transactions/<id>/void    — soft-delete with void_reason
# - POST /transactions/<id>/correct — void + pre-fill create form

# P1-I4 must use the same validate_transaction() from this iteration.
# P1-I4 must not re-implement any validation rules.
```

---

## Execution Workflow

Follow this sequence exactly. Do not skip or reorder steps.

### Step 0 — Branch setup

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

If either fails: stop. Do not proceed until baseline is clean.

### Step 2 — Read before writing

Read all files listed in "Files to Read Before Starting" in order. Do not write a line of implementation until you understand the validation rules and VAT formulas.

### Step 3 — Plan before multi-file changes

This task touches more than 2 files. Present the full implementation plan (which files, what changes, in what order) before writing any code. Wait for confirmation.

### Step 4 — Implement

Build in this order:
1. `app/services/validation.py` — all validation rules first, no routes yet
2. `app/services/calculations.py` — VAT formulas
3. `app/routes/transactions.py` — routes after services are complete
4. `app/templates/transactions/create.html` — create form
5. `app/templates/transactions/list.html` — list template
6. `static/form.js` — client-side behaviour last
7. `tests/test_validation.py` + `tests/test_transactions.py` — tests last

### Step 5 — Test and lint

```bash
pytest
# Must pass: all 25 P1-I2 tests + all new P1-I3 tests. Zero failures.

ruff check .
# Must be clean. Fix all issues before committing.
```

Do not submit if either command fails.

### Step 6 — Verify scope

```bash
git diff --name-only main
```

Every file in the output must appear in the allowed files list. Revert any unexpected file before committing.

### Step 7 — Commit and mark PR ready

```bash
git add <specific files — do not use git add -A>
git commit -m "feat: transaction capture form with validation, VAT logic, and recent list (P1-I3)"

gh pr ready feature/phase-1/iteration-3
```

---

## Definition of Done

This iteration is complete when ALL of the following are true:

- [ ] GET `/transactions/new` renders form with all required fields for authenticated users
- [ ] POST `/transactions/new` with valid data saves transaction and redirects to list
- [ ] POST `/transactions/new` with invalid data re-renders form with all errors shown, input preserved
- [ ] `logged_by` is always `users.id` from session — never from form input, never null
- [ ] `income_type = internal` with any `vat_rate ≠ 0` is rejected server-side
- [ ] Expense row without `vat_deductible_pct` is rejected server-side
- [ ] `other_expense` / `other_income` without description is rejected server-side
- [ ] Category auto-defaults fire on category change (form.js + `/categories` endpoint)
- [ ] Card payment reminder shown/hidden by form.js
- [ ] Gross amount label "Enter gross amount (VAT included)" persistent at all times
- [ ] GET `/transactions/` shows last 20 active transactions, correct columns, `created_at DESC`
- [ ] Inactive transactions (`is_active = FALSE`) not shown in list
- [ ] All test_validation.py tests pass
- [ ] All test_transactions.py tests pass
- [ ] 25 P1-I2 regression tests still pass
- [ ] Ruff clean
- [ ] Only allowed files modified
- [ ] No LLM calls anywhere
- [ ] No derived values stored in database

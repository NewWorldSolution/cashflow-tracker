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
| I3-T1 | Service layer (validation + calculations)  | Codex       | ✅ DONE    | —            | `feature/p1-i3/t1-services`         |
| I3-T2 | Transaction routes                         | Claude Code | ✅ DONE        | I3-T1    | `feature/p1-i3/t2-routes`           |
| I3-T3 | Create template                            | Claude Code | ✅ DONE        | I3-T1    | `feature/p1-i3/t3-create-template`  |
| I3-T4 | List template + form.js                   | Claude Code | 🔄 IN PROGRESS | I3-T2, I3-T3 | `feature/p1-i3/t4-list-and-js`      |
| I3-T5 | Tests + ruff + PR ready                    | Codex       | ⏳ WAITING | I3-T4        | `feature/p1-i3/t5-tests`            |

---

## Prompts & Reviews

| Task  | Implementation prompt                            | Review prompt                             | Reviewer    |
|-------|--------------------------------------------------|-------------------------------------------|-------------|
| I3-T1 | `iterations/p1-i3/prompts/t1-services.md`        | `iterations/p1-i3/reviews/review-t1.md`  | Claude Code |
| I3-T2 | `iterations/p1-i3/prompts/t2-routes.md`          | `iterations/p1-i3/reviews/review-t2.md`  | Codex       |
| I3-T3 | `iterations/p1-i3/prompts/t3-create-template.md` | `iterations/p1-i3/reviews/review-t3.md`  | Codex       |
| I3-T4 | `iterations/p1-i3/prompts/t4-list-and-js.md`     | `iterations/p1-i3/reviews/review-t4.md`  | Codex       |
| I3-T5 | `iterations/p1-i3/prompts/t5-tests.md`           | `iterations/p1-i3/reviews/review-t5.md`  | Claude Code |
| —     | —                                                | `iterations/p1-i3/reviews/review-iteration.md` | Claude Code (QA) |

---

## Task Details

### I3-T1 — Service layer: validation + calculations (Codex)

**Goal:** Pure service layer. No routes, no templates. Business logic only.

**Read first:** `iterations/p1-i3/prompts/t1-services.md` (full spec)

**Allowed files:**
```
app/services/validation.py
app/services/calculations.py
app/services/__init__.py     ← check if exists before creating; empty package marker only
```

**Functions to implement:**

```python
# app/services/validation.py

validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]
  # Enforces ALL 15 rules from prompt.md "Validation Rules" section.
  # Returns list of error strings. Empty = valid. Never raises.
  # db is the live connection passed from the route handler — do not open a new one.
  # Collect ALL errors before returning — do not stop at first error.
  # Key rules:
  #   category_id → lookup in categories table to verify FK and direction
  #   income_type = 'internal' → vat_rate MUST be 0 (reject any other value)
  #   vat_deductible_pct required on expense, None on income
  #   description required on other_expense / other_income
  #   logged_by → verify integer FK in users table
  #   Category VAT default is a suggestion — user may override (rule 8 is the only VAT restriction)

# app/services/calculations.py
# Use canonical formulas from docs/architecture.md (copied in prompt.md):

vat_amount(gross: Decimal, vat_rate: float) -> Decimal
  # gross - (gross / (1 + vat_rate/100))
  # Quantize to Decimal('0.01'), ROUND_HALF_UP

net_amount(gross: Decimal, vat_rate: float) -> Decimal
  # gross - vat_amount

vat_reclaimable(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal
  # vat_amount * vat_deductible_pct / 100

effective_cost(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal
  # net_amount + (vat_amount * (1 - vat_deductible_pct / 100))
  # Use the canonical formula — not the equivalent shorthand

# Decimal rules:
#   All arithmetic in Decimal — never float
#   Input conversion: Decimal(str(value)) — NEVER Decimal(float(value))
#   All results: .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

**Architecture rules:**
- `validate_transaction` is the ONLY place any validation rule is enforced — routes must not re-implement rules inline
- Parameterised queries only for any DB lookups — never string interpolation
- `calculations.py` has NO database access — pure math functions only
- No `except: pass`, no silent defaults

**Acceptance check:**
```bash
python -c "from app.services.validation import validate_transaction; from app.services.calculations import vat_amount, net_amount, vat_reclaimable, effective_cost; print('imports ok')"
```

**Done when:** Both files importable; all exports present; ruff clean; PR open → `feature/phase-1/iteration-3`.

---

### I3-T2 — Transaction routes (Claude Code)

**Goal:** Four route handlers wired to services. No templates created in this task.

**Depends on:** I3-T1 (validation.py and calculations.py must be ✅ DONE)

**Read first:** `iterations/p1-i3/prompts/t2-routes.md` (full spec)

**Allowed files:**
```
app/routes/transactions.py
app/main.py                    ← register transactions router only; no other changes
```

**Routes to implement:**
```
GET  /transactions/new     → render create.html (template will be added by T3)
POST /transactions/new     → normalise → validate → save or re-render with errors
GET  /transactions/        → fetch last 20 active transactions + compute derived fields
GET  /categories           → JSON list of all categories (exact response structure in prompt.md)
```

**Key contracts:**
- `logged_by = user["id"]` from session — never from form data
- Data normalisation before `validate_transaction` (see prompt.md "Data Normalisation" section)
- On validation failure: re-render with errors list + form_data, status_code=422
- On success: INSERT with explicit column list (see prompt.md) → redirect 302 to /transactions/
- `/categories` returns JSON with exact fields: `category_id`, `name`, `label`, `direction`, `default_vat_rate`, `default_vat_deductible_pct`
- `/categories` is protected by AuthGate — no special handling in route handler

**Acceptance check (T2 only — independent of T3):**
```bash
python -c "from app.routes.transactions import router; print('router imports ok')"
```

Note: End-to-end HTTP tests (GET /transactions/new returns 200) require T3's template and are verified in T5.

**Done when:** Router imports without error; `app/main.py` registers the router; ruff clean; PR open → `feature/phase-1/iteration-3`.

---

### I3-T3 — Create template (Codex)

**Goal:** Full transaction entry form. All fields, inline errors, preserved input, guardrails.

**Depends on:** I3-T1 (knows field names and error message contract)

**Read first:** `iterations/p1-i3/prompts/t3-create-template.md` (full spec)

**Allowed files:**
```
app/templates/transactions/create.html
```

**Template requirements:**
```
- Extends base.html (inherits SANDBOX banner and nav)
- Form: POST /transactions/new, enctype default (not multipart)
- All form fields: date, direction, amount, category_id, payment_method,
  vat_rate, income_type, vat_deductible_pct, description
- Persistent label on amount field: "Enter gross amount (VAT included)"
- Card reminder div (id="card-reminder"): hidden by default, visible when payment_method=card
  Text: "Log gross amount. Card commission is logged separately at month end from terminal invoice"
- income_type row (id="income-type-row"): hidden by default
- vat_deductible_pct row (id="vat-deductible-row"): hidden by default
- Description required indicator (id="desc-required"): hidden by default
- Error display: unordered list of all errors, above the form, only when errors list non-empty
- Input values preserved on error: all fields use form_data dict from route handler
  e.g. value="{{ form_data.get('amount', '') }}"
- Link back to /transactions/
- <script src="/static/form.js"> at bottom of body
```

**Element IDs (used by form.js — must match exactly):**
- `id="card-reminder"` — card payment warning div
- `id="income-type-row"` — row containing income_type field
- `id="vat-deductible-row"` — row containing vat_deductible_pct field
- `id="desc-required"` — required indicator span inside description label

**Acceptance check:**
```bash
python -c "
import os; os.environ['SECRET_KEY'] = 'test'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
# Template file exists and Jinja2 can load it without error
from fastapi.templating import Jinja2Templates
t = Jinja2Templates(directory='app/templates')
print('template loadable ok')
"
```

**Done when:** Template renders without Jinja2 errors; element IDs match spec; ruff N/A; PR open → `feature/phase-1/iteration-3`.

---

### I3-T4 — List template + form.js (Claude Code)

**Goal:** Transaction list page and client-side form behaviour.

**Depends on:** I3-T2 (routes exist and merged), I3-T3 (create template exists and merged)

**Read first:** `iterations/p1-i3/prompts/t4-list-and-js.md` (full spec)

**Allowed files:**
```
app/templates/transactions/list.html
static/form.js
```

**list.html requirements:**
```
- Extends base.html
- Shows transactions in a table (last 20 active, passed from route)
- Columns: date, category label, direction, amount (gross), payment method, logged by (username),
  vat_amount (derived), effective_cost (derived, expense rows only)
- Empty state: "No transactions yet." when list is empty
- Link to /transactions/new ("New transaction" button)
- No JS required on list page
```

**form.js requirements (element IDs must match create.html):**
```javascript
// On DOMContentLoaded:
// Fetch /categories → build lookup map by category_id

// On direction change (input[name="direction"]):
// Show/hide #income-type-row and #vat-deductible-row
// Clear and re-enable vat_rate if income_type was locked

// On category change (select[name="category_id"]):
// Set vat_rate select value to default_vat_rate
// If direction=expense: set vat_deductible_pct to default_vat_deductible_pct
// Show/hide #desc-required based on category name being other_expense or other_income

// On income_type change (select[name="income_type"]):
// If "internal": set vat_rate to "0", set disabled=true
// If "external": set disabled=false

// On payment_method change (select[name="payment_method"]):
// Show/hide #card-reminder

// Vanilla JS only — no import, no require, no build step
```

**Acceptance check:**
```bash
node --check static/form.js
# Expected: no syntax errors, exit code 0
```

**Done when:** list.html renders without Jinja2 errors with empty list; form.js passes `node --check`; ruff N/A for JS; PR open → `feature/phase-1/iteration-3`.

---

### I3-T5 — Tests + ruff + PR ready (Codex)

**Goal:** Full test suite green, ruff clean, iteration closed.

**Depends on:** I3-T4 (all implementation complete and merged)

**Read first:** `iterations/p1-i3/prompts/t5-tests.md` and `iterations/p1-i3/prompt.md` "Tests Required" section (full test list).

**Allowed files:**
```
tests/test_validation.py
tests/test_transactions.py
iterations/p1-i3/tasks.md    ← status update only (closure step)
```

**Fixture requirements:**

```python
# Use two fixtures — not three.

@pytest.fixture
def client(tmp_path):
    # Fresh db, opening balance PRE-SET, authenticated as 'owner'.
    # Pattern from test_auth.py: store db path as attribute on client.
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        c.db_path = db_path   # store for tests that need direct db access
        c.post("/settings/opening-balance", data={"opening_balance": "50000", "as_of_date": "2026-01-01"}, follow_redirects=True)
        c.post("/auth/login", data={"username": "owner", "password": "owner123"})
        yield c

@pytest.fixture
def logged_out_client(tmp_path):
    # Fresh db, opening balance PRE-SET, NOT authenticated.
    # Used ONLY for test_unauthenticated_create_redirects.
    # Note: this is NOT the same as P1-I2's fresh_client (which had no opening balance).
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        c.post("/settings/opening-balance", data={"opening_balance": "50000", "as_of_date": "2026-01-01"}, follow_redirects=True)
        # no login — session is empty
        yield c
```

**Tests to implement:**

Full list in `iterations/p1-i3/prompt.md` "Tests Required" section:
- `tests/test_validation.py`: 22 tests (direct calls to `validate_transaction`)
- `tests/test_transactions.py`: 14 tests (route-level via TestClient)

Read that section before writing any test. Do not invent tests not listed; do not skip tests listed.

**Closure steps:**
1. `pytest` — all tests pass (25 P1-I2 + 36 new P1-I3), exit code 0
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
11. **Read your task prompt file:** `iterations/p1-i3/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency or bootstrap |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-3` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

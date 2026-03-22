# Pre-I5 Comprehensive Review
**Scope:** Full project — P1-I1 through P1-I4 plus post-merge hotfixes
**Branch:** `main`
**Purpose:** Logical and code correctness review before starting P1-I5 (UI polish). Identify any bugs, logic errors, gaps, or architectural problems that should be fixed before the UI layer is built on top.

---

## Context

This is a private cashflow tracker for a 3-person Polish business. Key rules (from `CLAUDE.md`):
- Gross amounts stored — VAT always extracted, never added on top
- No hard deletes — soft delete only (`is_active=FALSE`, `void_reason`, `voided_by`)
- Derived values (vat_amount, net_amount, vat_reclaimable, effective_cost) never stored
- `logged_by` and `voided_by` always from session — never from form
- `void_transaction` in `app/services/transaction_service.py` is the single source of truth for void precondition checks
- `validate_transaction` in `app/services/validation.py` is the single enforcement point for transaction field rules

---

## Files to review

```
app/main.py
app/services/auth_service.py
app/services/validation.py
app/services/calculations.py
app/services/transaction_service.py
app/routes/auth.py
app/routes/transactions.py
app/routes/settings.py
app/templates/base.html
app/templates/dashboard.html
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
static/form.js
db/schema.sql
db/init_db.py
tests/test_auth.py
tests/test_init_db.py
tests/test_validation.py
tests/test_transactions.py
tests/test_calculations.py
```

---

## Review areas

### 1. Business logic correctness

Check each rule from `CLAUDE.md` is correctly enforced end-to-end:

- **VAT extraction:** `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost` in `calculations.py` — are the formulas correct? (VAT extracted from gross, never added on top)
- **income_type = internal:** must force `vat_rate = 0` — is this enforced in validation? Is the JS lock correct and does it actually submit the value (not skip it due to `disabled`)?
- **vat_deductible_pct:** mandatory on every expense row, forbidden on income rows — is this enforced in validation and in the form?
- **Soft delete:** can a voided transaction be voided again? Can a voided transaction be corrected? Are both cases properly handled?
- **Correction flow:** does `POST /transactions/{id}/correct` correctly insert new row → get new id → void original with `replacement_transaction_id` → commit?
- **Category direction:** does validation reject a category whose direction doesn't match the transaction direction?
- **other_expense / other_income:** does validation require a non-empty description for these categories?
- **logged_by / voided_by:** are these ever read from form data anywhere?
- **Show all list:** does `GET /transactions/?show_all=true` actually include voided rows? Does the active-only view correctly exclude them?

### 2. Calculation correctness

Verify the four formulas manually against the test cases in `tests/test_calculations.py`:

- `vat_amount(gross, rate)` — VAT extracted from gross: `gross * rate / (100 + rate)`
- `net_amount(gross, rate)` — `gross - vat_amount`
- `vat_reclaimable(gross, rate, deductible_pct)` — `vat_amount * deductible_pct / 100`
- `effective_cost(gross, rate, deductible_pct)` — `gross - vat_reclaimable`

Are the test values correct? Are edge cases covered (rate=0, deductible_pct=0)?

### 3. Authentication and session security

- Does `require_auth` raise/redirect correctly on unauthenticated requests?
- Is `logged_by` always taken from `user["id"]` in session — never from a form field?
- Is `voided_by` always taken from `user["id"]` in session — never from a form field?
- Does logout properly clear the session?
- Does the zombie session cleanup work (user deleted mid-session)?

### 4. Route handler correctness

For each route, verify:

- **GET /transactions/new** — loads categories, passes today's date
- **POST /transactions/new** — validates, inserts, commits, redirects 302; on error re-renders 422 with errors + preserved form data
- **GET /transactions/** — filters `is_active=TRUE` by default; `?show_all=true` removes filter
- **GET /transactions/{id}** — 200 with full joined data; 404 if not found
- **GET /transactions/{id}/void** — 404 if not found OR already voided; 200 otherwise
- **POST /transactions/{id}/void** — delegates preconditions to `void_transaction`; catches ValueError → 422; commits + 302 on success
- **GET /transactions/{id}/correct** — 404 if not found OR already voided; prefills form with original values
- **POST /transactions/{id}/correct** — validates new data; INSERT → last_insert_rowid → UPDATE original; commits + 302

### 5. Form and JS correctness (`form.js`)

- On page load: are the direction-dependent rows (income-type, vat-deductible) initialized correctly based on any pre-checked radio button?
- On direction change: do income categories and expense categories filter correctly?
- Is the `internal` income type VAT lock working — does selecting internal set vat_rate=0, visually lock it, AND does the value actually get submitted (not blocked by `disabled`)?
- On validation error re-render: is form data preserved correctly across all fields?
- Does the card reminder show/hide correctly on payment method change?
- Does `other_expense` / `other_income` category trigger the "required" description indicator?

### 6. Template correctness

- **create.html:** is `form_action` used with correct default? Does the correct form render for both new and correct flows?
- **list.html:** does the date link to detail? Do voided rows render correctly in show_all mode (opacity, strikethrough, status column)?
- **detail.html:** does the voided state show void_reason, voided_by, and replacement link? Does the active state show void/correct links?
- **void.html:** does the cancel link point back to the correct detail page? Does the void_reason field preserve input on 422 re-render?

### 7. Database and schema

- Does `db/schema.sql` have the correct columns for the full void/correct flow? (`void_reason`, `voided_by`, `replacement_transaction_id`, `is_active`)
- Is `init_db.py` idempotent (safe to run multiple times)?
- Are all FK relationships correct?

### 8. Test coverage gaps

- Are there tests for `GET /transactions/{id}` returning 404?
- Is there a test for `GET /transactions/{id}/void` returning 404 on an already-voided transaction?
- Is there a test for `GET /transactions/?show_all=true` returning voided rows?
- Is `income_type = internal` + VAT lock tested end-to-end?
- Are the calculation formulas tested with rate=0?

---

## How to run

```bash
# Full test suite
pytest -v
# Expected: 81 passed

# Lint
ruff check .
# Expected: clean

# Manual smoke test
python -m uvicorn app.main:app --reload
# Open http://127.0.0.1:8000
```

---

## Required output format

### 1. Overall verdict
`PASS` | `ISSUES FOUND`

### 2. Business logic issues
List any rules from `CLAUDE.md` that are not correctly enforced, with file and line reference.

### 3. Calculation errors
List any incorrect formulas or test values.

### 4. Route / handler bugs
List any incorrect behaviour per route.

### 5. Form / JS bugs
List any broken form behaviour.

### 6. Test coverage gaps
List missing tests that would catch real bugs.

### 7. Security issues
Any session, injection, or auth bypass concerns.

### 8. Recommended fixes before I5
Numbered list, ordered by severity. If none: `None.`

# Phase 1 Plan — Web Form & Transaction Capture

**Status:** Ready to execute
**Timeline:** 14–18 working days across 4 iterations
**Database:** SQLite (sandbox — all data non-production)
**Stack decision (locked):** Flask, not "Flask or FastAPI." This is server-rendered CRUD with 3 known users. FastAPI adds no value here and introduces unnecessary complexity. Decision closed.

---

## What Phase 1 delivers

A working internal tool that lets 3 authenticated users log transactions correctly, view recent history, and correct mistakes — with all VAT rules enforced and a clean audit trail. Phase 1 is done when users can hand the month's records to the accountant without manual reconstruction.

Phase 1 is **not** done when the form works. It is done when the correction flow works and the data is trustworthy.

---

## Project structure (to be created in Iteration 1)

```
cashflow-tracker/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/
│   │   ├── user.py
│   │   ├── transaction.py
│   │   └── category.py
│   ├── services/
│   │   ├── validation.py    # all transaction_validator rules — single source of truth
│   │   └── calculations.py  # derived VAT formulas — never stored, always computed
│   ├── routes/
│   │   ├── auth.py          # login, logout, session
│   │   ├── transactions.py  # create, list, void, correct
│   │   └── settings.py      # opening balance setup
│   └── templates/
│       ├── base.html
│       ├── auth/
│       ├── transactions/
│       └── settings/
├── seed/
│   ├── categories.py        # all 22 categories with defaults
│   └── users.py             # 3 users with hashed passwords
├── tests/
│   ├── test_validation.py
│   └── test_calculations.py
├── db/
│   └── init_db.py           # schema creation + seed runner
├── config.py
└── run.py
```

**Key structure rules:**
- `services/validation.py` is the single enforcement point for all transaction_validator rules — route handlers call it, they do not re-implement rules
- `services/calculations.py` contains all VAT formulas — nothing in templates or route handlers calculates VAT
- No business logic in templates or route handlers — they call services only

---

## Iteration 1 — Foundation
**Days 1–4**

### Goal
Working Flask app with database, seeded data, opening balance setup, and nothing broken.

### Scope
```
app/__init__.py
app/models/user.py
app/models/category.py
app/routes/settings.py
app/templates/settings/opening_balance.html
db/init_db.py
seed/categories.py
seed/users.py
config.py
run.py
```

### Skills to inject
- `skills/cash-flow/schema`
- `skills/cash-flow/auth_logic`

### Deliverables
- Flask app factory with SQLite connection
- `db/init_db.py` creates all tables from the schema (users, categories, transactions, settings)
- `seed/categories.py` inserts all 22 categories with correct defaults (4 income, 18 expense — from docs/concept.md Category Reference)
- `seed/users.py` inserts 3 users with bcrypt-hashed passwords (owner, assistant, wife)
- Opening balance setup page — captures `opening_balance` (PLN) and `as_of_date`, stored in settings table
- System warns if opening balance is not set

### Acceptance criteria
- `python db/init_db.py` runs without error and produces all 4 tables
- All 22 categories present with correct `default_vat_rate` and `default_vat_deductible_pct`
- 3 users present with hashed passwords (passwords never stored in plaintext)
- Opening balance page saves to settings table and can be retrieved
- `settings` table correctly stores `opening_balance` and `as_of_date`

### Constraints (from CLAUDE.md)
- `category_id` is an integer PK — seed data must use the exact names from concept.md
- `logged_by` stores `users.id` FK — never a name string
- `vat_rate` has no CHECK constraint in the database

---

## Iteration 2 — Authentication
**Days 5–7**

### Goal
Login, session management, and route protection. All 3 users can log in and out.

### Scope
```
app/routes/auth.py
app/templates/auth/login.html
app/templates/auth/base.html (update)
```

### Skills to inject
- `skills/cash-flow/auth_logic`
- `skills/cash-flow/error_handling`

### Deliverables
- Login page with username + password fields
- Session set on successful login — `users.id` stored in session, never username string
- All non-auth routes protected — redirect to login if no session
- Logout clears session
- Failed login shows error inline — no generic "wrong credentials" page, show the error on the form

### Acceptance criteria
- All 3 seeded users can log in with correct credentials
- Wrong password shows an error on the login page without redirecting
- Accessing any protected route while logged out redirects to login
- After logout, back button does not restore session
- `session['user_id']` contains `users.id` (integer) — not username, not name

### Constraints (from CLAUDE.md)
- `logged_by` must be `users.id` from session — never typed by user
- No silent failures — login errors surface explicitly on the form

---

## Iteration 3 — Transaction Capture
**Days 8–13**

### Goal
Transaction create form with all VAT rules enforced, all guardrails active, and correct persistence.

### Scope
```
app/routes/transactions.py       (create endpoint)
app/services/validation.py       (all validation rules)
app/services/calculations.py     (VAT formula, for form preview only — not stored)
app/templates/transactions/create.html
app/templates/transactions/list.html   (basic recent list)
```

### Skills to inject
- `skills/cash-flow/transaction_validator`
- `skills/cash-flow/form_logic`
- `skills/cash-flow/error_handling`
- `skills/cash-flow/deterministic_logic`

### Deliverables

**Form fields (all from build-phases.md):**
- Date (default today)
- Direction: income / expense
- Amount (gross)
- Category (dropdown — populates from categories table)
- Payment method: cash / card / transfer
- VAT rate: 0 / 5 / 8 / 23
- Income type: internal / external (shown only for income rows)
- VAT deductible %: 0 / 50 / 100 (shown only for expense rows, mandatory)
- Description (optional; required indicator shown for other_expense / other_income)

**Required guardrails (non-optional):**
- Persistent label on amount: "Enter gross amount (VAT included)"
- Card reminder when payment_method = card: "Log gross amount. Card commission is logged separately at month end from terminal invoice"
- Category selection auto-fills VAT rate and deductible % from category defaults

**Validation rules enforced (server-side — all mandatory):**
- `income_type = internal` → `vat_rate` must be 0 (reject any other value)
- Expense row → `vat_deductible_pct` must be present (100 / 50 / 0)
- `other_expense` or `other_income` → description must be non-empty
- `category_id` must be a valid FK — free-text category rejected
- `logged_by` set from session — never from form input
- `is_active` defaults to TRUE — not a form field

**Recent transaction list:**
- Shows last 20 transactions (active only — `WHERE is_active = TRUE`)
- Columns: date, category label, direction, amount, payment method, logged by (username)
- Ordered by `created_at DESC`

### Acceptance criteria
- Successful transaction saves to DB with all fields correctly populated
- `logged_by` is always `users.id` from session — never null, never a string
- `income_type = internal` with any `vat_rate ≠ 0` is rejected with an error message
- Expense row submitted without `vat_deductible_pct` is rejected
- `other_expense` submitted without description is rejected
- Card payment reminder appears when payment_method = card
- Gross amount label is visible at all times
- Category selection populates VAT rate and deductible % defaults
- Transaction list shows only active rows, ordered by `created_at DESC`
- All form errors shown inline — form does not reset, user input is preserved

### Constraints (from CLAUDE.md)
- No business logic in templates or route handlers — validation.py is the only enforcement point
- VAT calculations are never stored — computed at query time only
- No LLM anywhere in this iteration

---

## Iteration 4 — Corrections, Hardening & Acceptance
**Days 14–18**

### Goal
Void/correct workflow with full audit trail, test coverage on all validation and calculation rules, basic styling, and a working local setup.

### Scope
```
app/routes/transactions.py       (void + correct endpoints)
app/templates/transactions/detail.html
app/templates/transactions/void.html
tests/test_validation.py
tests/test_calculations.py
README.md                        (local setup + demo credentials)
```

### Skills to inject
- `skills/generic/qa_runner`
- `skills/generic/code_reviewer`
- `skills/cash-flow/transaction_validator`
- `skills/cash-flow/error_handling`

### Deliverables

**Void/correct flow:**
- Transaction detail view — shows all fields for a single transaction
- Void action — requires `void_reason` input; sets `is_active = FALSE`, `voided_by = session user_id`
- Correct action — voids original (as above) and opens create form pre-filled with original values; on save, links new transaction via `replacement_transaction_id` on the voided row
- Voided transactions hidden from the main list — visible in admin view only

**Test suite (test_validation.py):**
- `income_type = internal` with `vat_rate ≠ 0` → rejected
- Expense row with `vat_deductible_pct = NULL` → rejected
- `other_expense` with empty description → rejected
- `other_income` with empty description → rejected
- Free-text category value → rejected
- `is_active = FALSE` without `void_reason` → rejected
- Valid transaction for each of the 22 categories → accepted

**Test suite (test_calculations.py):**
- `vat_amount` formula for each valid rate (0, 5, 8, 23)
- `net_amount` derived correctly
- `vat_reclaimable` for deductible % of 0, 50, 100
- `effective_cost` formula
- `net_vat_position` across a mix of income and expense rows

**Local setup:**
- README updated with: local install steps, how to run `db/init_db.py`, demo credentials for all 3 users
- Basic functional styling — not polished, but usable on desktop

### Acceptance criteria
- A voided transaction does not appear in the transaction list
- Voided row has `is_active = FALSE`, non-empty `void_reason`, and `voided_by` set to the acting user
- Correction creates a new transaction and links it via `replacement_transaction_id` on the voided row
- All test cases in test_validation.py pass
- All test cases in test_calculations.py pass
- A new developer can run the app locally using only the README
- 30 sample transactions entered end-to-end with no schema changes required
- At least 3 of those are corrected via the void/correct flow

### Constraints (from CLAUDE.md)
- No hard deletes — ever
- `void_reason` is mandatory when `is_active` is set to FALSE
- `voided_by` must be `users.id` — never a name string

---

## Deferred to later phases

| Item | Phase |
|---|---|
| Monthly summary / reporting | Phase 2 |
| Card reconciliation check | Phase 3 |
| WBSB integration | Phase 4 |
| Telegram bot | Phase 5 |
| LLM extraction (Haiku / Sonnet) | Phase 6 |
| PostgreSQL / Azure go-live | Between phases |
| CSV export | Phase 2 buffer |
| Search / filter by date or category | Phase 2 |
| Responsive mobile styling | Phase 2 buffer |
| Role permissions beyond basic session auth | Not planned |

---

## Success criteria

Phase 1 is complete when:
1. All 3 users can log in and create transactions without developer help
2. 90%+ of common transactions can be entered without free-text workaround
3. All VAT validation rules pass the test suite
4. Opening balance is captured and stored
5. A mistaken entry can be voided and corrected without deleting history
6. 30+ realistic transactions have been entered end-to-end with no schema changes
7. A user can review the recent ledger and trust what was entered

**The real test:** users choose this over WhatsApp, notes, or paper for daily logging. If they do not, Phase 1 is not done regardless of what the code does.

---

## Risks

| Risk | Mitigation |
|---|---|
| Business rules duplicated across routes, templates, and DB | All rules live in `services/validation.py` only — enforced by code_reviewer skill |
| Void flow skipped as "nice to have" | It is must-have — without it, mistakes destroy audit trail |
| VAT edge cases missed in testing | qa_runner skill mandates specific edge cases regardless of scope |
| Phase 2 features creeping into Phase 1 | Deferred list above is explicit — code_reviewer flags scope violations |
| SQLite quirks masking PostgreSQL issues | Use standard SQL only — avoid SQLite-specific syntax |
| Over-indexing on planning, under-executing | Phase 1 brief is now locked. Start Iteration 1 today. |

# cashflow-tracker Iteration Prompt — P1-I8: Hierarchical Categories + Manual VAT + Procedure Metadata

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**

```text
User (web form) → FastAPI route → services/ → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT extracted at query time, never stored unless the user explicitly entered manual VAT values |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — computed at query time only, except user-entered manual VAT values that are part of source data |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point for transaction field rules |

---

## Planning Baseline

- **Iteration branch:** `feature/phase-1/iteration-8`
- **Base branch when I8 starts:** `main` after P1-I7 is merged
- **Current test baseline:** verify on `main` when I8 begins
- **Ruff:** clean
- **Prerequisite iteration:** P1-I7 — multi-company support + accountant flag must be complete before I8 starts
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I8 |
| Title | Hierarchical Categories + Manual VAT + Procedure Metadata |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 8 |
| Feature branch | `feature/phase-1/iteration-8` |
| Depends on | P1-I7 (multi-company + accountant flag — all merged to main) |
| Blocks | P1-I9 (Azure deployment) |
| PR scope | Task branches PR into `feature/phase-1/iteration-8`. The iteration branch PRs into `main` after QA. |

---

## Iteration Goal

Replace the flat 22-category testing structure with a real two-level business taxonomy (19 parent groups, 62 subcategories), rename direction from income/expense to cash_in/cash_out, add manual VAT mode for mixed-rate invoices, and introduce procedure metadata (customer_type, document_flow, for_accountant default change).

After I8:

- direction uses `cash_in` / `cash_out` throughout (DB, validation, UI, i18n)
- `income_type` renamed to `cash_in_type`
- create/correct forms use a two-level category picker
- transactions can use either automatic or manual VAT mode
- every transaction has `customer_type` (private/company/other)
- external cash_in requires `document_flow`; cash_out has it optional
- `for_accountant` defaults to true (except internal cash_in)
- list/detail/dashboard show category paths, manual VAT indicator, and metadata

---

## Reference Documents (source of truth)

| Document | Purpose |
|----------|---------|
| `iterations/p1-i8/scope-decisions.md` | All locked decisions, cross-field validation rules, internal cash_in table |
| `iterations/p1-i8/category-taxonomy.md` | Full taxonomy with slugs, VAT defaults, deductible percentages |
| `iterations/p1-i8/tasks.md` | Task board with statuses and branches |

**Read these documents before starting any task.** They override any conflicting information in this file.

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```text
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md          (I8 section)
iterations/p1-i8/scope-decisions.md
iterations/p1-i8/category-taxonomy.md
```

### Task-specific

| Task | Also read |
|------|-----------|
| I8-T1 | `db/schema.sql`, `db/init_db.py`, `seed/categories.sql`, `app/i18n/en.py`, `app/i18n/pl.py` |
| I8-T2 | `seed/categories.sql`, `db/init_db.py`, `app/i18n/en.py`, `app/i18n/pl.py` |
| I8-T3 | `app/services/validation.py`, `app/services/transaction_service.py`, `app/services/calculations.py` |
| I8-T4 | `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js` |
| I8-T5 | `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js` |
| I8-T6 | `app/routes/transactions.py`, `app/templates/transactions/create.html`, `app/templates/transactions/detail.html`, `static/form.js`, `app/i18n/en.py`, `app/i18n/pl.py` |
| I8-T7 | `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/templates/dashboard.html`, `app/routes/dashboard.py`, `app/routes/transactions.py` |
| I8-T8 | `tests/test_transactions.py`, `tests/test_validation.py`, `tests/test_calculations.py`, `tests/test_init_db.py` |

---

## Key Schema Changes

```text
categories table:
  + parent_id INTEGER REFERENCES categories(category_id)  -- NULL for parent groups
  direction values: 'cash_in' / 'cash_out'                -- renamed from income/expense
  (existing: category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)

transactions table:
  direction values: 'cash_in' / 'cash_out'                -- renamed from income/expense
  income_type → cash_in_type                               -- column renamed
  vat_rate REAL (nullable)                                 -- was NOT NULL, now nullable for manual mode
  + vat_mode TEXT NOT NULL DEFAULT 'automatic'              -- 'automatic' or 'manual'
  + manual_vat_deductible_amount DECIMAL(10,2)             -- new, for manual mode on cash_out
  + customer_type TEXT NOT NULL                             -- 'private' / 'company' / 'other'
  + document_flow TEXT                                     -- nullable; 'invoice'/'receipt'/'invoice_and_receipt'/'other_document'
  (manual_vat_amount already exists in schema)

Old 22 test categories: dropped entirely (fresh start).
New: 19 parent groups + 62 leaf subcategories.
```

---

## Internal Cash_In — Consolidated Rules

When `cash_in_type = internal`, all of the following are enforced:

| Field | Behavior |
|-------|----------|
| `vat_mode` | Forced to `automatic` |
| `vat_rate` | Forced to `0` |
| `payment_method` | Forced to `cash` |
| `for_accountant` | Forced to `false` |
| `customer_type` | Forced to `private`, selector hidden |
| `document_flow` | Hidden, not stored (NULL) |
| Manual VAT toggle | Hidden |

Category is still selectable — internal cash_in can use any cash_in category.

---

## Cross-Field Validation Summary

| Rule | Enforcement |
|------|------------|
| `invoice_and_receipt` only when `customer_type = private` | Validation service + JS |
| `manual_vat_deductible_amount <= manual_vat_amount` | Validation service |
| `vat_rate` required when `vat_mode = automatic` | Validation service |
| `vat_rate` must be NULL when `vat_mode = manual` | Validation service |
| `manual_vat_amount` required when `vat_mode = manual` | Validation service |
| `manual_vat_deductible_amount` required for cash_out when `vat_mode = manual` | Validation service |
| `document_flow` required when `cash_in + cash_in_type = external` | Validation service |
| `document_flow` must be NULL when `cash_in_type = internal` | Validation service |
| `cash_in_type` must be NULL for `cash_out` direction | Validation service |
| `vat_deductible_pct` must be NULL for `cash_in` direction | Validation service |
| `Other Income` and `Other Expense` require non-empty description | Existing rule, carried forward |

---

## Dependency Map

```text
T1 (direction rename + schema foundations)
  └── T2 (category seed + hierarchy + i18n)
        └── T3 (validation + services)
              └── T4 (category picker UI)
                    └── T5 (VAT mode UI)
                          └── T6 (procedure metadata UI)
                                └── T7 (list/detail/dashboard display)
                                      └── T8 (tests)
```

All tasks are sequential. Each depends on the previous.

---

## Deliverables By Task

### I8-T1 — Direction Rename + Schema Foundations

- Rename direction values `income`/`expense` → `cash_in`/`cash_out` in schema and all code
- Rename `income_type` column → `cash_in_type`
- Add `parent_id`, `vat_mode`, `manual_vat_deductible_amount`, `customer_type`, `document_flow` columns
- Make `vat_rate` nullable
- Drop old 22 test categories
- Update CHECK constraints, ALLOWED_DIRECTIONS, all references

### I8-T2 — Category Seed + Hierarchy + i18n

- Seed 19 parent groups + 62 subcategories from taxonomy doc
- Add EN + PL translations for all category labels
- Ensure hierarchy data is queryable (parent → children)

### I8-T3 — Validation + Services

- Update validation.py for all new fields and cross-field rules
- Update transaction_service.py for new columns
- Update calculations.py for manual VAT path
- Internal cash_in consolidated enforcement

### I8-T4 — Category Picker UI

- Two-level category picker in create/correct forms
- Parent dropdown → child dropdown cascade
- Category auto-defaults drive VAT fields
- Correction pre-selects both parent and child
- Hierarchy data embedded on page load (no API calls)

### I8-T5 — VAT Mode UI

- Automatic/Manual toggle in create/correct forms
- Automatic: vat_rate + vat_deductible_pct (cash_out only)
- Manual: manual_vat_amount + manual_vat_deductible_amount (cash_out only)
- Internal cash_in hides toggle
- Manual deductible auto-fills from manual VAT amount
- Correction opens with stored mode preselected

### I8-T6 — Procedure Metadata UI

- customer_type selector (private/company/other) on all transactions
- document_flow selector for external cash_in (required), cash_out (optional), internal (hidden)
- for_accountant defaults to true (except internal cash_in → false)
- Cross-field: invoice_and_receipt only when customer_type = private
- Correction preserves stored values
- EN + PL labels for all new fields

### I8-T7 — List/Detail/Dashboard Display

- Category path display (Parent > Subcategory) in list/detail/dashboard
- Manual VAT indicator in detail view
- customer_type and document_flow in detail view
- for_accountant display in detail view

### I8-T8 — Tests

- Schema/migration tests
- Validation tests for all new fields and cross-field rules
- Create/correct flow tests
- Internal cash_in restriction tests
- Display correctness tests
- Direction rename regression tests

---

## Allowed Files

```text
db/schema.sql
db/init_db.py
seed/categories.sql
app/services/validation.py
app/services/calculations.py
app/services/transaction_service.py
app/routes/transactions.py
app/routes/dashboard.py
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/dashboard.html
app/i18n/en.py
app/i18n/pl.py
static/form.js
tests/test_transactions.py
tests/test_validation.py
tests/test_calculations.py
tests/test_init_db.py
iterations/p1-i8/tasks.md
```

---

## What Must NOT Change

- Auth model — same 3-user session-based auth
- Soft-delete behavior — no changes
- Route paths for existing functionality — no breaking changes
- Company support from I7 — no regression
- Deterministic business logic — no LLM in logic layer

---

## Acceptance Checklist

```bash
pytest -v
ruff check .
```

- [ ] Direction renamed to `cash_in`/`cash_out` throughout
- [ ] `income_type` renamed to `cash_in_type`
- [ ] `parent_id` column exists on categories table
- [ ] 19 parent groups + 62 subcategories seeded
- [ ] Two-level category picker works in create/correct
- [ ] Category path displayed in list/detail/dashboard
- [ ] VAT mode column exists, old rows default to `automatic`
- [ ] `vat_rate` is nullable (NULL when `vat_mode = manual`)
- [ ] Manual VAT works for cash_in (manual_vat_amount only)
- [ ] Manual VAT works for cash_out (manual_vat_amount + manual_vat_deductible_amount)
- [ ] Manual deductible amount cannot exceed manual VAT amount
- [ ] Internal cash_in enforces all consolidated rules (VAT 0, cash, for_accountant=false, customer_type=private, etc.)
- [ ] `customer_type` required on all transactions
- [ ] `document_flow` required for external cash_in, optional for cash_out, hidden for internal
- [ ] `invoice_and_receipt` only allowed when `customer_type = private`
- [ ] `for_accountant` defaults to true except internal cash_in
- [ ] Correction opens with stored values, does not re-apply defaults
- [ ] EN + PL labels for all new UI elements
- [ ] Tests cover all new features
- [ ] ruff clean

---

## Agent Rules

1. Read this file first.
2. Read your task prompt file: `iterations/p1-i8/prompts/t[N]-[name].md`
3. Read `scope-decisions.md` and `category-taxonomy.md` — they override this file on any conflict.
4. Update status to IN PROGRESS before writing any code.
5. Check dependencies — never start if dep is not DONE.
6. Verify acceptance checklist before requesting review.
7. After PR is merged: update `tasks.md` status → DONE with one-line note.
8. No LLM calls in any logic layer.
9. Default locale is `pl` (Polish) — English is the fallback, not the default.
10. All new UI labels must have both EN and PL translations.
11. Test with both locales before marking done.
12. Fresh start on categories — old 22 test categories are dropped entirely, no migration needed.
13. Maximum category depth is 2 levels — do not implement deeper nesting.
14. Only leaf categories (subcategories) are selectable — parent rows are for grouping/reporting only.

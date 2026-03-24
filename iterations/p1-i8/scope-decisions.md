# P1-I8 — Scope Decisions

**Status:** Locked 2026-03-24
**Source of truth** for all I8 planning, prompts, and reviews.

---

## What I8 Includes

### 1. Hierarchical Category System (fresh start)

- Drop all 22 testing categories from I1-I7.
- Seed 19 parent groups and 62 subcategories from `category-taxonomy.md`.
- Schema: add `parent_id INTEGER REFERENCES categories(category_id)` to categories table.
- Two-level maximum: parent → child. Only leaf nodes are selectable.
- VAT defaults set explicitly per subcategory (first-pass pragmatic: 23% normal, 0% where obviously non-VAT).
- No inheritance model — leaf rows are the source of truth for VAT defaults. Parent rows do not carry VAT defaults.
- Globally unique slugs using direction-prefix convention (see taxonomy doc).

### 2. Direction Rename: income/expense → cash_in/cash_out

- DB: `direction` column values change from `income`/`expense` to `cash_in`/`cash_out`.
- DB: CHECK constraints on `direction` updated.
- DB: categories `direction` column values also updated.
- Validation: `ALLOWED_DIRECTIONS` updated.
- All templates, JS, i18n labels updated.
- Since all prior data is testing-only, no production migration needed.

### 3. Field Rename: income_type → cash_in_type

- DB column renamed from `income_type` to `cash_in_type`.
- Values remain: `internal` / `external`.
- Applies only to `cash_in` direction.
- All validation, routes, templates, JS, i18n updated.
- `internal` still enforces: VAT 0, cash payment, `for_accountant = false`, `vat_mode = automatic`, `customer_type = private` (forced), `document_flow` hidden.

### 4. Manual VAT Mode

- New column: `vat_mode TEXT NOT NULL DEFAULT 'automatic'` — values: `automatic` / `manual`.
- `vat_rate` becomes **nullable** — NULL when `vat_mode = manual`. No sentinel values.
- Existing column `manual_vat_amount` is formalized and wired into logic.
- New column: `manual_vat_deductible_amount DECIMAL(10,2)` — for manual mode on cash_out.

#### Automatic mode (current behavior)
- `vat_rate` is required.
- Cash Out uses `vat_deductible_pct`.
- Cash In has no deductible field.
- Calculations derive VAT from gross amount and rate.

#### Manual mode
- **Cash Out:** user enters `manual_vat_amount` and `manual_vat_deductible_amount`.
- **Cash In:** user enters `manual_vat_amount` only. No deductible field.
- `manual_vat_deductible_amount` auto-fills from `manual_vat_amount` on first entry; user may override.
- Validation: `manual_vat_deductible_amount <= manual_vat_amount`.
- No fake blended VAT rates — `vat_rate` is NULL in manual mode.

#### Internal cash_in
- Manual VAT mode is hidden / disallowed.
- Always forces: `vat_mode = automatic`, `vat_rate = 0`, payment = `cash`.

#### Correction flow
- Opens with stored `vat_mode` preselected.
- User may switch between automatic and manual during correction.

#### Display
- Detail view shows a visible indicator when manual VAT was used.
- List/dashboard do not need a manual VAT marker.

### 5. customer_type Field

- New column: `customer_type TEXT NOT NULL` — values: `private` / `company` / `other`.
- **Required on all transactions** — including cash_out, because counterparty type matters for private loans, rent from private persons, and non-company counterparties.
- Meaning of `other`: government, tax office, unknown counterparty, non-standard party.
- **Internal cash_in:** forced to `private`, selector hidden.
- **Per-category customer_type defaults:** deferred to Phase 2. For now, user selects manually. Phase 2 may add category-level defaults so the field pre-fills.

### 6. document_flow Field

- New column: `document_flow TEXT` — **nullable**.
- Values: `invoice` / `receipt` / `invoice_and_receipt` / `other_document`.

#### Rules by context

| Context | Required? | Default | Notes |
|---------|-----------|---------|-------|
| Cash In + external | **Required** | `receipt` | 90% of external cash_in is receipt |
| Cash In + internal | **Hidden** | — | Internal has no document flow |
| Cash Out | **Optional** | NULL | User may fill it, not required. Phase 2 may add category defaults |

#### Cross-field validation
- `invoice_and_receipt` is **only allowed** when `customer_type = private`.
- If `customer_type != private`, the `invoice_and_receipt` option must be disabled/rejected.

#### Polish business logic
- One real transaction may have both invoice and receipt (private person sale).
- Accountant reconciles so it is not double-taxed.
- System represents this as ONE transaction with `document_flow = invoice_and_receipt`, NOT two transactions.

### 7. for_accountant Default Change

- New transactions default `for_accountant = true`.
- User may turn it off.
- Internal cash_in always forces `for_accountant = false`.
- Correction form preserves the stored value — does NOT re-apply the default.
- This is an intentional workflow change. The team understands it.

### 8. Two-Level Category Picker UI

- Form: select parent group first → subcategory dropdown populates.
- Parent group used for reporting/analysis grouping.
- Subcategory is what gets stored on the transaction (`category_id` FK to leaf node).
- Correction pre-selects both parent and child from stored category.
- Vanilla JS only, no API calls for cascade behavior — hierarchy data on page load.

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

## Task Structure (8 tasks)

| ID | Title | Depends on |
|----|-------|-----------|
| T1 | Direction rename + schema foundations | — |
| T2 | Category seed + hierarchy | T1 |
| T3 | Validation + services | T2 |
| T4 | Category picker UI | T3 |
| T5 | VAT mode UI | T4 |
| T6 | Procedure metadata UI (customer_type, document_flow, for_accountant default) | T5 |
| T7 | List/detail/dashboard display | T6 |
| T8 | Tests | T7 |

---

## Key Schema Changes Summary

```
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

Old 22 test categories: dropped entirely.
New: 19 parent groups + 62 leaf subcategories.
```

---

## What I8 Does NOT Include (deferred)

| Item | Deferred To | Reason |
|------|------------|--------|
| Non-Cash / Amortization category | Phase 2 | Needs `affects_cashflow` flag; not a cashflow item |
| Internal Transfer category | Phase 2 | Meaningless without per-company balances |
| Per-company balances | Phase 2 | Each company having its own cash position |
| Per-category customer_type defaults | Phase 2 | Reduces form friction with smart defaults |
| Per-category document_flow defaults (cash_out) | Phase 2 | Same — smart defaults to reduce clicks |
| Role-based access control | Phase 2 | Receptionist vs admin/manager permissions |
| Time-based correction limits | Phase 2 | 7-day window for receptionist, unlimited for admin |
| Reporting | Phase 2 | Needs per-company balances and final category structure first |
| Document number field | Future | |
| Document attachments | Future | |
| Service price catalog / presets | Future | |
| Multi-currency / exchange rates | Future | Too large, deeply affects all layers |

---

## Phase 2 Early Thinking (brainstorm, not committed)

- **Per-company balances** — each company (sp, ltd, ff, private) has own cash position
- **Internal transfers** — move money between company balances
- **Reporting** — leveraging parent-group / subcategory hierarchy for analysis
- **Amortization** — non-cash category for profitability analysis, excluded from cashflow totals
- **Access control** — role-based (receptionist: view/create/correct within 7 days; admin: full access)
- **Category-level defaults** — customer_type and document_flow auto-fill from category to reduce form friction
- **Cybersecurity** — access restrictions, audit logging
- **Invoice receivables tracking** — record a sale on the invoice date as a pending receivable, then mark it paid when cash arrives in the bank. Design: separate `invoices` table (id, date_issued, amount, customer_type, category_id, company_id, description, logged_by, status: pending/paid/void, paid_transaction_id FK). Flow: create invoice → shows in pending receivables list (excluded from cashflow) → mark paid → system auto-creates the transaction and links back to the invoice. Both invoice date and payment date are recorded. VAT calculated on actual payment. This keeps cashflow totals correct (only real cash) while giving visibility into outstanding receivables. Requested by wife 2026-03-24.

These are brainstorm items from 2026-03-24. Validate before planning Phase 2 iterations.

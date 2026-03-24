# I8-T3 — Validation + Services

**Branch:** `feature/p1-i8/t3-validation-services`
**Base:** `feature/phase-1/iteration-8` (after T2 merged)
**Depends on:** I8-T2

---

## Goal

Update the validation service, transaction service, and calculations service to handle all new I8 fields: vat_mode, manual VAT amounts, customer_type, document_flow, for_accountant default, cash_in_type enforcement, and the full cross-field validation matrix. After this task, the backend correctly validates and persists all new fields.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md     ← cross-field validation table is here
app/services/validation.py
app/services/transaction_service.py
app/services/calculations.py
```

---

## Deliverables

### 1. Validation rules in `app/services/validation.py`

Add validation for all new fields. The full cross-field validation matrix from `scope-decisions.md`:

#### vat_mode validation
- `vat_mode` must be `automatic` or `manual`
- When `vat_mode = automatic`: `vat_rate` is required (existing behavior)
- When `vat_mode = manual`: `vat_rate` must be NULL (do not accept a rate)
- When `vat_mode = manual`: `manual_vat_amount` is required
- When `vat_mode = manual` AND direction = `cash_out`: `manual_vat_deductible_amount` is required
- `manual_vat_deductible_amount <= manual_vat_amount` (when both present)

#### customer_type validation
- `customer_type` is required on ALL transactions (cash_in and cash_out)
- Allowed values: `private`, `company`, `other`

#### document_flow validation
- When `cash_in` + `cash_in_type = external`: `document_flow` is required
- When `cash_in_type = internal`: `document_flow` must be NULL
- When `cash_out`: `document_flow` is optional (nullable)
- Allowed values when present: `invoice`, `receipt`, `invoice_and_receipt`, `other_document`
- Cross-field: `invoice_and_receipt` is only allowed when `customer_type = private`

#### Internal cash_in enforcement
When `cash_in_type = internal`, force/validate:
- `vat_mode` = `automatic` (reject `manual`)
- `vat_rate` = `0`
- `payment_method` = `cash`
- `for_accountant` = `false`
- `customer_type` = `private`
- `document_flow` = NULL

#### Direction-specific field rules
- `cash_in_type` must be NULL for `cash_out` direction
- `vat_deductible_pct` must be NULL for `cash_in` direction
- `manual_vat_deductible_amount` should only be present for `cash_out` in manual mode

#### Existing rules (carry forward)
- `Other Income` (`ci_other_income`) and `Other Expense` (`co_other_expense`) require non-empty description
- Category must be a valid leaf node (not a parent group) — validate that `parent_id IS NOT NULL` for the selected category
- Category direction must match transaction direction

#### for_accountant default
- The service layer accepts whatever value the route passes — it does not inject a default.
- The route is responsible for applying the default (`true`) on create and preserving the stored value on correction.
- Internal cash_in forces `false` — the validation service must reject `for_accountant = true` when `cash_in_type = internal`.
- Document this boundary clearly so T6 (which owns the route/form logic) knows where ownership lies.

### 2. Transaction service updates in `app/services/transaction_service.py`

- Accept and persist all new fields: `vat_mode`, `manual_vat_deductible_amount`, `customer_type`, `document_flow`
- Update INSERT and UPDATE queries to include new columns
- Update SELECT queries to return new columns
- Do NOT inject a `for_accountant` default in the service — the route owns that (T6). The service persists whatever it receives.
- Category queries should join to get parent info for path display (or provide a helper)

### 3. Calculations updates in `app/services/calculations.py`

Update derived calculation logic:

```text
When vat_mode = 'automatic':
  vat_amount = amount - (amount / (1 + vat_rate / 100))
  net_amount = amount - vat_amount
  vat_reclaimable (cash_out) = vat_amount * vat_deductible_pct / 100

When vat_mode = 'manual':
  vat_amount = manual_vat_amount                    (user-entered, stored)
  net_amount = amount - manual_vat_amount
  vat_reclaimable (cash_out) = manual_vat_deductible_amount  (user-entered, stored)
```

- `effective_cost` (cash_out) = `net_amount + (vat_amount - vat_reclaimable)`
- Cash_in has no deductible fields — `vat_reclaimable` is N/A for cash_in

### 4. Category hierarchy helpers

Add helper function(s) to support:
- **Leaf-only validation**: Check that a category_id points to a leaf node (has `parent_id IS NOT NULL`)
- **Category path lookup**: Given a leaf category_id, return `"Parent Label > Child Label"` string
- **Children-of-parent query**: Given a parent category_id, return all child categories (for the picker)
- **Categories-by-direction**: Return all parent groups for a given direction, with their children

---

## Important Rules

- **Validation is the single enforcement point** — all rules must be in `validation.py`, not scattered across routes or templates.
- **Do NOT modify templates or routes** — that is T4-T6's job.
- **Do NOT modify tests** — that is T8's job.
- **Internal cash_in rules are FORCED, not defaults** — validation must reject violations, not silently correct them.
- **for_accountant default change** — new transactions default to `true`. But correction must use the stored value.
- **Leaf-only selection** — parent groups (parent_id IS NULL) must be rejected as category_id values.

---

## Allowed Files

```text
app/services/validation.py
app/services/transaction_service.py
app/services/calculations.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] All cross-field validation rules from scope-decisions.md are implemented
- [ ] `vat_mode = manual` correctly requires manual amounts and rejects vat_rate
- [ ] `vat_mode = automatic` correctly requires vat_rate
- [ ] `customer_type` is validated as required on all transactions
- [ ] `document_flow` is required for external cash_in, optional for cash_out, rejected for internal
- [ ] `invoice_and_receipt` is rejected when `customer_type != private`
- [ ] Internal cash_in enforcement rejects all violations
- [ ] Category validation rejects parent groups (leaf-only)
- [ ] Category direction mismatch is rejected
- [ ] Transaction service persists and retrieves all new fields
- [ ] Calculations handle both automatic and manual VAT modes
- [ ] Category path helper returns "Parent > Child" format
- [ ] `for_accountant` defaults to `true` for new transactions
- [ ] `ruff check .` passes

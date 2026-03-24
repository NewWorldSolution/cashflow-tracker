# Review — I8-T3: Validation + Services
**Branch:** `feature/p1-i8/t3-validation-services`
**PR target:** `feature/phase-1/iteration-8`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `app/services/validation.py` — all cross-field validation rules for new I8 fields
- `app/services/transaction_service.py` — accepts/persists new columns, `for_accountant` default changed to `true`, category path helper added
- `app/services/calculations.py` — manual VAT calculation path alongside automatic

---

## Review Steps

1. Confirm diff scope is limited to `app/services/validation.py`, `app/services/transaction_service.py`, and `app/services/calculations.py`.

2. **vat_mode validation** — verify:
   - `vat_mode = automatic` requires `vat_rate` (not NULL)
   - `vat_mode = manual` requires `manual_vat_amount`
   - `vat_mode = manual` rejects non-NULL `vat_rate`
   - `vat_mode = manual` + `cash_out` requires `manual_vat_deductible_amount`
   - `manual_vat_deductible_amount > manual_vat_amount` is rejected

3. **customer_type validation** — verify:
   - Required on ALL transactions (cash_in and cash_out)
   - Allowed values: `private`, `company`, `other` only

4. **document_flow validation** — verify:
   - Required when `cash_in` + `cash_in_type = external`
   - Must be NULL when `cash_in_type = internal`
   - Optional (nullable) for `cash_out`
   - Allowed values: `invoice`, `receipt`, `invoice_and_receipt`, `other_document`
   - `invoice_and_receipt` rejected when `customer_type != private`

5. **Internal cash_in enforcement** — verify all are enforced when `cash_in_type = internal`:
   - `vat_mode = manual` rejected
   - `vat_rate != 0` rejected
   - `payment_method != cash` rejected
   - `for_accountant = true` rejected (forced false)
   - `customer_type != private` rejected
   - `document_flow` not NULL rejected

6. **Direction-specific rules** — verify:
   - `cash_in_type` is NULL for `cash_out` transactions (rejected if set)
   - `vat_deductible_pct` is NULL for `cash_in` transactions (rejected if set)

7. **Leaf-only category validation** — verify:
   - Parent group categories (where `parent_id IS NULL`) are rejected as `category_id`
   - Category direction must match transaction direction

8. **transaction_service.py** — verify:
   - INSERT/UPDATE queries include all new columns: `vat_mode`, `manual_vat_deductible_amount`, `customer_type`, `document_flow`
   - SELECT queries return new columns
   - The service persists whatever `for_accountant` value it receives — it must NOT inject a default itself. The create-form default (`true`) is owned by the route (T6); the service is a pass-through.
   - Category path helper exists (returns "Parent > Child" format)

9. **calculations.py** — verify:
   - When `vat_mode = automatic`: existing formula used (`amount - amount / (1 + vat_rate/100)`)
   - When `vat_mode = manual`: `manual_vat_amount` used directly as vat_amount
   - When `vat_mode = manual` + cash_out: `manual_vat_deductible_amount` used for reclaimable
   - No fake blended vat_rate stored or returned

10. Verify no route, template, JS, i18n, or test changes were made.
11. Run:

```bash
pytest -v
ruff check .
```

---

## Required Output Format

### 1. Verdict

```text
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```text
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/services/validation.py`, `app/services/transaction_service.py`, `app/services/calculations.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `vat_mode = automatic` requires `vat_rate`
- [PASS|FAIL] `vat_mode = manual` requires `manual_vat_amount` and rejects `vat_rate`
- [PASS|FAIL] `manual_vat_deductible_amount > manual_vat_amount` rejected
- [PASS|FAIL] `customer_type` required on all transactions with correct allowed values
- [PASS|FAIL] `document_flow` required for external cash_in
- [PASS|FAIL] `document_flow` must be NULL for internal cash_in
- [PASS|FAIL] `invoice_and_receipt` rejected when `customer_type != private`
- [PASS|FAIL] all 6 internal cash_in enforcement rules implemented
- [PASS|FAIL] `cash_in_type` rejected on cash_out transactions
- [PASS|FAIL] `vat_deductible_pct` rejected on cash_in transactions
- [PASS|FAIL] parent group category_id rejected (leaf-only)
- [PASS|FAIL] category direction mismatch rejected
- [PASS|FAIL] transaction service persists all new columns
- [PASS|FAIL] transaction service does NOT inject a `for_accountant` default (that is the route's job in T6)
- [PASS|FAIL] category path helper returns "Parent > Child" format
- [PASS|FAIL] calculations handle both automatic and manual VAT modes
- [PASS|FAIL] no routes/templates/JS/i18n/tests modified
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

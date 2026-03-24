# I8-T8 — Tests

**Branch:** `feature/p1-i8/t8-tests`
**Base:** `feature/phase-1/iteration-8` (after T7 merged)
**Depends on:** I8-T7

---

## Goal

Update and extend the test suite to cover all I8 changes: direction rename, category hierarchy, manual VAT mode, customer_type, document_flow, for_accountant defaults, cross-field validation, and display correctness. All existing tests must be updated to use the new direction/field names. After this task, `pytest -v` passes cleanly.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md     ← cross-field validation rules
iterations/p1-i8/category-taxonomy.md   ← expected seed data
tests/test_transactions.py
tests/test_validation.py
tests/test_calculations.py
tests/test_init_db.py
```

---

## Deliverables

### 1. Update existing tests for direction rename

All existing tests that reference `income`/`expense` must be updated to `cash_in`/`cash_out`. All references to `income_type` must become `cash_in_type`.

Files to update:
- `tests/test_transactions.py`
- `tests/test_validation.py`
- `tests/test_calculations.py`
- `tests/test_init_db.py`

### 2. Schema/migration tests in `tests/test_init_db.py`

- [ ] Categories table has `parent_id` column
- [ ] 19 parent groups exist with `parent_id IS NULL`
- [ ] 62 subcategories exist with valid `parent_id` references
- [ ] All slugs from taxonomy doc exist in DB
- [ ] Parent groups have NULL VAT defaults
- [ ] Subcategory VAT defaults match taxonomy document
- [ ] Transactions table has `vat_mode`, `customer_type`, `document_flow`, `manual_vat_deductible_amount` columns
- [ ] `vat_rate` is nullable
- [ ] `cash_in_type` column exists (not `income_type`)
- [ ] Direction CHECK constraint accepts `cash_in`/`cash_out`

### 3. Validation tests in `tests/test_validation.py`

#### vat_mode rules
- [ ] `vat_mode = automatic` requires `vat_rate`
- [ ] `vat_mode = manual` requires `manual_vat_amount`
- [ ] `vat_mode = manual` rejects non-NULL `vat_rate`
- [ ] `vat_mode = manual` + cash_out requires `manual_vat_deductible_amount`
- [ ] `manual_vat_deductible_amount > manual_vat_amount` is rejected

#### customer_type rules
- [ ] Missing `customer_type` is rejected
- [ ] Invalid `customer_type` value is rejected
- [ ] Valid values accepted: `private`, `company`, `other`

#### document_flow rules
- [ ] External cash_in without `document_flow` is rejected
- [ ] Internal cash_in with `document_flow` set is rejected
- [ ] Cash_out with no `document_flow` is accepted (optional)
- [ ] Invalid `document_flow` value is rejected
- [ ] `invoice_and_receipt` + `customer_type = company` is rejected
- [ ] `invoice_and_receipt` + `customer_type = private` is accepted

#### Internal cash_in enforcement
- [ ] Internal cash_in with `vat_mode = manual` is rejected
- [ ] Internal cash_in with `vat_rate != 0` is rejected
- [ ] Internal cash_in with `payment_method != cash` is rejected
- [ ] Internal cash_in with `for_accountant = true` is rejected (or forced false)
- [ ] Internal cash_in with `customer_type != private` is rejected
- [ ] Internal cash_in with `document_flow` set is rejected

#### Direction-specific rules
- [ ] `cash_in_type` set on `cash_out` transaction is rejected
- [ ] `vat_deductible_pct` set on `cash_in` transaction is rejected

#### Category rules
- [ ] Parent group category_id is rejected (leaf-only selection)
- [ ] Category direction mismatch is rejected (e.g., cash_in category on cash_out transaction)
- [ ] Valid leaf category_id is accepted

#### Existing rules still pass
- [ ] `other_income` / `other_expense` slug categories require description
- [ ] All existing validation tests pass with updated direction/field names

### 4. Calculation tests in `tests/test_calculations.py`

#### Automatic mode (existing behavior, updated field names)
- [ ] VAT amount calculated correctly: `amount - (amount / (1 + vat_rate / 100))`
- [ ] Net amount: `amount - vat_amount`
- [ ] VAT reclaimable (cash_out): `vat_amount * vat_deductible_pct / 100`

#### Manual mode
- [ ] Manual VAT amount used directly as `vat_amount`
- [ ] Manual net amount: `amount - manual_vat_amount`
- [ ] Manual VAT reclaimable (cash_out): `manual_vat_deductible_amount` used directly
- [ ] Manual effective cost calculated correctly

### 5. Transaction flow tests in `tests/test_transactions.py`

#### Create flow
- [ ] Create cash_in transaction with all new fields
- [ ] Create cash_out transaction with all new fields
- [ ] Create internal cash_in with forced values
- [ ] Create transaction with manual VAT mode
- [ ] Create transaction with document_flow
- [ ] for_accountant defaults to true on create

#### Correct flow
- [ ] Correct preserves stored vat_mode
- [ ] Correct preserves stored customer_type
- [ ] Correct preserves stored document_flow
- [ ] Correct preserves stored for_accountant (does NOT re-default)
- [ ] Correct allows switching vat_mode
- [ ] Correct pre-selects category parent and child

#### Category picker
- [ ] Two-level category selection works (leaf node stored)
- [ ] Direction change resets category selection

### 6. Test helpers

Update test helper functions to:
- Use `cash_in`/`cash_out` instead of `income`/`expense`
- Use `cash_in_type` instead of `income_type`
- Include `customer_type` (default to `private` for test simplicity)
- Include `vat_mode` (default to `automatic`)
- Use valid leaf category IDs (not parent group IDs)

---

## Important Rules

- **All tests must pass**: `pytest -v` must be green
- **Update ALL existing tests** — do not leave any `income`/`expense`/`income_type` references
- **Use real seed data** — test category IDs must match the seeded taxonomy
- **Test both directions** — cash_in and cash_out for every rule that differs by direction
- **Test cross-field combinations** — especially internal cash_in and invoice_and_receipt + customer_type
- **Do NOT modify application code** — all app changes are done in T1-T7. Only modify test files.

---

## Allowed Files

```text
tests/test_transactions.py
tests/test_validation.py
tests/test_calculations.py
tests/test_init_db.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] `pytest -v` passes with zero failures
- [ ] `ruff check .` passes
- [ ] No references to `income`/`expense` as direction values in test code
- [ ] No references to `income_type` in test code (all `cash_in_type`)
- [ ] Schema tests verify all new columns exist
- [ ] Seed tests verify 19 parents + 62 subcategories
- [ ] Validation tests cover all cross-field rules from scope-decisions.md
- [ ] Calculation tests cover both automatic and manual VAT modes
- [ ] Transaction flow tests cover create and correct with all new fields
- [ ] Internal cash_in enforcement fully tested
- [ ] Category leaf-only selection tested
- [ ] document_flow visibility rules tested per context
- [ ] for_accountant default behavior tested (true for new, preserved for correction)

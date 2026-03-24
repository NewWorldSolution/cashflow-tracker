# QA Review — P1-I8: Hierarchical Categories + Manual VAT + Procedure Metadata
**Reviewer:** QA agent
**Branch:** `feature/phase-1/iteration-8`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T8) show ✅ DONE in `iterations/p1-i8/tasks.md`
**Reference docs:** `iterations/p1-i8/prompt.md`, `iterations/p1-i8/scope-decisions.md`, `iterations/p1-i8/category-taxonomy.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 8. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

Use the implementation prompts in `iterations/p1-i8/prompts/` and the locked planning docs above as the detailed source of truth for task boundaries, acceptance criteria, and cross-field rules.

---

## What this iteration was supposed to deliver

1. Direction renamed from `income` / `expense` to `cash_in` / `cash_out`
2. `income_type` renamed to `cash_in_type`
3. Old flat testing categories replaced with 19 parent groups and 62 leaf subcategories
4. Category selection is leaf-only and uses a two-level picker
5. Slugs are globally unique and stable
6. Manual VAT mode exists for mixed-rate transactions
7. `vat_rate` is nullable in manual mode
8. Internal cash_in still enforces VAT 0, cash payment, no accountant flag, hidden document flow
9. `customer_type` exists and is required on all transactions
10. `document_flow` exists, required for external cash_in, optional for cash_out
11. `invoice_and_receipt` is allowed only for `customer_type = private`
12. New transactions default `for_accountant = true` except internal cash_in
13. Detail/list/dashboard display the new hierarchy and metadata correctly
14. Full test coverage exists for direction rename, hierarchy, VAT mode, and metadata rules

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-8
git pull origin feature/phase-1/iteration-8
```

### Step 2 — Full suite and lint

```bash
pytest -v
ruff check .
```

Expected:

- All tests pass
- Ruff is clean

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected implementation files may include:

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
tests/test_init_db.py
tests/test_validation.py
tests/test_calculations.py
tests/test_transactions.py
```

Iteration planning/docs files may also appear in the diff; this is expected:

```text
iterations/p1-i8/tasks.md
iterations/p1-i8/prompt.md
iterations/p1-i8/category-taxonomy.md
iterations/p1-i8/scope-decisions.md
iterations/p1-i8/prompts/*.md
iterations/p1-i8/reviews/*.md
```

Frozen areas that should not change unless explicitly justified by the merged task branches:

```text
app/services/auth_service.py
seed/users.sql
app/main.py
```

### Step 4 — Architecture checks

Verify by code inspection:

- [ ] No hard deletes introduced
- [ ] No derived VAT/net/effective-cost values started being stored directly
- [ ] Validation remains centralized in the service layer
- [ ] `cash_in_type` applies only to `cash_in`
- [ ] Manual VAT logic does not use fake blended `vat_rate` values
- [ ] No 3-level category hierarchy was introduced
- [ ] `logged_by` and `voided_by` remain integer FKs — no name strings stored

### Step 5 — Schema and seed checks

Verify by code inspection:

- [ ] `categories.parent_id` exists
- [ ] categories use `cash_in` / `cash_out` direction values
- [ ] 19 parent groups exist with `parent_id IS NULL`
- [ ] 62 leaf subcategories exist with valid `parent_id`
- [ ] leaf categories have globally unique slugs
- [ ] leaf VAT defaults match `category-taxonomy.md`
- [ ] `transactions.cash_in_type` exists instead of `income_type`
- [ ] `transactions.vat_mode` exists
- [ ] `transactions.vat_rate` is nullable
- [ ] `transactions.manual_vat_deductible_amount` exists
- [ ] `transactions.customer_type` exists
- [ ] `transactions.document_flow` exists and is nullable

### Step 6 — UI and flow checks

Verify by code inspection and, if needed, manual app run:

- [ ] create/correct forms use the two-level category picker
- [ ] only leaf categories can be submitted
- [ ] manual VAT mode works for cash_in and cash_out per scope
- [ ] internal cash_in hides manual VAT mode and document flow
- [ ] internal cash_in forces `vat_rate = 0`, payment `cash`, and `for_accountant = false`
- [ ] create form defaults `for_accountant` to checked for non-internal transactions
- [ ] correct form preserves stored `for_accountant`
- [ ] `customer_type` is required and behaves correctly for internal cash_in
- [ ] `document_flow` is required for external cash_in and optional for cash_out
- [ ] `invoice_and_receipt` is unavailable when `customer_type != private`
- [ ] list view shows translated `Parent > Subcategory`
- [ ] detail view shows full hierarchy path
- [ ] detail view shows manual VAT indicator when applicable
- [ ] detail view shows `customer_type`, `document_flow` when present, and `for_accountant`
- [ ] dashboard uses translated `cash_in` / `cash_out` labels

### Step 7 — Translation checks

Verify by reading `app/i18n/en.py` and `app/i18n/pl.py`:

- [ ] category parent and child labels exist for the seeded taxonomy
- [ ] `cash_in` / `cash_out` display labels exist
- [ ] VAT mode labels exist
- [ ] customer type labels exist
- [ ] document flow labels exist
- [ ] translations are consistent and professional

### Step 8 — Test coverage checks

Verify the final merged tests cover:

- [ ] direction rename to `cash_in` / `cash_out`
- [ ] `cash_in_type` rename
- [ ] hierarchy seed shape: 19 parents, 62 leaves
- [ ] unique slugs
- [ ] VAT defaults from taxonomy
- [ ] manual VAT validation and calculations
- [ ] external cash_in `document_flow` requirement
- [ ] `invoice_and_receipt` private-only rule
- [ ] internal cash_in enforcement
- [ ] create/correct flows with hierarchy and metadata

---

## Required output format

### 1. Verdict

```text
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

Full list with file references.

### 3. Problems Found

```text
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Architecture Violations

If none: `None.`

### 5. Acceptance Criteria Check

- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean
- [PASS|FAIL] direction renamed everywhere to `cash_in` / `cash_out`
- [PASS|FAIL] `cash_in_type` replaced `income_type` correctly
- [PASS|FAIL] 19 parent groups and 62 leaf subcategories are seeded correctly
- [PASS|FAIL] slugs are globally unique and stable
- [PASS|FAIL] leaf-only category selection is enforced
- [PASS|FAIL] two-level picker works in create and correct flows
- [PASS|FAIL] manual VAT mode works for cash_in and cash_out
- [PASS|FAIL] `vat_rate` is nullable and not misused in manual mode
- [PASS|FAIL] internal cash_in restrictions are enforced
- [PASS|FAIL] `customer_type` exists and is required
- [PASS|FAIL] `document_flow` required/optional behavior matches scope
- [PASS|FAIL] `invoice_and_receipt` is allowed only for `private`
- [PASS|FAIL] create defaults `for_accountant` to true except internal cash_in
- [PASS|FAIL] correct form preserves stored metadata values
- [PASS|FAIL] list/detail/dashboard display hierarchy and metadata correctly
- [PASS|FAIL] EN + PL translations cover all new UI
- [PASS|FAIL] tests cover renamed fields, hierarchy, VAT mode, and metadata rules
- [PASS|FAIL] frozen files remain unchanged or justified

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

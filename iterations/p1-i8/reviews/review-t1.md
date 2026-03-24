# Review — I8-T1: Direction Rename + Schema Foundations
**Branch:** `feature/p1-i8/t1-direction-schema`
**PR target:** `feature/phase-1/iteration-8`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `db/schema.sql` — direction CHECK constraints updated, `income_type` renamed to `cash_in_type`, `parent_id` added to categories, new transaction columns added (`vat_mode`, `manual_vat_deductible_amount`, `customer_type`, `document_flow`), `vat_rate` made nullable
- `db/init_db.py` — runs updated schema cleanly
- `seed/categories.sql` — old 22 test categories removed, file emptied or commented
- `app/services/validation.py` — `ALLOWED_DIRECTIONS` updated, `income_type` → `cash_in_type` references updated
- `app/services/transaction_service.py` — all `income`/`expense` string literals → `cash_in`/`cash_out`, `income_type` → `cash_in_type`
- `app/services/calculations.py` — direction references updated if any
- `app/routes/transactions.py` — direction and column name references updated
- `app/routes/dashboard.py` — direction references updated
- `app/templates/transactions/create.html` — direction values updated
- `app/templates/transactions/list.html` — direction display updated
- `app/templates/transactions/detail.html` — direction display updated
- `app/templates/dashboard.html` — direction references updated
- `static/form.js` — all `income`/`expense` checks → `cash_in`/`cash_out`, `income_type` → `cash_in_type`
- `app/i18n/en.py` — direction labels and income_type/cash_in_type keys updated
- `app/i18n/pl.py` — same as en.py

---

## Review Steps

1. Confirm diff scope is limited to the 15 allowed files above.
2. Verify `db/schema.sql` categories CHECK constraint uses `('cash_in','cash_out')`.
3. Verify `db/schema.sql` transactions CHECK constraint uses `('cash_in','cash_out')`.
4. Verify `income_type` column no longer exists in schema — replaced by `cash_in_type`.
5. Verify `cash_in_type CHECK(cash_in_type IN ('internal','external'))` is present.
6. Verify `categories.parent_id INTEGER REFERENCES categories(category_id)` is added (NULL for parent groups).
7. Verify new transaction columns exist:
   - `vat_mode TEXT NOT NULL DEFAULT 'automatic'` with CHECK(`automatic`,`manual`)
   - `manual_vat_deductible_amount DECIMAL(10,2)` (nullable)
   - `customer_type TEXT NOT NULL` with CHECK(`private`,`company`,`other`)
   - `document_flow TEXT` (nullable) with CHECK(`invoice`,`receipt`,`invoice_and_receipt`,`other_document`)
8. Verify `vat_rate` is now nullable (was `NOT NULL`).
9. Verify `manual_vat_amount` column was NOT added again (it already existed).
10. Verify `seed/categories.sql` has the old 22 categories removed.
11. Verify `ALLOWED_DIRECTIONS` in `validation.py` is `['cash_in', 'cash_out']`.
12. Verify no `income` or `expense` string literals remain in `validation.py`, `transaction_service.py`, or `calculations.py` (as direction values).
13. Verify no `income_type` references remain — all updated to `cash_in_type`.
14. Verify JS in `form.js` uses `cash_in`/`cash_out` in all direction checks.
15. Verify no new validation rules for the new columns were added yet (those are T3's job).
16. Verify no category seed data was added (that is T2's job).
17. Run:

```bash
python db/init_db.py
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

Files modified outside the allowed list for this task.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] categories CHECK uses `cash_in`/`cash_out`
- [PASS|FAIL] transactions CHECK uses `cash_in`/`cash_out`
- [PASS|FAIL] `income_type` column gone, `cash_in_type` present with correct CHECK
- [PASS|FAIL] `categories.parent_id` added
- [PASS|FAIL] `vat_mode` column added (TEXT NOT NULL DEFAULT 'automatic', CHECK constraint)
- [PASS|FAIL] `manual_vat_deductible_amount` column added (nullable DECIMAL)
- [PASS|FAIL] `customer_type` column added (TEXT NOT NULL, CHECK constraint)
- [PASS|FAIL] `document_flow` column added (nullable TEXT, CHECK constraint)
- [PASS|FAIL] `vat_rate` is now nullable
- [PASS|FAIL] `manual_vat_amount` was NOT added again
- [PASS|FAIL] old 22 categories removed from `seed/categories.sql`
- [PASS|FAIL] `ALLOWED_DIRECTIONS` uses `cash_in`/`cash_out`
- [PASS|FAIL] no residual `income`/`expense` direction string literals in service/route files
- [PASS|FAIL] no residual `income_type` references in any allowed file
- [PASS|FAIL] JS updated for `cash_in`/`cash_out` and `cash_in_type`
- [PASS|FAIL] i18n updated for renamed fields
- [PASS|FAIL] no new category seed data (T2's job)
- [PASS|FAIL] no new validation rules for new columns (T3's job)
- [PASS|FAIL] `init_db.py` runs cleanly
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

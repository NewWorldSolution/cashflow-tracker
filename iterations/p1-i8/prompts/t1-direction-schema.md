# I8-T1 — Direction Rename + Schema Foundations

**Branch:** `feature/p1-i8/t1-direction-schema`
**Base:** `feature/phase-1/iteration-8`
**Depends on:** — (first task)

---

## Goal

Rename direction values from `income`/`expense` to `cash_in`/`cash_out`, rename the `income_type` column to `cash_in_type`, add all new schema columns, make `vat_rate` nullable, and drop the old 22 test categories. This task lays the schema foundation for the entire iteration — no seed data, no validation changes, no UI changes.

---

## Read Before Starting

```text
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md
iterations/p1-i8/category-taxonomy.md
db/schema.sql
db/init_db.py
seed/categories.sql
```

---

## Deliverables

### 1. Direction rename in schema

- `db/schema.sql`: Change CHECK constraint on `transactions.direction` from `('income','expense')` to `('cash_in','cash_out')`
- `db/schema.sql`: Change CHECK constraint on `categories.direction` from `('income','expense')` to `('cash_in','cash_out')`
- `db/init_db.py`: Update any hardcoded direction values

### 2. Column rename: income_type → cash_in_type

- `db/schema.sql`: Rename the column from `income_type` to `cash_in_type`
- Update CHECK constraint: `cash_in_type IN ('internal','external')`
- Values remain `internal` / `external` — no change to allowed values

### 3. Add parent_id to categories

- `db/schema.sql`: Add `parent_id INTEGER REFERENCES categories(category_id)` to categories table
- NULL means parent group, non-NULL means subcategory (leaf node)

### 4. New transaction columns

Add to `db/schema.sql`:

```sql
vat_mode TEXT NOT NULL DEFAULT 'automatic'  -- CHECK(vat_mode IN ('automatic','manual'))
manual_vat_deductible_amount DECIMAL(10,2)  -- for manual mode on cash_out
customer_type TEXT NOT NULL                 -- CHECK(customer_type IN ('private','company','other'))
document_flow TEXT                          -- CHECK(document_flow IN ('invoice','receipt','invoice_and_receipt','other_document'))
```

### 5. Make vat_rate nullable

- `db/schema.sql`: Change `vat_rate REAL NOT NULL` → `vat_rate REAL` (nullable)
- NULL is valid when `vat_mode = manual`

### 6. Drop old categories

- `seed/categories.sql`: Remove all 22 old test categories
- Leave the file empty or with a comment — T2 will populate it with the new taxonomy

### 7. Direction rename in application code

- `app/services/validation.py`: Update `ALLOWED_DIRECTIONS` from `['income', 'expense']` to `['cash_in', 'cash_out']`
- Update all references to `income_type` → `cash_in_type` in validation.py
- `app/services/transaction_service.py`: Update all `income`/`expense` string literals to `cash_in`/`cash_out`, all `income_type` references to `cash_in_type`
- `app/services/calculations.py`: Update direction references if any
- `app/routes/transactions.py`: Update all `income`/`expense` references to `cash_in`/`cash_out`, `income_type` to `cash_in_type`
- `app/routes/dashboard.py`: Update direction references
- `app/templates/transactions/create.html`: Update direction values in form
- `app/templates/transactions/list.html`: Update direction display
- `app/templates/transactions/detail.html`: Update direction display
- `app/templates/dashboard.html`: Update direction references
- `static/form.js`: Update all `income`/`expense` checks to `cash_in`/`cash_out`, `income_type` to `cash_in_type`
- `app/i18n/en.py`: Update direction labels, rename income_type keys to cash_in_type
- `app/i18n/pl.py`: Same updates as en.py

### 8. Update init_db.py

- Ensure `init_db.py` runs the updated schema correctly
- Drop and recreate tables (this is sandbox/testing data — no migration needed)

---

## Important Rules

- **Fresh start** — all old data is testing-only. No production migration needed. Drop and recreate is acceptable.
- **Do NOT seed new categories** — that is T2's job. Just clear the old ones.
- **Do NOT update validation rules** for new fields yet — that is T3's job. Only update direction/cash_in_type references.
- **Do NOT add UI elements** for new fields — that is T4-T6's job.
- All CHECK constraints for new columns should be in schema.sql.
- `manual_vat_amount` column already exists in schema — do not add it again.

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
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] `schema.sql` uses `cash_in`/`cash_out` in all CHECK constraints
- [ ] `income_type` column renamed to `cash_in_type` in schema
- [ ] `parent_id` column exists on categories table
- [ ] `vat_mode`, `manual_vat_deductible_amount`, `customer_type`, `document_flow` columns added
- [ ] `vat_rate` is nullable
- [ ] Old 22 categories removed from `seed/categories.sql`
- [ ] `ALLOWED_DIRECTIONS` uses `cash_in`/`cash_out`
- [ ] All `income`/`expense` string literals in allowed files updated to `cash_in`/`cash_out`
- [ ] All `income_type` references updated to `cash_in_type`
- [ ] i18n labels updated for direction rename
- [ ] `init_db.py` runs cleanly with new schema
- [ ] `ruff check .` passes
- [ ] Application starts without errors (no need for full test suite yet — tests will be updated in T8)

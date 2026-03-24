# Review — I8-T2: Category Seed + Hierarchy + i18n
**Branch:** `feature/p1-i8/t2-category-seed`
**PR target:** `feature/phase-1/iteration-8`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `seed/categories.sql` — 19 parent groups + 62 subcategories seeded with correct slugs, directions, VAT defaults, and deductible percentages per `category-taxonomy.md`
- `db/init_db.py` — seeds categories in correct order (parents first, children second)
- `app/i18n/en.py` — EN translations for all 81 category labels (19 parents + 62 children)
- `app/i18n/pl.py` — PL translations for all 81 category labels

---

## Review Steps

1. Confirm diff scope is limited to `seed/categories.sql`, `db/init_db.py`, `app/i18n/en.py`, and `app/i18n/pl.py`.
2. Verify parent groups have `parent_id = NULL`.
3. Verify subcategories have `parent_id` referencing a valid parent row.
4. Verify **exactly 7 Cash In parent groups** with slugs: `ci_services`, `ci_training`, `ci_products`, `ci_commissions`, `ci_consulting`, `ci_financial`, `ci_other`.
5. Verify **exactly 12 Cash Out parent groups** with slugs: `co_marketing`, `co_operations`, `co_people`, `co_taxes`, `co_services`, `co_financial`, `co_inventory`, `co_capex`, `co_training_int`, `co_training_del`, `co_private`, `co_other`.
6. Verify **exactly 20 Cash In subcategories** with slugs matching `category-taxonomy.md`.
7. Verify **exactly 42 Cash Out subcategories** with slugs matching `category-taxonomy.md`.
8. Verify parent rows have `default_vat_rate = NULL` and `default_vat_deductible_pct = NULL`.
9. Verify Cash In subcategories have `default_vat_deductible_pct = NULL` (no deductible on income).
10. Spot-check VAT rates against taxonomy:
    - `co_training_int_hotel` → 8%
    - `co_training_int_food` → 8%
    - `co_training_del_food` → 8%
    - `co_operations_transport` → 23% with 50% deductible
    - `co_people_salaries` → 0%
    - `co_taxes_vat` → 0%
    - `ci_financial_loan_taken` → 0%
    - `ci_services_test` → 23%
11. Verify all slugs are globally unique (no duplicates across cash_in and cash_out).
12. Verify `db/init_db.py` seeds parents before children (foreign key order).
13. Verify EN labels exist for all parent and child categories in `app/i18n/en.py`.
14. Verify PL labels exist for all parent and child categories in `app/i18n/pl.py`.
15. Verify no application code, routes, templates, or tests were modified.
16. Run:

```bash
python db/init_db.py
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

Files modified outside `seed/categories.sql`, `db/init_db.py`, `app/i18n/en.py`, `app/i18n/pl.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] 7 Cash In parent groups with correct slugs
- [PASS|FAIL] 12 Cash Out parent groups with correct slugs
- [PASS|FAIL] 20 Cash In subcategories with correct slugs
- [PASS|FAIL] 42 Cash Out subcategories with correct slugs
- [PASS|FAIL] parent rows have NULL VAT defaults
- [PASS|FAIL] Cash In subcategories have NULL deductible pct
- [PASS|FAIL] 8% VAT on hotel and food/catering categories
- [PASS|FAIL] 50% deductible on transport/petrol
- [PASS|FAIL] 0% VAT on all tax/payroll/financial categories
- [PASS|FAIL] all slugs globally unique
- [PASS|FAIL] `init_db.py` seeds parents before children
- [PASS|FAIL] EN translations present for all 81 labels
- [PASS|FAIL] PL translations present for all 81 labels
- [PASS|FAIL] no routes/services/templates/tests modified
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

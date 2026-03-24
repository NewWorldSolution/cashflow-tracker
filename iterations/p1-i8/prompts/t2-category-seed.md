# I8-T2 — Category Seed + Hierarchy + i18n

**Branch:** `feature/p1-i8/t2-category-seed`
**Base:** `feature/phase-1/iteration-8` (after T1 merged)
**Depends on:** I8-T1

---

## Goal

Seed the full two-level category taxonomy (19 parent groups, 62 subcategories) with all VAT defaults, and add EN + PL translations for every category label. After this task, the database has the complete hierarchy and the i18n system can display all category names in both languages.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md
iterations/p1-i8/category-taxonomy.md   ← PRIMARY SOURCE for all seed data
seed/categories.sql
db/init_db.py
app/i18n/en.py
app/i18n/pl.py
```

---

## Deliverables

### 1. Seed parent groups in `seed/categories.sql`

Insert 19 parent group rows with:
- `parent_id = NULL` (these are top-level groups)
- `direction` = `cash_in` or `cash_out`
- `name` = slug from taxonomy (e.g., `ci_services`, `co_marketing`)
- `label` = English display name (e.g., "Services", "Marketing")
- `default_vat_rate = NULL` — parent rows do NOT carry VAT defaults
- `default_vat_deductible_pct = NULL` — same

**Cash In parents (7):** `ci_services`, `ci_training`, `ci_products`, `ci_commissions`, `ci_consulting`, `ci_financial`, `ci_other`

**Cash Out parents (12):** `co_marketing`, `co_operations`, `co_people`, `co_taxes`, `co_services`, `co_financial`, `co_inventory`, `co_capex`, `co_training_int`, `co_training_del`, `co_private`, `co_other`

### 2. Seed subcategories (leaf nodes) in `seed/categories.sql`

Insert 62 subcategory rows with:
- `parent_id` = FK to the parent group's `category_id`
- `direction` = same as parent
- `name` = slug from taxonomy (e.g., `ci_services_test`, `co_marketing_paid_ads`)
- `label` = English display name
- `default_vat_rate` = from taxonomy (23, 8, 5, or 0)
- `default_vat_deductible_pct` = from taxonomy (cash_out only; NULL for cash_in)

**Use exact slugs, VAT rates, and deductible percentages from `category-taxonomy.md`.**

### 3. Update `db/init_db.py`

- Ensure init_db.py seeds categories in the correct order: parents first, then children
- Parent IDs must be resolved correctly (use INSERT with known IDs, or query-after-insert)
- Verify the seeding is idempotent (safe to run multiple times on a fresh DB)

### 4. Add i18n translations

Add translations for all category labels to both `app/i18n/en.py` and `app/i18n/pl.py`.

Use a single consistent key convention for all categories: `cat_{slug}` (e.g., `cat_ci_services`, `cat_co_marketing_paid_ads`). Parent groups use the same pattern as children — `cat_ci_services`, `cat_co_marketing`, etc. Do not introduce a separate `cat_group_` prefix; that creates two lookup schemes where one is sufficient.

**English labels** — use the display names from `category-taxonomy.md` directly.

**Polish labels** — translate each category name to Polish. Examples:
- Services → Usługi
- Training → Szkolenia
- Product Sales → Sprzedaż produktów
- Marketing → Marketing
- Operations → Działalność operacyjna
- People Costs → Koszty osobowe
- Financial → Finansowe
- etc.

---

## Important Rules

- **Use exact data from `category-taxonomy.md`** — do not invent or modify slugs, VAT rates, or deductible percentages.
- **No VAT inheritance** — leaf rows store their own VAT defaults. Parent rows have NULL for VAT fields.
- **Only leaf nodes will be selectable** in the UI (enforced in later tasks).
- **Cash In categories have no `vat_deductible_pct`** — that field is NULL for all cash_in subcategories.
- **Slugs are globally unique** across both directions.
- **category_id values** — use explicit IDs if possible for predictability. Parents could use IDs 1-19, children could start from 101. Or use AUTOINCREMENT and resolve parent references by slug. Choose whichever approach keeps the SQL readable.

---

## Allowed Files

```text
seed/categories.sql
db/init_db.py
app/i18n/en.py
app/i18n/pl.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] 19 parent group rows inserted with correct slugs and directions
- [ ] 62 subcategory rows inserted with correct parent_id, slugs, VAT defaults, and deductible percentages
- [ ] All VAT defaults match `category-taxonomy.md` exactly
- [ ] Cash In subcategories have `default_vat_deductible_pct = NULL`
- [ ] Parent groups have `default_vat_rate = NULL` and `default_vat_deductible_pct = NULL`
- [ ] `init_db.py` runs cleanly and seeds all categories
- [ ] EN translations added for all 81 category labels (19 parents + 62 children)
- [ ] PL translations added for all 81 category labels
- [ ] `ruff check .` passes
- [ ] Application starts and categories are queryable

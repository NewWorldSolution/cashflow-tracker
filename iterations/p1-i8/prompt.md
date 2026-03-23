# cashflow-tracker Task Prompt — P1-I8: Sub-Categories (Hierarchical Category System)

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/ → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — computed at query time only |
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
| Title | Sub-Categories (Hierarchical Category System) |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 8 |
| Feature branch | `feature/phase-1/iteration-8` |
| Depends on | P1-I7 (multi-company + accountant flag — all merged to main) |
| Blocks | P1-I9 (Azure deployment) |
| PR scope | Task branches PR into `feature/phase-1/iteration-8`. The iteration branch PRs into `main` after QA. |

---

## Task Goal

Introduce a two-level category system (parent + sub-category) so transactions can be classified more precisely. The current flat list of 22 categories becomes a hierarchical structure where parent categories group related sub-categories.

After I8, the create/correct forms use a two-level category picker, list/detail views show category paths, and all existing transactions remain valid with their current categories.

**Important:** The initial implementation uses a **placeholder/demo taxonomy**. The real business taxonomy will come from user testing feedback later. This iteration builds the structure and UI — not the final data.

**Execution model:** 5 task branches, each with its own prompt file in `iterations/p1-i8/prompts/`. This file is the full reference; task prompt files are the execution guides.

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md          (I8 section)
```

### Task-specific

| Task | Also read |
|------|-----------|
| I8-T1 | `db/schema.sql`, `db/init_db.py`, `seed/categories.sql` |
| I8-T2 | `app/services/validation.py`, `app/services/transaction_service.py` |
| I8-T3 | `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js` |
| I8-T4 | `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/templates/dashboard.html` |
| I8-T5 | `tests/test_transactions.py` |

---

## Category Hierarchy Design

### Schema change

Add `parent_id` to the existing `categories` table:

```sql
ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id);
```

- `parent_id = NULL` → top-level (parent) category
- `parent_id = <id>` → sub-category of that parent
- Maximum depth: **2 levels only** (parent → child). No deeper nesting.

### Current categories (22 flat)

**Income (4):** `salary_income`, `service_income`, `other_income`, `internal_transfer_in`
**Expense (18):** `rent`, `utilities`, `office_supplies`, `fuel`, `vehicle_maintenance`, `insurance`, `accounting_fees`, `legal_fees`, `marketing`, `software_subscriptions`, `hardware`, `phone_internet`, `meals_entertainment`, `travel`, `bank_fees`, `card_terminal_fees`, `other_expense`, `internal_transfer_out`

### Migration strategy

1. Some current categories become **parents** (grouping categories)
2. Some current categories become **children** under those parents
3. Some current categories remain **standalone** (both parent and selectable)
4. **Existing transactions keep their current `category_id`** — the FK remains valid because the category row still exists; it just now has a `parent_id` set

**Design decision for T1:** Whether parent categories are selectable or only leaf nodes. Recommendation: **only leaf nodes are selectable** in the picker — parent categories serve as grouping labels only. If a current category becomes a parent, it must either:
- Remain selectable (exception to leaf-only rule), OR
- Have its existing transactions migrated to a new "General" sub-category underneath it

### Placeholder taxonomy example

This is a **starting point** — the real taxonomy comes from user testing:

```
Income
├── Salary / Wages          (salary_income)
├── Service Revenue         (service_income)
├── Other Income            (other_income)
└── Internal Transfer In    (internal_transfer_in)

Operating Expenses
├── Rent                    (rent)
├── Utilities               (utilities)
├── Office Supplies         (office_supplies)
└── Accounting Fees         (accounting_fees)

Vehicle & Transport
├── Fuel                    (fuel)
├── Vehicle Maintenance     (vehicle_maintenance)
└── Travel                  (travel)

Professional Services
├── Legal Fees              (legal_fees)
├── Insurance               (insurance)
└── Marketing               (marketing)

Technology
├── Software Subscriptions  (software_subscriptions)
├── Hardware                (hardware)
└── Phone & Internet        (phone_internet)

Financial
├── Bank Fees               (bank_fees)
├── Card Terminal Fees      (card_terminal_fees)
└── Internal Transfer Out   (internal_transfer_out)

Other
├── Meals & Entertainment   (meals_entertainment)
└── Other Expense           (other_expense)
```

### VAT defaults in hierarchy

- Sub-categories **inherit** VAT defaults from the parent if not overridden
- Sub-categories **can override** with their own `default_vat_rate` and `default_vat_deductible_pct`
- The picker UI shows the effective default (own or inherited)

---

## Two-Level Picker UI

### Behavior

1. **First dropdown:** Select parent category (groups)
2. **Second dropdown:** Populates with children of selected parent
3. **Category auto-defaults:** When sub-category is selected, auto-fill VAT rate and deductibility (same behavior as current single-level picker)
4. **Form submission:** Only the sub-category `category_id` is submitted (the leaf node)
5. **Correction flow:** Pre-selects both parent and child from the existing transaction's category

### Implementation

- Vanilla JS only — cascading dropdowns
- Category hierarchy data passed from route to template (or embedded as JSON in page)
- No API calls for the cascade — all data available on page load
- Works with existing `form.js` auto-default logic

---

## Allowed Files

```
db/schema.sql                                  ← modify (categories.parent_id)
db/init_db.py                                  ← modify (migration + hierarchy seed)
seed/categories.sql                            ← modify (add parent_id, restructure)
app/services/validation.py                     ← modify (hierarchy-aware category validation)
app/services/transaction_service.py            ← modify (category path queries)
app/routes/transactions.py                     ← modify (two-level picker data, category path)
app/routes/dashboard.py                        ← modify (if category display changes)
app/templates/transactions/create.html         ← modify (two-level picker)
app/templates/transactions/list.html           ← modify (category path display)
app/templates/transactions/detail.html         ← modify (category path display)
app/templates/dashboard.html                   ← modify (category display if needed)
app/i18n/en.py                                 ← extend (parent category labels)
app/i18n/pl.py                                 ← extend (parent category labels)
static/form.js                                 ← modify (cascading picker behavior)
tests/test_transactions.py                     ← extend (hierarchy tests)
iterations/p1-i8/tasks.md                      ← status updates only
```

---

## Deliverables by Task

### T1 — Schema + Migration + Seed

**Goal:** `parent_id` column exists on categories, placeholder hierarchy is seeded, existing transactions remain valid.

- `parent_id` column added to `categories` table in `db/schema.sql`
- Migration in `db/init_db.py` — idempotent: add column, restructure seed data into hierarchy
- `seed/categories.sql` updated with parent-child relationships
- Design decision documented: leaf-only selection vs parent selectable
- Existing transactions' `category_id` FKs remain valid after migration
- VAT default inheritance logic defined

### T2 — Services + Validation

**Goal:** Validation and query services understand category hierarchy.

- `validation.py` updated: validate that submitted `category_id` is a valid leaf category (or selectable category per T1 decision)
- `transaction_service.py` updated: queries return category path (parent name + child name)
- Category hierarchy query helper: returns structured parent→children data for the picker
- `other_expense` / `other_income` description requirement still enforced regardless of hierarchy level

### T3 — Two-Level Category Picker UI

**Goal:** Create and correct forms use a cascading two-level category picker.

- Parent category dropdown (first level)
- Sub-category dropdown (second level — populates on parent selection)
- Category auto-defaults (VAT rate, deductibility) triggered on sub-category selection
- Correction flow pre-selects both levels from existing transaction
- Category hierarchy data embedded in page (no API calls)
- `form.js` updated for cascading behavior
- Works with existing income/expense direction toggling

### T4 — List/Detail Category Path Display

**Goal:** Category hierarchy visible in all transaction views.

- List view shows category as "Parent > Child" or similar path format
- Detail view shows full category path
- Dashboard recent transactions show category path
- i18n labels for all new parent category names in EN + PL

### T5 — Tests

**Goal:** Full test coverage for hierarchical category system.

- Category hierarchy seed validation
- Two-level picker selection (valid leaf, invalid parent-only if leaf-only enforced)
- Category auto-defaults with hierarchy
- Correction preserves category through hierarchy
- Migration correctness — existing transactions still valid
- Category path display in list/detail
- `other_expense` / `other_income` description requirement still works

---

## What Must NOT Change

- Auth model — same 3-user session-based auth
- VAT calculation formulas — no modifications
- Soft-delete behavior — no changes
- Existing transaction data integrity — migration must preserve all FKs
- Route paths for existing functionality — no breaking changes
- Company support from I7 — no regression
- All existing tests must continue to pass

---

## Acceptance Checklist

```bash
pytest -v
# Expected: all existing + new tests pass
ruff check .
# Expected: clean
```

- [ ] `parent_id` column exists on categories table
- [ ] Placeholder hierarchy seeded (parent categories + children)
- [ ] Existing transactions remain valid after migration
- [ ] Two-level picker works in create form
- [ ] Two-level picker works in correct form (pre-selected)
- [ ] Only valid categories can be submitted (leaf-only if decided)
- [ ] Category auto-defaults work with hierarchy
- [ ] Category path displayed in list view
- [ ] Category path displayed in detail view
- [ ] `other_expense` / `other_income` description rule still enforced
- [ ] VAT defaults inherited or overridden correctly
- [ ] EN + PL translations for all new parent category labels
- [ ] All existing tests pass
- [ ] New tests cover hierarchy flows
- [ ] ruff clean
- [ ] No multi-currency work (explicitly deferred)

---

## Agent Rules

1. Read this file first.
2. Read your task prompt file: `iterations/p1-i8/prompts/t[N]-[name].md`
3. Update status to IN PROGRESS before writing any code.
4. Check dependencies — never start if dep is not DONE.
5. Verify acceptance checklist before requesting review.
6. After PR is merged: update `tasks.md` status → DONE with one-line note.
7. No LLM calls in any logic layer.
8. Default locale is `pl` (Polish) — English is the fallback, not the default.
9. All new UI labels must have both EN and PL translations.
10. Test with both locales before marking done.
11. Existing transactions must remain valid — never break FK references during migration.
12. Maximum category depth is 2 levels — do not implement deeper nesting.

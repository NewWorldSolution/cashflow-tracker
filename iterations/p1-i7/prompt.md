# cashflow-tracker Task Prompt — P1-I7: Multi-Company Support + Accountant Flag

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```text
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

- **Iteration branch:** `feature/phase-1/iteration-7`
- **Base branch when I7 starts:** `main` after P1-I6 is merged
- **Current test baseline:** verify on `main` when I7 begins
- **Ruff:** clean
- **Prerequisite iteration:** P1-I6 — multi-language foundation + Polish UI must be complete before I7 starts
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I7 |
| Title | Multi-Company Support + Accountant Flag |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 7 |
| Feature branch | `feature/phase-1/iteration-7` |
| Depends on | P1-I6 (i18n + Polish UI — all merged to main) |
| Blocks | P1-I8 (sub-categories) |
| PR scope | Task branches PR into `feature/phase-1/iteration-7`. The iteration branch PRs into `main` after QA. |

---

## Task Goal

Support multiple legal/business entities inside one app so transactions, views, and summaries can be separated by company. Also add the `for_accountant` flag to mark transactions that need accountant attention.

After I7:

- every transaction is associated with a company
- users can filter list/dashboard views by company
- company display uses i18n-backed short/full labels
- `for_accountant` is available on create/correct flows
- `for_accountant` is visible as a normal field in list/detail views

**Execution model:** 5 task branches, each with its own prompt file in `iterations/p1-i7/prompts/`. This file is the full reference; task prompt files are the execution guides.

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```text
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md          (I7 section)
```

### Task-specific

| Task | Also read |
|------|-----------|
| I7-T1 | `db/schema.sql`, `db/init_db.py`, `seed/categories.sql`, `seed/users.sql` |
| I7-T2 | `app/routes/transactions.py`, `app/templates/transactions/create.html`, `app/services/validation.py` |
| I7-T3 | `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/templates/dashboard.html`, `app/routes/dashboard.py` |
| I7-T4 | `db/schema.sql`, `app/routes/transactions.py`, `app/templates/transactions/create.html`, `app/templates/transactions/list.html`, `app/templates/transactions/detail.html` |
| I7-T5 | `tests/test_transactions.py`, `tests/test_init_db.py` |

---

## Companies

### Initial seed data

| ID | Name | Slug | EN short | EN full | PL short | PL full |
|----|------|------|----------|---------|----------|---------|
| 1 | `sp` | `sp` | SP | Sole Proprietorship (SP) | JDG | Jednoosobowa działalność gospodarcza (JDG) |
| 2 | `ltd` | `ltd` | LTD | Limited Company (LTD) | Sp. z o.o. | Spółka z ograniczoną odpowiedzialnością (Sp. z o.o.) |
| 3 | `ff` | `ff` | FF | Family Foundation (FF) | FR | Fundacja rodzinna (FR) |
| 4 | `private` | `private` | P | Private (P) | P | Prywatny (P) |

### Schema

```sql
CREATE TABLE IF NOT EXISTS companies (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE,
    slug      TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
```

### Display Rules

- Database stores language-neutral keys only: `sp`, `ltd`, `ff`, `private`
- Short labels are used in list view, filters, and form selectors:
  - `t('company_' + company.name)`
- Full labels are used in transaction detail:
  - `t('company_' + company.name + '_full')`
- Do not hardcode user-facing company names in templates or seed descriptions

### Transaction FK

Add to `transactions` table:

```sql
company_id INTEGER NOT NULL REFERENCES companies(id)
```

**Migration:** Existing transactions must be backfilled to default company `id = 1` (`sp`). The migration must be idempotent.

---

## for_accountant Flag

### Schema

Add to `transactions` table:

```sql
for_accountant BOOLEAN NOT NULL DEFAULT FALSE
```

### Behavior

- Simple boolean in the schema
- Available on create and correct forms as a checkbox
- Always shown in detail view as a Yes/No field
- Shown in list view as an always-visible Yes/No column
- There is **no standalone toggle/edit flow**
- Changing the flag after creation happens through the existing correction flow
- Default is `FALSE`

---

## List / Detail UX Changes

- Transaction list adds **Company** and **For accountant** columns
- Transaction list removes **Logged by**
- Transaction detail keeps **Logged by**
- Company in list/filter/form uses short translated labels
- Company in detail uses full translated labels
- `for_accountant` in list/detail uses translated Yes/No values

---

## Allowed Files

```text
db/schema.sql                                  ← modify (companies table, transactions.company_id, for_accountant)
db/init_db.py                                  ← modify (migration + backfill)
seed/companies.sql                             ← create new (4 companies)
app/services/validation.py                     ← modify (company_id validation)
app/services/transaction_service.py            ← modify (company-aware queries)
app/routes/transactions.py                     ← modify (company selector, filtering, for_accountant)
app/routes/dashboard.py                        ← modify (company-specific summaries)
app/templates/transactions/create.html         ← modify (company selector, for_accountant checkbox)
app/templates/transactions/list.html           ← modify (company display, for_accountant, remove logged_by)
app/templates/transactions/detail.html         ← modify (company display, for_accountant)
app/templates/transactions/void.html           ← modify (company in summary if needed)
app/templates/dashboard.html                   ← modify (company filter, summaries)
app/templates/base.html                        ← modify (company selector in nav if needed)
app/i18n/en.py                                 ← extend (company + accountant labels)
app/i18n/pl.py                                 ← extend (company + accountant labels)
app/main.py                                    ← modify (if company middleware needed)
static/form.js                                 ← modify (if company selection affects form behavior)
tests/test_transactions.py                     ← extend (company + accountant tests)
tests/test_init_db.py                          ← extend (migration/backfill tests)
iterations/p1-i7/tasks.md                      ← status updates only
```

---

## Deliverables by Task

### T1 — Companies Schema + Seed + Migration

**Goal:** `companies` table exists, 4 companies seeded with neutral keys, transactions have `company_id` FK and `for_accountant` boolean, existing data backfilled.

- `companies` table in `db/schema.sql`
- `seed/companies.sql` with `sp`, `ltd`, `ff`, `private`
- `company_id` FK on transactions
- `for_accountant BOOLEAN NOT NULL DEFAULT FALSE` on transactions
- migration in `db/init_db.py` is idempotent
- existing transactions backfilled to company `id = 1` (`sp`)

### T2 — Create/Correct with Company

**Goal:** Transaction create and correct flows include company selection and `for_accountant` input.

- company selector dropdown in create/correct form
- selector uses short translated labels
- `for_accountant` checkbox in create/correct forms
- company and `for_accountant` passed to validation and persisted
- `validation.py` updated to validate `company_id`
- no standalone edit action for `for_accountant`

### T3 — List/Detail/Dashboard + Company Display & Filtering

**Goal:** Company visible in all transaction views, filterable in list and dashboard.

- company displayed in transaction list using short label
- company displayed in transaction detail using full label
- company displayed in dashboard/filter UI using short label
- company filter in list and dashboard views
- dashboard summaries support company filtering
- transaction list removes `Logged by`

### T4 — for_accountant Display & Behavior

**Goal:** `for_accountant` visible as a normal transaction field, without adding a separate edit workflow.

- list view shows always-visible Yes/No column
- detail view always shows Yes/No row
- translations exist for label + Yes/No values
- no standalone toggle/edit action exists
- changing the flag is done via correction flow

### T5 — Tests

**Goal:** Full test coverage for company and `for_accountant` features.

- transaction create with `company_id` — valid and invalid
- transaction create with `for_accountant`
- company filter in list/dashboard
- correction preserves or updates company
- correction can change `for_accountant`
- migration/backfill correctness
- detail/list rendering expectations for company and `for_accountant`

---

## What Must NOT Change

- Auth model — same 3-user session-based auth
- VAT calculation formulas — no modifications
- Soft-delete behavior — no changes
- Existing transaction data integrity — backfill only, never delete
- Route paths for existing functionality — no breaking changes
- All existing tests must continue to pass

---

## Acceptance Checklist

```bash
pytest -v
ruff check .
```

- [ ] `companies` table exists with 4 seeded companies using keys `sp`, `ltd`, `ff`, `private`
- [ ] `company_id` FK on all transactions — mandatory, backfilled for existing rows
- [ ] Existing transactions backfilled to company `id = 1` (`sp`)
- [ ] Company selector in create/correct forms
- [ ] Short company labels used in list/filter/form UI
- [ ] Full company labels used in detail UI
- [ ] Company filter works in list and dashboard
- [ ] `for_accountant` boolean on transactions — default FALSE
- [ ] `for_accountant` checkbox in create/correct forms
- [ ] `for_accountant` displayed as Yes/No in list
- [ ] `for_accountant` displayed as Yes/No in detail
- [ ] No standalone toggle/edit action for `for_accountant`
- [ ] `Logged by` removed from transaction list and retained in detail
- [ ] EN + PL translations for all new labels
- [ ] All existing tests pass
- [ ] New tests cover company + accountant flows
- [ ] ruff clean
- [ ] No multi-currency work (explicitly deferred)

---

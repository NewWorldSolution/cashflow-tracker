# QA Review — P1-I7: Multi-Company Support + Accountant Flag
**Reviewer:** QA agent
**Branch:** `feature/phase-1/iteration-7`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i7/tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 7. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What this iteration was supposed to deliver

1. `companies` table exists with 4 seeded language-neutral companies: `sp`, `ltd`, `ff`, `private`
2. Transactions have mandatory `company_id` FK
3. Existing transactions are backfilled to default company `id = 1` (`sp`)
4. Transactions have `for_accountant BOOLEAN NOT NULL DEFAULT FALSE`
5. Create and correct flows include company selection
6. Create and correct flows include `for_accountant` checkbox
7. Short company labels are used in list/filter/form UI
8. Full company labels are used in transaction detail
9. Company filtering works in list and dashboard views
10. Transaction list removes `Logged by`
11. `for_accountant` is visible as always-visible Yes/No in list/detail
12. No standalone toggle/edit flow exists for `for_accountant`
13. EN + PL translations exist for company/accountant UI
14. Full test coverage exists for company and accountant flows

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-7
git pull origin feature/phase-1/iteration-7
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
seed/companies.sql
app/services/validation.py
app/services/transaction_service.py
app/routes/transactions.py
app/routes/dashboard.py
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
app/templates/dashboard.html
app/templates/base.html
app/i18n/en.py
app/i18n/pl.py
app/main.py
static/style.css
static/form.js
tests/test_transactions.py
tests/test_init_db.py
```

Iteration planning/docs files may also appear in the diff; this is expected:

```text
iterations/p1-i7/prompt.md
iterations/p1-i7/tasks.md
iterations/p1-i7/prompts/*.md
iterations/p1-i7/reviews/*.md
```

Frozen areas that should not change unless explicitly justified by the merged task branches:

```text
app/services/calculations.py
app/services/auth_service.py
seed/categories.sql
seed/users.sql
tests/test_validation.py
tests/test_calculations.py
```

### Step 4 — Architecture checks

Verify by code inspection:

- [ ] No hard deletes introduced
- [ ] No VAT/net/effective-cost derived values started being stored
- [ ] `logged_by` / `voided_by` remain integer user FKs
- [ ] Validation remains in the service layer
- [ ] Company/accountant support does not alter auth behavior or route paths unexpectedly
- [ ] No standalone toggle/edit flow exists for `for_accountant`

### Step 5 — Schema and migration checks

Verify by code inspection:

- [ ] `companies` table exists with `id`, `name`, `slug`, `is_active`
- [ ] `seed/companies.sql` inserts `sp`, `ltd`, `ff`, `private`
- [ ] `transactions.company_id` exists and is mandatory
- [ ] `transactions.for_accountant` exists, boolean, default FALSE
- [ ] migration is idempotent for existing databases
- [ ] existing transactions are backfilled to company `id = 1` (`sp`)

### Step 6 — UI and query checks

Verify by code inspection and, if needed, manual app run:

- [ ] create form has company selector
- [ ] create/correct flows persist company correctly
- [ ] create/correct flows persist `for_accountant` correctly
- [ ] merged iteration branch resolves the T2/T4 overlap in `app/templates/transactions/create.html` cleanly
- [ ] list view displays company using short translated labels
- [ ] detail view displays company using full translated labels
- [ ] dashboard/filter UI uses short translated company labels
- [ ] list filter by company works
- [ ] dashboard filter by company works
- [ ] list view displays always-visible accountant Yes/No
- [ ] detail view displays always-visible accountant Yes/No
- [ ] `Logged by` removed from transaction list
- [ ] `Logged by` retained in detail

### Step 7 — Translation checks

Verify by reading `app/i18n/en.py` and `app/i18n/pl.py`:

- [ ] short company keys exist for `sp`, `ltd`, `ff`, `private`
- [ ] full company keys exist for `sp`, `ltd`, `ff`, `private`
- [ ] accountant field label exists in both locales
- [ ] accountant Yes/No values exist in both locales
- [ ] translations are consistent and professional

### Step 8 — Test coverage checks

Verify `tests/test_transactions.py` and `tests/test_init_db.py` include coverage for:

- [ ] valid `company_id` create flow
- [ ] invalid or missing `company_id`
- [ ] `for_accountant = true` create flow
- [ ] company filtering
- [ ] correction preserving/updating company
- [ ] correction preserving/updating `for_accountant`
- [ ] migration/backfill expectations
- [ ] short/full company label rendering expectations
- [ ] accountant Yes/No rendering expectations
- [ ] `Logged by` removed from list

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
- [PASS|FAIL] `companies` table exists with required columns
- [PASS|FAIL] 4 companies seeded correctly as `sp`, `ltd`, `ff`, `private`
- [PASS|FAIL] `transactions.company_id` exists and is mandatory
- [PASS|FAIL] existing transactions backfilled to company `id = 1` (`sp`)
- [PASS|FAIL] `transactions.for_accountant` exists with default FALSE
- [PASS|FAIL] create/correct flows include company selection
- [PASS|FAIL] create/correct flows include `for_accountant` checkbox
- [PASS|FAIL] short company labels used in list/filter/form UI
- [PASS|FAIL] full company labels used in detail UI
- [PASS|FAIL] merged iteration branch resolves T2/T4 overlap in `create.html`
- [PASS|FAIL] company filtering works in list and dashboard
- [PASS|FAIL] `Logged by` removed from list and retained in detail
- [PASS|FAIL] `for_accountant` displayed as always-visible Yes/No in list/detail
- [PASS|FAIL] no standalone toggle/edit flow exists for `for_accountant`
- [PASS|FAIL] EN + PL translations added for company/accountant UI
- [PASS|FAIL] tests cover company + accountant flows
- [PASS|FAIL] frozen files remain unchanged or justified

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

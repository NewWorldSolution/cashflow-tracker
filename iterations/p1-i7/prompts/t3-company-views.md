# I7-T3 — List/Detail/Dashboard + Company Filtering

**Branch:** `feature/p1-i7/t3-company-views` (from `feature/phase-1/iteration-7`)
**Worktree:** `../cashflow-tracker-t3`
**PR target:** `feature/phase-1/iteration-7`
**Depends on:** I7-T2 ✅ DONE

---

## Goal

Display company throughout the app and add company filtering to list/dashboard views.

After T3:

- list uses short company labels
- detail uses full company labels
- dashboard/filter UI uses short company labels
- transaction list no longer shows `Logged by`

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i7/tasks.md
iterations/p1-i7/prompt.md
app/routes/transactions.py
app/routes/dashboard.py
app/services/transaction_service.py
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/dashboard.html
app/i18n/en.py
app/i18n/pl.py
```

---

## Allowed Files

```text
app/services/transaction_service.py
app/routes/transactions.py
app/routes/dashboard.py
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/dashboard.html
app/i18n/en.py
app/i18n/pl.py
static/style.css
```

Do NOT modify schema/init/validation/create-form logic/tests in this task.

---

## What to Implement

### 1. Query Support

Update list/detail/dashboard queries to fetch company information needed for display and filtering.

The UI should have access to:

- company id
- company name key (`sp`, `ltd`, `ff`, `private`)
- any other field needed for stable filter rendering

### 2. List View

Update `app/templates/transactions/list.html` and supporting route logic:

- add company filter UI
- display company with short translated label:
  - `t('company_' ~ txn.company_name)`
- remove `Logged by` column from the transaction list

### 3. Detail View

Update `app/templates/transactions/detail.html`:

- display company with full translated label:
  - `t('company_' ~ txn.company_name ~ '_full')`

### 4. Dashboard

Update dashboard route/template:

- add company filter
- apply company filter to relevant summary/recent queries
- use short translated company labels in the filter UI and recent transaction display

### 5. i18n

Add EN + PL keys for:

- company column labels
- company filter labels
- short company labels
- full company labels

Required company keys:

- `company_sp`
- `company_sp_full`
- `company_ltd`
- `company_ltd_full`
- `company_ff`
- `company_ff_full`
- `company_private`
- `company_private_full`

---

## Acceptance Check

```bash
ruff check .
pytest -v
```

- [ ] transaction list displays company using short translated labels
- [ ] transaction detail displays company using full translated labels
- [ ] dashboard uses short translated labels for company UI
- [ ] list has working company filter
- [ ] dashboard has working company filter
- [ ] selected company is preserved in filter UI
- [ ] `Logged by` column removed from transaction list
- [ ] `Logged by` remains available in detail view
- [ ] EN + PL company translation keys added
- [ ] pytest passes
- [ ] ruff clean

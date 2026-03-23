# I7-T2 — Create/Correct with Company

**Branch:** `feature/p1-i7/t2-company-create` (from `feature/phase-1/iteration-7`)
**Worktree:** `../cashflow-tracker-t2`
**PR target:** `feature/phase-1/iteration-7`
**Depends on:** I7-T1 ✅ DONE

---

## Goal

Add company selection to the transaction create/correct flows and include the `for_accountant` checkbox in those forms.

After T2:

- every new transaction includes `company_id`
- create/correct forms include `for_accountant`
- company selector uses short translated labels
- changing `for_accountant` after creation happens only through the existing correction flow

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i7/tasks.md
iterations/p1-i7/prompt.md
app/routes/transactions.py
app/services/validation.py
app/templates/transactions/create.html
app/i18n/en.py
app/i18n/pl.py
```

---

## Allowed Files

```text
app/routes/transactions.py
app/services/validation.py
app/templates/transactions/create.html
app/i18n/en.py
app/i18n/pl.py
```

Do NOT modify schema, init, list/detail/dashboard templates, or tests in this task.

---

## What to Implement

### 1. Validation

Update `app/services/validation.py` to validate `company_id`:

- required
- integer
- valid active company

Validation errors must be explicit and translatable.

### 2. Create/Correct Routes

Update `app/routes/transactions.py` so create and correct flows:

- fetch active companies for form rendering
- accept `company_id`
- accept `for_accountant`
- persist both values on create and correction insert
- preserve submitted values on validation failure

Do not build any dedicated route/action for changing only `for_accountant`.

### 3. Create Template

Update `app/templates/transactions/create.html`:

- add mandatory company selector
- use short translated labels in the selector:
  - `t('company_' ~ company.name)`
- add `for_accountant` checkbox
- preserve values for both normal create and correction flows

### 4. i18n

Add EN + PL keys needed for:

- company form label
- company validation errors
- accountant checkbox label

Use the established i18n pattern. Do not hardcode user-facing company names in the template.

---

## Acceptance Check

```bash
ruff check .
pytest -v
```

- [ ] company selector appears on create form
- [ ] company selector appears on correction form
- [ ] company selector uses short translated labels
- [ ] company is required
- [ ] invalid/inactive company IDs are rejected
- [ ] `company_id` is saved on create
- [ ] `company_id` is saved on correction
- [ ] `for_accountant` checkbox appears on create/correct form
- [ ] `for_accountant` is persisted on create/correction insert
- [ ] no standalone toggle/edit flow for `for_accountant` is introduced
- [ ] EN + PL translations added for company/accountant form UI
- [ ] pytest passes
- [ ] ruff clean

# I7-T4 — for_accountant Flag

**Branch:** `feature/p1-i7/t4-accountant-flag` (from `feature/phase-1/iteration-7`)
**Worktree:** `../cashflow-tracker-t4`
**PR target:** `feature/phase-1/iteration-7`
**Depends on:** I7-T1 ✅ DONE

---

## Merge Warning

T4 depends on T1 because the `transactions.for_accountant` column is created in T1.

T4 also overlaps with T2/T3 in these files:

- `app/routes/transactions.py`
- `app/templates/transactions/create.html`
- `app/templates/transactions/list.html`
- `app/templates/transactions/detail.html`
- `app/i18n/en.py`
- `app/i18n/pl.py`

This task can be developed in parallel, but merged after T2/T3 or with deliberate conflict resolution.

---

## Goal

Define the final user-facing behavior for `for_accountant`.

After T4:

- create/correct forms still use a checkbox
- list always shows a Yes/No accountant column
- detail always shows a Yes/No accountant field
- there is no standalone toggle/edit action
- changing the flag uses the correction flow

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i7/tasks.md
iterations/p1-i7/prompt.md
app/routes/transactions.py
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/i18n/en.py
app/i18n/pl.py
```

---

## Allowed Files

```text
app/routes/transactions.py
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/i18n/en.py
app/i18n/pl.py
static/style.css
```

Do NOT modify schema/init files here unless you are explicitly repairing a missing T1 dependency during merge conflict resolution. Do NOT add a new route or standalone edit workflow.

---

## What to Implement

### 1. Create/Correct Flow

Keep the checkbox in create/correct form.

Requirements:

- create can set `for_accountant`
- correction can preserve or change `for_accountant`
- there is no separate “change accountant flag” action

### 2. List View

Update list template/route support so the list shows an always-visible accountant column with translated Yes/No values.

Use normal text or an intentionally simple visual treatment. Do not hide the field when false.

### 3. Detail View

Update detail template so `for_accountant` is always shown as a normal field with translated Yes/No value.

Do not render it only when true.

### 4. i18n

Add EN + PL keys needed for:

- accountant column/field label
- accountant Yes value
- accountant No value

Keep this simple. No badge/helper/toggle-specific language is needed unless the UI genuinely uses it.

---

## Acceptance Check

```bash
ruff check .
pytest -v
```

- [ ] task is implemented on top of T1 schema support
- [ ] create/correct forms still allow setting `for_accountant`
- [ ] list shows always-visible accountant Yes/No column
- [ ] detail shows always-visible accountant Yes/No field
- [ ] no standalone toggle/edit flow exists
- [ ] changing the flag happens via correction flow
- [ ] EN + PL labels exist for accountant field and Yes/No values
- [ ] pytest passes
- [ ] ruff clean

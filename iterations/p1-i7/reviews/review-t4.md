# Review — I7-T4: for_accountant Flag
**Branch:** `feature/p1-i7/t4-accountant-flag`
**PR target:** `feature/phase-1/iteration-7`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/routes/transactions.py` — final display/behavior handling for `for_accountant`
- Modified: `app/templates/transactions/create.html` — checkbox stays available in create/correct flow
- Modified: `app/templates/transactions/list.html` — always-visible accountant Yes/No column
- Modified: `app/templates/transactions/detail.html` — always-visible accountant Yes/No field
- Extended: `app/i18n/en.py` and `app/i18n/pl.py` — accountant labels and Yes/No values
- Optionally extended: `static/style.css` — accountant field presentation only

**Dependency note:** This task relies on the `transactions.for_accountant` column existing from I7-T1. Review against a branch state where T1 is already merged into `feature/phase-1/iteration-7`, or treat missing schema support as `BLOCKED`.

---

## Review steps

1. Confirm diff scope is limited to `app/routes/transactions.py`, `app/templates/transactions/create.html`, `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/i18n/en.py`, `app/i18n/pl.py`, and optionally `static/style.css` for accountant-related presentation only.
2. Verify this review is being performed against a branch state that already includes the T1 schema change for `transactions.for_accountant`; otherwise return `BLOCKED`.
3. Verify create/correct forms still allow setting `for_accountant`.
4. Verify transaction list shows an always-visible accountant column with translated Yes/No values.
5. Verify transaction detail shows an always-visible accountant field with translated Yes/No value.
6. Verify false/unset behavior is rendered explicitly as No, not hidden.
7. Verify no standalone route/action/UI was introduced to toggle only `for_accountant`.
8. Verify changing the flag after creation still happens through the correction flow.
9. Verify EN/PL labels exist for the accountant field and Yes/No values.
10. Run:

```bash
pytest -v
ruff check .
```

---

## Required output format

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
- [PASS|FAIL] T1 schema dependency is satisfied or review is marked BLOCKED
- [PASS|FAIL] create/correct forms still allow setting `for_accountant`
- [PASS|FAIL] list shows always-visible accountant Yes/No column
- [PASS|FAIL] detail shows always-visible accountant Yes/No field
- [PASS|FAIL] false/unset state is shown explicitly as No
- [PASS|FAIL] no standalone toggle/edit flow exists
- [PASS|FAIL] changing the flag happens via correction flow
- [PASS|FAIL] EN + PL labels added for accountant field and Yes/No values
- [PASS|FAIL] any `static/style.css` changes are limited to accountant presentation
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

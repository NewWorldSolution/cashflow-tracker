# Review — I7-T2: Create/Correct With Company
**Branch:** `feature/p1-i7/t2-company-create`
**PR target:** `feature/phase-1/iteration-7`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/routes/transactions.py` — create/correct flows accept and persist `company_id` and `for_accountant`
- Modified: `app/templates/transactions/create.html` — company selector and `for_accountant` checkbox in create/correct form
- Modified: `app/services/validation.py` — validate `company_id`
- Extended: `app/i18n/en.py` and `app/i18n/pl.py` — company/accountant form labels and validation strings

---

## Review steps

1. Confirm diff scope is limited to `app/routes/transactions.py`, `app/templates/transactions/create.html`, `app/services/validation.py`, `app/i18n/en.py`, and `app/i18n/pl.py`.
2. Verify the create/correct form includes a mandatory company selector.
3. Verify the company selector is populated from real companies rather than hardcoded UI-only values.
4. Verify the selector uses short translated labels derived from company keys, not raw English/Polish text stored in the DB.
5. Verify the create/correct form includes a `for_accountant` checkbox.
6. Verify create flow passes `company_id` and `for_accountant` through validation and persistence.
7. Verify correction flow preserves the original company by default or allows explicit company selection, and persists the submitted value.
8. Verify correction flow can preserve or change `for_accountant`.
9. Verify `for_accountant` submitted values survive validation failure re-render.
10. Verify `app/services/validation.py` validates `company_id` as required and as a valid active company.
11. Verify routes do not introduce any standalone action dedicated only to changing `for_accountant`.
12. Verify EN/PL labels added in `en.py` / `pl.py` cover new form labels and validation errors.
13. Run:

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
- [PASS|FAIL] create/correct form has mandatory company selector
- [PASS|FAIL] company options come from real company data
- [PASS|FAIL] selector uses short translated labels
- [PASS|FAIL] create/correct form has `for_accountant` checkbox
- [PASS|FAIL] create flow persists `company_id`
- [PASS|FAIL] create flow persists `for_accountant`
- [PASS|FAIL] correction flow preserves or updates company correctly
- [PASS|FAIL] correction flow preserves or updates `for_accountant` correctly
- [PASS|FAIL] invalid company selection surfaces explicit validation error
- [PASS|FAIL] submitted company/flag values survive validation failure re-render
- [PASS|FAIL] no standalone toggle/edit flow for `for_accountant` is introduced
- [PASS|FAIL] EN + PL labels are present
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

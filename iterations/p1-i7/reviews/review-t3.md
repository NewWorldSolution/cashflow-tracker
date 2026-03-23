# Review — I7-T3: List/Detail/Dashboard Company Display + Filtering
**Branch:** `feature/p1-i7/t3-company-views`
**PR target:** `feature/phase-1/iteration-7`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/services/transaction_service.py` — company-aware transaction queries
- Modified: `app/routes/transactions.py` — list/detail company display and list filtering
- Modified: `app/routes/dashboard.py` — company-specific summaries and recent transactions
- Modified: `app/templates/transactions/list.html` — company column/filter UI and `Logged by` removal
- Modified: `app/templates/transactions/detail.html` — company display
- Modified: `app/templates/dashboard.html` — company filter and company-aware recent transactions/summaries
- Extended: `app/i18n/en.py` and `app/i18n/pl.py` — company names and filter labels
- Optionally extended: `static/style.css` — filter/layout styling only

---

## Review steps

1. Confirm diff scope matches the allowed files only, with `static/style.css` allowed only for view/filter styling related to this task.
2. Verify transaction list queries include company information needed for display/filtering.
3. Verify transaction detail query includes company information for the selected transaction.
4. Verify dashboard queries and summary calculations respect the selected company filter.
5. Verify list view exposes a company filter and preserves the selected value in the UI.
6. Verify dashboard view exposes a company filter and preserves the selected value in the UI.
7. Verify company is shown in transaction list rows using short translated labels.
8. Verify company is shown in transaction detail using full translated labels.
9. Verify dashboard/filter UI uses short translated company labels.
10. Verify the transaction list no longer shows `Logged by`.
11. Verify `Logged by` remains available in transaction detail.
12. Verify EN/PL keys exist for:
    - `company_sp`, `company_sp_full`
    - `company_ltd`, `company_ltd_full`
    - `company_ff`, `company_ff_full`
    - `company_private`, `company_private_full`
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
- [PASS|FAIL] company data included in transaction list queries
- [PASS|FAIL] company data included in transaction detail query
- [PASS|FAIL] dashboard summaries respect selected company
- [PASS|FAIL] dashboard recent transactions respect selected company
- [PASS|FAIL] list view has working company filter UI
- [PASS|FAIL] dashboard has working company filter UI
- [PASS|FAIL] selected company is preserved in filter UI
- [PASS|FAIL] company displayed in list rows using short translated labels
- [PASS|FAIL] company displayed in detail view using full translated labels
- [PASS|FAIL] `Logged by` removed from transaction list
- [PASS|FAIL] `Logged by` retained in detail
- [PASS|FAIL] EN + PL company label keys added
- [PASS|FAIL] any `static/style.css` changes are limited to company view/filter styling
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

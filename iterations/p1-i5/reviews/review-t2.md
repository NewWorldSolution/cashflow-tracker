# Review — I5-T2: Real Dashboard
**Branch:** `feature/p1-i5/t2-dashboard`
**PR target:** `feature/phase-1/iteration-5`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Rewritten: `app/templates/dashboard.html` — summary cards, recent transactions, quick actions
- Extended: `app/routes/dashboard.py` — queries for opening balance, transaction counts, totals, recent 5

---

## Review steps

1. Confirm diff scope is only `app/templates/dashboard.html` and `app/routes/dashboard.py`.
2. Verify route queries settings table key-value pairs for `opening_balance` and `as_of_date`.
3. Verify route queries active/voided counts, income/expense totals (active only), and last 5 active transactions.
4. Verify template shows: opening balance card, summary cards, recent transactions, quick action links.
5. Verify responsive layout (grid on desktop, stack on mobile).
6. Verify empty state when no transactions.
7. Verify no business logic in template — only display.
8. Run:

```bash
pytest -v   # all 94 tests must pass
ruff check .
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/templates/dashboard.html` and `app/routes/dashboard.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] opening balance queried from settings key-value table
- [PASS|FAIL] transaction counts (active + voided) queried
- [PASS|FAIL] income/expense totals queried (active only)
- [PASS|FAIL] last 5 active transactions queried with category label
- [PASS|FAIL] dashboard renders summary cards with real data
- [PASS|FAIL] recent transactions table/list present
- [PASS|FAIL] quick action links (new transaction, view all) present
- [PASS|FAIL] responsive (stack on mobile, grid on desktop)
- [PASS|FAIL] all 94 tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

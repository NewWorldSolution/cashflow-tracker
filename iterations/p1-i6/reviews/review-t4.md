# Review — I6-T4: Locale-Aware Formatting
**Branch:** `feature/p1-i6/t4-locale-formatting`
**PR target:** `feature/phase-1/iteration-6`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Extended: `app/i18n/__init__.py` — `format_date()` and `format_amount()` functions
- Modified: `app/main.py` — register format functions as Jinja2 globals/filters
- Modified: `app/templates/transactions/list.html` — use format functions for dates and amounts
- Modified: `app/templates/transactions/detail.html` — use format functions for dates and amounts
- Modified: `app/templates/dashboard.html` — use format functions for dates and amounts

---

## Review steps

1. Confirm diff scope matches allowed files only. No changes to routes, services, JS, CSS, or tests.
2. Verify `format_date()` in `app/i18n/__init__.py`:
   - Polish: outputs `dd.mm.yyyy` format
   - English: outputs ISO `yyyy-mm-dd` format
   - Handles both date objects and string values
   - Returns `"—"` for empty/None values
3. Verify `format_amount()` in `app/i18n/__init__.py`:
   - Polish: `1 234,56` with non-breaking space (`\u00a0`) as thousands separator, comma as decimal
   - English: `1,234.56` with comma thousands, period decimal
   - Returns `"—"` for None values
   - Always 2 decimal places
4. Verify format functions are registered as Jinja2 globals or filters in `app/main.py`.
5. Verify `list.html`: date column and amount column use format functions.
6. Verify `detail.html`: date, amount, and created_at use format functions.
7. Verify `dashboard.html`: amounts in summary cards and dates in recent transactions use format functions.
8. Verify form input values are NOT formatted (date picker needs ISO, amount input needs standard decimal).
9. Verify `data-*` attributes are NOT formatted.
10. Run:

```bash
pytest -v   # all existing tests must pass (98 before T5 merges, 101 after)
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

Files modified outside allowed list.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `format_date()` — Polish `dd.mm.yyyy`, English ISO
- [PASS|FAIL] `format_date()` — handles date objects and strings
- [PASS|FAIL] `format_amount()` — Polish `1 234,56` (non-breaking space + comma)
- [PASS|FAIL] `format_amount()` — English `1,234.56`
- [PASS|FAIL] `format_amount()` — always 2 decimal places
- [PASS|FAIL] format functions registered in Jinja2
- [PASS|FAIL] list.html uses format functions for dates and amounts
- [PASS|FAIL] detail.html uses format functions for dates and amounts
- [PASS|FAIL] dashboard.html uses format functions for dates and amounts
- [PASS|FAIL] form input values remain unformatted (ISO date, standard decimal)
- [PASS|FAIL] data attributes remain unformatted
- [PASS|FAIL] all existing tests pass (98 before T5 merges, 101 after)
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

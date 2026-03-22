# Review — I5-T3: Transaction Form UX
**Branch:** `feature/p1-i5/t3-form-ux`
**PR target:** `feature/phase-1/iteration-5`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/templates/transactions/create.html` — restructured into 5 visual sections
- Modified: `static/form.js` — minimal toggle button class toggling only, no business-rule changes

---

## Review steps

1. Confirm diff scope is only `create.html` and `form.js`.
2. Verify form is organized into 5 sections: Basics, Amount, Details, VAT, Optional.
3. Verify direction uses toggle button styling with hidden radio inputs for form submission.
4. Verify error summary box at top (required). No per-field error mapping via string matching.
5. Verify card reminder styled as info callout (`.callout-info`).
6. Verify `form_action | default('/transactions/new')` preserved for correct flow.
7. Verify no business-rule changes in `form.js` — only minimal UI-state/class changes allowed (e.g., toggle button active class, adjustments for new markup structure).
8. Verify all existing JS selectors still match the new HTML structure:
   - `input[name="direction"]` radio inputs
   - `select[name="category_id"]`, `select[name="income_type"]`, etc.
   - `#income-type-row`, `#vat-deductible-row`, `#card-reminder`, `#desc-required` IDs
9. Verify page-load initialization (5b, 5c, 5d) still works with new template structure.
10. Run:

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

Files modified outside `create.html` and `form.js`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] form organized into 5 visual sections
- [PASS|FAIL] direction uses toggle buttons with hidden radios
- [PASS|FAIL] error summary box at top (no per-field string matching)
- [PASS|FAIL] card reminder as info callout
- [PASS|FAIL] form_action variable preserved
- [PASS|FAIL] form.js: no business-rule changes — only minimal UI-state/class changes
- [PASS|FAIL] all JS selectors/IDs preserved (direction radios, category select, income-type-row, etc.)
- [PASS|FAIL] gross amount helper text visible
- [PASS|FAIL] submit + cancel button hierarchy
- [PASS|FAIL] mobile responsive (single column)
- [PASS|FAIL] all 94 tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

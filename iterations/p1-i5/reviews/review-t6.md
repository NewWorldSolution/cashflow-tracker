# Review — I5-T6: UX Improvements (list tracking, form order, split view)
**Branch:** `feature/p1-i5/t6-ux-improvements`
**PR target:** `feature/phase-1/iteration-5`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/templates/transactions/list.html` — `#ID` column, "Corrected" badge, split view toggle
- Modified: `app/templates/transactions/detail.html` — bidirectional correction link
- Modified: `app/templates/transactions/create.html` — income type moved above category
- Modified: `app/routes/transactions.py` — minimal change: add reverse-correction query to detail route only (list route change only if `replacement_transaction_id` not already available)
- NOT modified: `static/form.js` — must remain untouched
- Modified: `static/style.css` — `.badge-corrected`, `.split-view`, `.split-view-col`

---

## Review steps

1. Confirm diff scope is limited to the allowed files listed above.
2. Verify `#ID` column added as first column in transaction list table.
3. Verify "Corrected" badge appears when `replacement_transaction_id` is set (in show_all mode), distinct from "Voided" badge.
4. Verify `.badge-corrected` CSS class exists in `style.css`.
5. Verify detail page shows "This is a correction of #X" callout for replacement transactions.
6. Verify the reverse query in `transactions.py` is read-only (`SELECT id FROM transactions WHERE replacement_transaction_id = ?`).
7. Verify income type field (`#income-type-row`) appears before the category/payment `.form-row` in Section 3 of `create.html`.
8. Verify split view JS is an inline `<script>` in `list.html` — NOT in `form.js`.
9. Verify split view toggle button exists, hidden by default, shown via JS on desktop (>= 768px).
10. Verify split view correctly clones and separates income/expense rows into two columns.
11. Verify `form.js` is NOT modified.
12. Verify all existing element IDs and names are preserved in `create.html` — `#income-type-row`, `#vat-deductible-row`, `#card-reminder`, `#desc-required` still present with same IDs.
13. Verify `replacement_transaction_id` is available to the list template. If the list query already uses `t.*` or `SELECT *`, no route change is needed — verify the implementer did not add an unnecessary edit.
14. Verify no schema changes — no ALTER TABLE, no new columns.
15. Verify no business-rule changes — no validation, no calculation changes.
16. Run:

```bash
pytest -v   # all existing tests must pass
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

Files modified outside allowed files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `#ID` column in transaction list
- [PASS|FAIL] "Corrected" badge for corrected transactions in show_all mode
- [PASS|FAIL] `.badge-corrected` CSS class
- [PASS|FAIL] detail page bidirectional correction link
- [PASS|FAIL] detail route query is read-only
- [PASS|FAIL] income type field above category in create form
- [PASS|FAIL] split view toggle hidden on mobile, visible on desktop
- [PASS|FAIL] split view separates income/expense correctly
- [PASS|FAIL] split view JS is inline in list.html (not in form.js)
- [PASS|FAIL] form.js not modified
- [PASS|FAIL] all JS selectors/IDs preserved
- [PASS|FAIL] no schema changes
- [PASS|FAIL] no business-rule changes
- [PASS|FAIL] all existing tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# Review — I5-T4: List, Detail & Void Styling
**Branch:** `feature/p1-i5/t4-list-detail-void`
**PR target:** `feature/phase-1/iteration-5`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/templates/transactions/list.html` — styled table, amount formatting, badges, empty state, responsive
- Modified: `app/templates/transactions/detail.html` — card layout, badges, audit trail
- Modified: `app/templates/transactions/void.html` — warning styling, destructive button

---

## Review steps

1. Confirm diff scope is limited to the three template files.
2. Verify list table has styled headers, hover states, proper alignment.
3. Verify amount formatting: thousands separator, 2 decimal places.
4. Verify show_all mode: active/voided badges, muted voided rows.
5. Verify empty state message when no transactions.
6. Verify responsive: `.table-wrap` for horizontal scroll on mobile.
7. Verify detail page: card layout, active badge + action links, voided badge + audit trail.
8. Verify void page: warning callout, transaction summary, destructive submit, cancel link.
9. Verify no business logic in templates — display only.
10. Verify all existing route links/URLs are preserved.
11. Run:

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

Files modified outside the three allowed template files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to list.html, detail.html, void.html
- [PASS|FAIL] list table styled with headers and hover states
- [PASS|FAIL] amounts formatted with thousands separator and 2 decimals
- [PASS|FAIL] show_all mode: badges + muted voided rows
- [PASS|FAIL] empty state message present
- [PASS|FAIL] responsive table wrapper for mobile
- [PASS|FAIL] detail page: card layout, badges, audit trail for voided
- [PASS|FAIL] void page: warning callout, destructive button, cancel link
- [PASS|FAIL] all existing links and URLs preserved
- [PASS|FAIL] all 94 tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

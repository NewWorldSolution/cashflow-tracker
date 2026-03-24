# Review — I8-T7: List/Detail/Dashboard Display
**Branch:** `feature/p1-i8/t7-display`
**PR target:** `feature/phase-1/iteration-8`
**Source prompt:** `iterations/p1-i8/prompts/t7-display.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/routes/transactions.py` — list/detail data exposes category path and new metadata
- Modified: `app/routes/dashboard.py` — dashboard uses `cash_in` / `cash_out` and correct VAT-mode-aware values
- Modified: `app/templates/transactions/list.html` — shows translated direction labels and category paths
- Modified: `app/templates/transactions/detail.html` — shows full category path, manual VAT indicator, and metadata
- Modified: `app/templates/dashboard.html` — reflects new direction labels and I8 display rules
- Extended: `app/i18n/en.py` and `app/i18n/pl.py` — display labels

Use `iterations/p1-i8/prompts/t7-display.md` as the detailed source of truth for:
- which views must display hierarchy and metadata
- where manual VAT indicator is allowed
- which calculated values must respect `vat_mode`
- allowed file scope

---

## Review steps

1. Confirm diff scope is limited to `app/routes/transactions.py`, `app/routes/dashboard.py`, `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/templates/dashboard.html`, `app/i18n/en.py`, and `app/i18n/pl.py`.
2. Verify list view shows category as `Parent > Subcategory` using translated labels.
3. Verify list view shows translated `cash_in` / `cash_out` direction labels.
4. Verify list view does not introduce a manual VAT marker or metadata clutter that scope explicitly excluded.
5. Verify detail view shows full translated category path.
6. Verify detail view visibly indicates manual VAT when `vat_mode = manual`.
7. Verify detail view shows manual VAT amounts when applicable and normal VAT values otherwise.
8. Verify detail view shows `customer_type`, `document_flow` when present, and `for_accountant`.
9. Verify detail calculations use manual values in manual mode and derived values in automatic mode.
10. Verify dashboard labels and aggregations use `cash_in` / `cash_out` consistently.
11. Verify EN/PL labels exist for any new display strings.
12. Run:

```bash
pytest -v
ruff check .
```

### Prompt-specific checks from `t7-display.md`

- Verify detail view shows `vat_mode` itself, not just the manual badge.
- Verify `manual_vat_deductible_amount` is shown only where applicable for cash_out manual transactions.
- Verify list view does not show `customer_type` or `document_flow`.
- Verify `app/templates/transactions/create.html` and `static/form.js` were NOT modified (form behavior is T4–T6 scope).
- Verify test files were NOT modified (tests are T8's scope).

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
- [PASS|FAIL] list view shows translated `Parent > Subcategory` path
- [PASS|FAIL] list view shows translated `cash_in` / `cash_out` labels
- [PASS|FAIL] list view does not add disallowed metadata noise
- [PASS|FAIL] detail view shows full category path
- [PASS|FAIL] detail view shows manual VAT indicator when applicable
- [PASS|FAIL] detail view shows correct VAT values for automatic and manual modes
- [PASS|FAIL] detail view shows `customer_type`
- [PASS|FAIL] detail view shows `document_flow` when present
- [PASS|FAIL] detail view shows `for_accountant`
- [PASS|FAIL] dashboard uses `cash_in` / `cash_out` direction labels correctly
- [PASS|FAIL] dashboard calculations/aggregations respect VAT mode
- [PASS|FAIL] EN + PL display labels are present
- [PASS|FAIL] `create.html` and `form.js` not modified (T4–T6 scope)
- [PASS|FAIL] test files not modified (T8 scope)
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# Review — I8-T5: VAT Mode UI
**Branch:** `feature/p1-i8/t5-vat-mode-ui`
**PR target:** `feature/phase-1/iteration-8`
**Source prompt:** `iterations/p1-i8/prompts/t5-vat-mode-ui.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/routes/transactions.py` — create/correct flows accept and preserve `vat_mode`, `manual_vat_amount`, and `manual_vat_deductible_amount`
- Modified: `app/templates/transactions/create.html` — VAT mode toggle and manual VAT fields
- Modified: `static/form.js` — VAT mode UI behavior, manual deductible auto-fill, and internal cash_in lockout
- Extended: `app/i18n/en.py` and `app/i18n/pl.py` — VAT mode labels

Use `iterations/p1-i8/prompts/t5-vat-mode-ui.md` as the detailed source of truth for:
- exact UI behavior
- correction initialization requirements
- internal cash_in restrictions
- allowed file scope

---

## Review steps

1. Confirm diff scope is limited to `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js`, `app/i18n/en.py`, and `app/i18n/pl.py`.
2. Verify the create/correct form shows a VAT mode toggle with `automatic` and `manual` options.
3. Verify selecting `manual` hides rate-based VAT inputs and shows `manual_vat_amount` plus `manual_vat_deductible_amount` for cash_out only.
4. Verify selecting `automatic` hides manual VAT fields and restores the normal VAT inputs.
5. Verify internal cash_in hides the VAT mode UI and forces automatic mode in the form behavior.
6. Verify `manual_vat_deductible_amount` auto-fills from `manual_vat_amount` until the user edits it manually.
7. Verify create POST passes VAT mode fields through to validation/persistence rather than silently dropping them.
8. Verify correct GET preloads stored VAT mode/manual values.
9. Verify correct POST preserves or updates VAT mode/manual values.
10. Verify hidden VAT fields are cleared when switching modes so stale values are not submitted.
11. Verify EN/PL labels exist for VAT mode and manual VAT fields.
12. Run:

```bash
pytest -v
ruff check .
```

### Prompt-specific checks from `t5-vat-mode-ui.md`

- Verify the manual deductible auto-fill stops after the user manually edits the deductible field.
- Verify the manual deductible section is hidden whenever direction changes to `cash_in`.
- Verify the implementation does not introduce `customer_type` or `document_flow` work into this task.
- Verify correction mode initializes the correct visible/hidden VAT sections on page load.
- Verify `app/templates/transactions/detail.html` was NOT modified (display is T7's scope).
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
- [PASS|FAIL] VAT mode toggle appears in create/correct form
- [PASS|FAIL] manual mode hides rate-based VAT inputs
- [PASS|FAIL] manual mode shows `manual_vat_amount`
- [PASS|FAIL] `manual_vat_deductible_amount` is shown only for cash_out
- [PASS|FAIL] automatic mode restores normal VAT inputs
- [PASS|FAIL] internal cash_in hides VAT mode UI and forces automatic
- [PASS|FAIL] manual deductible auto-fills from manual VAT amount
- [PASS|FAIL] create flow passes VAT mode/manual fields through correctly
- [PASS|FAIL] correct flow preloads and persists stored VAT mode/manual values
- [PASS|FAIL] hidden VAT fields are cleared on mode switch
- [PASS|FAIL] EN + PL VAT mode labels are present
- [PASS|FAIL] `detail.html` not modified (T7 scope)
- [PASS|FAIL] test files not modified (T8 scope)
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

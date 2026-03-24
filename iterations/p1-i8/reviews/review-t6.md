# Review — I8-T6: Procedure Metadata UI
**Branch:** `feature/p1-i8/t6-procedure-metadata`
**PR target:** `feature/phase-1/iteration-8`
**Source prompt:** `iterations/p1-i8/prompts/t6-procedure-metadata.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `app/routes/transactions.py` — create/correct flows accept and preserve `customer_type`, `document_flow`, and `for_accountant`
- Modified: `app/templates/transactions/create.html` — customer type selector, document flow selector, and updated accountant default behavior
- Modified: `static/form.js` — context-dependent metadata visibility and client-side guardrails
- Extended: `app/i18n/en.py` and `app/i18n/pl.py` — metadata labels

Use `iterations/p1-i8/prompts/t6-procedure-metadata.md` as the detailed source of truth for:
- exact context rules for `document_flow`
- correction preselection behavior
- `invoice_and_receipt` client-side behavior
- allowed file scope

---

## Review steps

1. Confirm diff scope is limited to `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js`, `app/i18n/en.py`, and `app/i18n/pl.py`.
2. Verify `customer_type` appears on transactions generally and is required.
3. Verify internal cash_in hides `customer_type` and forces it to `private`.
4. Verify `document_flow` is shown and required for `cash_in + cash_in_type = external`, with default `receipt`.
5. Verify `document_flow` is hidden for internal cash_in.
6. Verify `document_flow` is shown but optional for cash_out.
7. Verify `invoice_and_receipt` is disabled or rejected in the UI when `customer_type != private`.
8. Verify create form defaults `for_accountant` to checked for normal transactions.
9. Verify internal cash_in forces `for_accountant = false` in the form behavior.
10. Verify correction loads stored `customer_type`, `document_flow`, and `for_accountant` values rather than re-defaulting them.
11. Verify routes pass all metadata fields through to validation/persistence rather than silently dropping them.
12. Verify EN/PL labels exist for all new metadata fields and values.
13. Run:

```bash
pytest -v
ruff check .
```

### Prompt-specific checks from `t6-procedure-metadata.md`

- Verify `document_flow` defaults to `receipt` only for external cash_in, not for cash_out.
- Verify switching away from internal cash_in clears forced metadata values correctly.
- Verify `invoice_and_receipt` is reset if it was selected and `customer_type` changes to non-private.
- Verify switching away from internal cash_in re-enables customer_type and document_flow without forcing values.
- Verify `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, and `app/templates/dashboard.html` were NOT modified (display is T7's scope).
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
- [PASS|FAIL] `customer_type` selector appears and is required
- [PASS|FAIL] internal cash_in hides and forces `customer_type = private`
- [PASS|FAIL] external cash_in shows `document_flow` as required with default `receipt`
- [PASS|FAIL] internal cash_in hides `document_flow`
- [PASS|FAIL] cash_out shows `document_flow` as optional
- [PASS|FAIL] `invoice_and_receipt` is unavailable when `customer_type != private`
- [PASS|FAIL] create form defaults `for_accountant` to checked
- [PASS|FAIL] internal cash_in forces `for_accountant = false`
- [PASS|FAIL] correct form preserves stored metadata values without re-defaulting
- [PASS|FAIL] routes pass metadata fields through correctly
- [PASS|FAIL] switching away from internal cash_in restores customer_type and document_flow without forcing values
- [PASS|FAIL] EN + PL metadata labels are present
- [PASS|FAIL] list/detail/dashboard templates not modified (T7 scope)
- [PASS|FAIL] test files not modified (T8 scope)
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

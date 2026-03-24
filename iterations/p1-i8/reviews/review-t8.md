# Review — I8-T8: Tests
**Branch:** `feature/p1-i8/t8-tests`
**PR target:** `feature/phase-1/iteration-8`
**Source prompt:** `iterations/p1-i8/prompts/t8-tests.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `tests/test_init_db.py` — schema and seed coverage for hierarchy and new columns
- Modified: `tests/test_validation.py` — cross-field validation coverage for I8 rules
- Modified: `tests/test_calculations.py` — automatic/manual VAT calculation coverage
- Modified: `tests/test_transactions.py` — create/correct and UI-facing flow coverage for I8 features

Use `iterations/p1-i8/prompts/t8-tests.md` as the detailed source of truth for:
- exact schema expectations
- exact validation/cross-field coverage
- expected helper updates
- allowed file scope

---

## Review steps

1. Confirm diff scope is limited to `tests/test_init_db.py`, `tests/test_validation.py`, `tests/test_calculations.py`, and `tests/test_transactions.py`.
2. Verify all prior direction/income-type test references are updated to `cash_in` / `cash_out` and `cash_in_type`.
3. Verify schema/seed tests cover 19 parents, 62 subcategories, unique slugs, and the new transaction columns.
4. Verify validation tests cover manual VAT rules, `customer_type`, `document_flow`, internal cash_in restrictions, and leaf-only category selection.
5. Verify calculation tests cover both automatic and manual VAT paths.
6. Verify transaction tests cover create/correct flows with category hierarchy, VAT mode, metadata, and accountant defaults.
7. Verify tests cover `invoice_and_receipt` only for `customer_type = private`.
8. Verify tests cover `document_flow` required for external cash_in and optional for cash_out.
9. Run:

```bash
pytest -v
ruff check .
```

### Prompt-specific checks from `t8-tests.md`

- Verify tests assert parent categories have NULL VAT defaults and leaves match the taxonomy table.
- Verify tests cover both create and correct flows for manual VAT and metadata preservation.
- Verify test helpers use valid leaf category IDs (not parent group IDs) — a parent ID would silently pass an invalid category through validation.
- Verify this task does not modify application code outside test files.

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

- [PASS|FAIL] diff scope limited to allowed test files
- [PASS|FAIL] direction/value renames are fully reflected in tests
- [PASS|FAIL] schema tests cover new columns and hierarchy shape
- [PASS|FAIL] seed tests cover unique slugs and VAT defaults
- [PASS|FAIL] validation tests cover all I8 cross-field rules
- [PASS|FAIL] calculation tests cover automatic and manual VAT modes
- [PASS|FAIL] transaction tests cover create and correct flows with new fields
- [PASS|FAIL] tests cover external cash_in `document_flow` requirement
- [PASS|FAIL] tests cover `invoice_and_receipt` private-only rule
- [PASS|FAIL] tests cover internal cash_in enforcement
- [PASS|FAIL] test helpers use leaf category IDs (not parent group IDs)
- [PASS|FAIL] no application code modified outside test files
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

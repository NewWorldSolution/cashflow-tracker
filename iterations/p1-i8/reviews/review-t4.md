# Review — I8-T4: Category Picker UI
**Branch:** `feature/p1-i8/t4-category-picker`
**PR target:** `feature/phase-1/iteration-8`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `app/routes/transactions.py` — passes category hierarchy data to create/correct templates; correct route passes parent_id and category_id for pre-selection
- `app/templates/transactions/create.html` — two-level picker (parent group → subcategory) with embedded JSON hierarchy
- `static/form.js` — cascade logic, VAT auto-fill on subcategory selection, direction-change reset, correction initialization
- `app/i18n/en.py` — labels for category picker UI elements
- `app/i18n/pl.py` — same as en.py

---

## Review Steps

1. Confirm diff scope is limited to `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js`, `app/i18n/en.py`, and `app/i18n/pl.py`.

2. **Route — create GET:**
   - Passes category hierarchy (parents + children) for both directions to the template.
   - Includes VAT defaults per subcategory in the data.

3. **Route — correct GET:**
   - Passes `parent_id` and `category_id` of the stored transaction for pre-selection.

4. **Template — category picker structure:**
   - Two dropdowns exist: parent group selector and subcategory selector.
   - Only `category_id` (leaf) has `name="category_id"` — this is the field submitted to the server.
   - The parent group selector does NOT have a `name` attribute that gets submitted (it is cosmetic only).
   - Both dropdowns filter by direction (cash_in/cash_out).

5. **Template — hierarchy data embed:**
   - Category hierarchy is embedded in the page (via a `<script>` block, a data attribute, or inline JSON) — no form of API call or fetch is used to retrieve it.
   - Embedded data covers both cash_in and cash_out hierarchies.
   - Each subcategory entry includes `vat_rate` and `vat_deductible_pct`.
   - The exact variable name (e.g., `window.CATEGORY_HIERARCHY`) does not matter — what matters is that the data is present on page load and the JS cascade uses it exclusively.

6. **JS — cascade logic:**
   - Parent group change populates subcategory dropdown with the parent's children only.
   - Subcategory selection auto-fills `vat_rate` (and `vat_deductible_pct` for cash_out) from embedded data.
   - Direction change (cash_in ↔ cash_out) resets both dropdowns and repopulates parent groups.

7. **JS — correction initialization:**
   - On page load in correction mode, the correct parent group is pre-selected.
   - Subcategory dropdown is populated with that parent's children.
   - The stored subcategory is selected.

8. **No API calls** — all cascade logic uses embedded data, no fetch/XHR.

9. **i18n labels** — verify EN and PL translations exist for picker UI elements:
   - `select_category_group`
   - `select_subcategory`
   - `form_category_group`
   - `form_subcategory`
10. **Category label key convention** — verify that category names rendered in the dropdowns are looked up via `cat_{slug}` keys (e.g., `cat_ci_services`, `cat_co_marketing_paid_ads`), consistent with the T2 seeding convention. Hardcoded label strings or a `cat_group_` prefix are a failure.

10. Verify VAT mode toggle (T5's work), customer_type, document_flow, and for_accountant (T6's work) were NOT added in this task.
11. Run:

```bash
pytest -v
ruff check .
```

---

## Required Output Format

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

Files modified outside `app/routes/transactions.py`, `app/templates/transactions/create.html`, `static/form.js`, `app/i18n/en.py`, `app/i18n/pl.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] create GET passes hierarchy data for both directions
- [PASS|FAIL] correct GET passes parent_id and category_id for pre-selection
- [PASS|FAIL] two separate dropdowns in template (parent group + subcategory)
- [PASS|FAIL] only `category_id` is submitted (parent group is cosmetic)
- [PASS|FAIL] hierarchy data embedded on page load (no API calls, any variable name acceptable)
- [PASS|FAIL] embedded data includes VAT defaults per subcategory
- [PASS|FAIL] JS cascade: parent selection populates subcategory dropdown
- [PASS|FAIL] JS cascade: subcategory selection auto-fills VAT defaults
- [PASS|FAIL] JS: direction change resets and repopulates both dropdowns
- [PASS|FAIL] JS: correction pre-selects parent and subcategory on page load
- [PASS|FAIL] no API calls for cascade (all data embedded)
- [PASS|FAIL] EN + PL i18n labels for picker UI elements
- [PASS|FAIL] category labels use `cat_{slug}` key convention (no hardcoded strings or `cat_group_` prefix)
- [PASS|FAIL] no VAT mode, customer_type, or document_flow added (T5/T6 scope)
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

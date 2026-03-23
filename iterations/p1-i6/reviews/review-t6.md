# Review — I6-T6: UX Polish for Transaction States + Labels
**Branch:** `feature/p1-i6/t6-ux-polish`
**PR target:** `feature/phase-1/iteration-6`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Renamed "Direction" → "Transaction Type" in all UI labels (EN + PL)
- Replaced "Void/Voided" with "Cancel/Canceled" in user-facing text (backend names unchanged)
- Corrected transactions show distinct "Correction Details" section (not "Cancellation Details")
- Correction flow requires an explicit reason (no more hardcoded "Corrected")
- Audit timestamps (`created_at`, `voided_at`) show date+time via `format_datetime()`
- Business dates remain date-only
- "Logged by" removed from transaction detail page
- Category labels localized via `t('category_' + name)` — DB unchanged
- Direction, payment method, income type display values localized
- Split-view JS updated to use `data-direction` attribute
- `void.html` summary uses `format_date()` and `format_amount()`

---

## Review steps

1. Confirm diff scope matches allowed files only. No changes to `validation.py`, `calculations.py`, `form.js`, `db/schema.sql`, `db/init_db.py`, `base.html`, `auth/login.html`, `settings/opening_balance.html`.

2. Verify **i18n key changes** in `en.py` and `pl.py`:
   - `form_direction`, `list_col_direction`, `detail_direction` updated to "Transaction Type" / "Typ transakcji"
   - All user-facing "void/voided" text changed to "cancel/canceled"
   - New correction detail keys: `correction_details_title`, `correction_reason`, `corrected_by`, `corrected_at`
   - New correction form keys: `correction_reason_label`, `correction_reason_placeholder`
   - New validation error: `"Correction reason is required."`
   - 22 category label keys (`category_services`, `category_products`, etc.) in both locales
   - Backend variable/column names unchanged in code

3. Verify **detail.html** splits the inactive transaction block:
   - `replacement_transaction_id` present → show "Correction Details" with correction-specific labels
   - No replacement → show "Cancellation Details" with cancel-specific labels
   - Both blocks use `format_datetime()` for `voided_at`
   - `created_at` uses `format_datetime()`
   - "Logged by" line removed
   - `category_label` → `t('category_' + txn.category_name)`
   - Direction and payment method use `t()` lookup

4. Verify **correction flow** in `app/routes/transactions.py`:
   - `get_correct_transaction` passes `is_correction=True` to template
   - `post_correct_transaction` accepts `correction_reason` form field
   - Empty correction reason returns validation error (translated)
   - Submitted reason used in UPDATE instead of hardcoded `'Corrected'`

5. Verify **create.html** shows correction reason field when `is_correction` is true.

6. Verify **format_datetime** in `app/i18n/__init__.py`:
   - Polish: `DD.MM.YYYY HH:MM`
   - English: `YYYY-MM-DD HH:MM`
   - Handles date objects and datetime strings
   - Registered as Jinja2 global in `app/main.py`

7. Verify **list.html**:
   - Direction cell has `data-direction="{{ txn.direction }}"` attribute
   - Direction display uses `t('direction_' + txn.direction)`
   - Payment method uses `t('payment_' + txn.payment_method)`
   - Category uses `t('category_' + txn.category_name)`
   - Split-view JS reads `data-direction` attribute instead of text content

8. Verify **dashboard.html**:
   - Direction and payment method use `t()` lookup
   - Category uses `t('category_' + txn.category_name)`

9. Verify **void.html** summary line uses `format_date()` and `format_amount()`.

10. Verify **SQL queries** in `transaction_service.py`, `routes/transactions.py`, and `routes/dashboard.py` now include `c.name AS category_name` in the SELECT.

11. Run:
```bash
pytest -v   # all existing + new tests must pass
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
- [PASS|FAIL] "Direction" renamed to "Transaction Type" in UI
- [PASS|FAIL] "Void/Voided" replaced with "Cancel/Canceled" in user-facing text
- [PASS|FAIL] Backend names unchanged (void_transaction, void_reason, voided_by, voided_at)
- [PASS|FAIL] Corrected transactions show "Correction Details" in detail view
- [PASS|FAIL] Correction flow requires explicit reason
- [PASS|FAIL] Audit timestamps show date+time via format_datetime
- [PASS|FAIL] Business dates remain date-only
- [PASS|FAIL] "Logged by" removed from detail page
- [PASS|FAIL] Category labels localized in both locales
- [PASS|FAIL] Direction, payment method, income type localized in display
- [PASS|FAIL] Split-view JS uses data-direction attribute
- [PASS|FAIL] void.html summary uses format_date/format_amount
- [PASS|FAIL] PL/EN switch works in all affected views
- [PASS|FAIL] No schema/migration changes
- [PASS|FAIL] All tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

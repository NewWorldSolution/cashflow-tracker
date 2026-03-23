# I6-T6 — UX Polish for Transaction States + Labels

**Branch:** `feature/p1-i6/t6-ux-polish` (from `feature/phase-1/iteration-6`)
**PR target:** `feature/phase-1/iteration-6`
**Depends on:** I6-T4 ✅ DONE

---

## Goal

Clean up the remaining UX issues in transaction views after i18n/formatting:

- Replace technical "void/voided" wording with user-friendly "cancel/canceled" in UI
- Improve corrected-transaction presentation (distinct from canceled)
- Show date+time for audit timestamps (`created_at`, `voided_at`)
- Rename "Direction" to "Transaction Type" in UI
- Remove "Logged by" from transaction detail view
- Localize category labels via i18n keys mapped from `category.name`
- Require a correction reason when correcting a transaction
- Fix `void.html` to use `format_date()` and `format_amount()`

---

## Read Before Starting

```
CLAUDE.md
app/i18n/en.py                                (current English dictionary)
app/i18n/pl.py                                (current Polish dictionary)
app/i18n/__init__.py                          (format_date, format_amount)
app/templates/transactions/detail.html
app/templates/transactions/list.html
app/templates/transactions/create.html
app/templates/transactions/void.html
app/templates/dashboard.html
app/routes/transactions.py                    (correction flow, line ~380)
seed/categories.sql                           (category names for i18n keys)
```

---

## Allowed Files

```
app/i18n/en.py                                ← extend (new/renamed keys)
app/i18n/pl.py                                ← extend (new/renamed keys)
app/i18n/__init__.py                          ← modify (add format_datetime)
app/main.py                                   ← modify (register format_datetime global)
app/templates/transactions/detail.html        ← modify
app/templates/transactions/list.html          ← modify
app/templates/transactions/create.html        ← modify
app/templates/transactions/void.html          ← modify
app/templates/dashboard.html                  ← modify
app/routes/transactions.py                    ← modify (correction reason capture)
tests/test_transactions.py                    ← extend (correction reason tests)
```

Do NOT modify `validation.py`, `calculations.py`, `form.js`, `db/schema.sql`, `db/init_db.py`, `base.html`, `auth/login.html`, or `settings/opening_balance.html`.

---

## What to Implement

### 1. Rename "Direction" → "Transaction Type" in UI

Update i18n keys — English and Polish labels only. Do NOT change the database column name, form field name, or any backend code.

**en.py changes:**
```python
"form_direction": "Transaction Type",         # was "Direction"
"list_col_direction": "Type",                 # was "Direction"
"detail_direction": "Transaction type",       # was "Direction"
```

**pl.py changes:**
```python
"form_direction": "Typ transakcji",           # was "Kierunek"
"list_col_direction": "Typ",                  # was "Kierunek"
"detail_direction": "Typ transakcji",         # was "Kierunek"
```

### 2. Replace "Void/Voided" with "Cancel/Canceled" in user-facing text

Backend names (`void_transaction`, `void_reason`, `voided_at`, `voided_by`) stay unchanged. Only UI labels change.

**en.py — update existing keys:**
```python
# Badges
"badge_voided": "Canceled",                                    # was "Voided"

# Detail page — void details section
"void_details_title": "Cancellation Details",                  # was "Void Details"
"void_reason": "Cancellation reason",                          # was "Void reason"
"voided_by": "Canceled by",                                    # was "Voided by"
"voided_at": "Canceled at",                                    # was "Voided at"

# Void page
"void_title": "Cancel Transaction",                            # was "Void Transaction"
"void_warning": "This action cannot be undone. The transaction will be marked as canceled.",
"void_reason_label": "Reason for canceling (required)",        # was "Reason for voiding (required)"
"void_reason_placeholder": "Why is this transaction being canceled?",
"void_submit": "Cancel Transaction",                           # was "Void Transaction"

# Detail action button
"detail_void": "Cancel",                                       # was "Void"

# List
"list_show_all": "Show All (incl. canceled)",                  # was "Show All (incl. voided)"

# Dashboard
"dashboard_voided": "canceled",                                # was "voided"

# Flash
"flash_transaction_voided": "Transaction canceled.",           # was "Transaction voided."
"flash_transaction_corrected": "Transaction corrected. Original has been canceled.",
```

**pl.py — corresponding updates:**
```python
# The Polish already uses "anulowana" (canceled) — keep those as-is where they fit.
# The main change is making correction vs cancellation distinct (see step 3).
```

### 3. Improve corrected transaction presentation

Corrected transactions should display differently from canceled ones in the detail page.

**Add new i18n keys for correction details:**

**en.py:**
```python
# Correction details (shown instead of Cancellation Details when replacement_transaction_id exists)
"correction_details_title": "Correction Details",
"correction_reason": "Correction reason",
"corrected_by": "Corrected by",
"corrected_at": "Corrected at",
```

**pl.py:**
```python
"correction_details_title": "Szczegóły korekty",
"correction_reason": "Powód korekty",
"corrected_by": "Skorygował",
"corrected_at": "Data korekty",
```

**Update `detail.html`** — the existing `{% if not txn.is_active %}` block currently always shows "Void Details". Split it:

```html
{% if not txn.is_active %}
  {% if txn.replacement_transaction_id %}
  {# This transaction was corrected — show correction details #}
  <div class="card mt-4 audit-card">
    <h3>{{ t('correction_details_title') }}</h3>
    <dl class="detail-grid">
      <dt>{{ t('correction_reason') }}</dt><dd>{{ txn.void_reason }}</dd>
      <dt>{{ t('corrected_by') }}</dt><dd>{{ txn.voided_by_username }}</dd>
      {% if txn.voided_at %}
      <dt>{{ t('corrected_at') }}</dt><dd>{{ format_datetime(txn.voided_at) }}</dd>
      {% endif %}
      <dt>{{ t('replaced_by') }}</dt>
      <dd><a href="/transactions/{{ txn.replacement_transaction_id }}">#{{ txn.replacement_transaction_id }}</a></dd>
    </dl>
  </div>
  {% else %}
  {# This transaction was canceled — show cancellation details #}
  <div class="card mt-4 audit-card">
    <h3>{{ t('void_details_title') }}</h3>
    <dl class="detail-grid">
      <dt>{{ t('void_reason') }}</dt><dd>{{ txn.void_reason }}</dd>
      <dt>{{ t('voided_by') }}</dt><dd>{{ txn.voided_by_username }}</dd>
      {% if txn.voided_at %}
      <dt>{{ t('voided_at') }}</dt><dd>{{ format_datetime(txn.voided_at) }}</dd>
      {% endif %}
    </dl>
  </div>
  {% endif %}
{% endif %}
```

### 4. Require a correction reason

Currently, the correction flow hardcodes `void_reason = 'Corrected'`. Instead, capture an explicit reason from the user.

**In `app/routes/transactions.py`:**

The `get_correct_transaction` handler renders `create.html`. Add a `correction_reason` field to `form_data` and a flag `is_correction = True` to the template context.

The `post_correct_transaction` handler should accept a `correction_reason` Form field. If empty, return a validation error. Use the submitted reason instead of hardcoded `'Corrected'` in the UPDATE statement.

**In `create.html`:**

Add a correction reason field that only shows when `is_correction` is true:

```html
{% if is_correction %}
<div class="form-section form-section-alt mb-4">
  <div class="form-group">
    <label class="form-label" for="correction_reason">{{ t('correction_reason_label') }}</label>
    <textarea id="correction_reason" name="correction_reason" rows="2"
      placeholder="{{ t('correction_reason_placeholder') }}">{{ form_data.get('correction_reason', '') }}</textarea>
  </div>
</div>
{% endif %}
```

**Add i18n keys:**

en.py:
```python
"correction_reason_label": "Reason for correction (required)",
"correction_reason_placeholder": "What is being corrected and why?",
```

pl.py:
```python
"correction_reason_label": "Powód korekty (wymagane)",
"correction_reason_placeholder": "Co jest korygowane i dlaczego?",
```

**Add validation error key (route-level, not in validation.py):**

en.py VALIDATION_ERRORS:
```python
"Correction reason is required.": "Correction reason is required.",
```

pl.py VALIDATION_ERRORS:
```python
"Correction reason is required.": "Powód korekty jest wymagany.",
```

### 5. Add `format_datetime` for audit timestamps

Audit timestamps (`created_at`, `voided_at`) should show date AND time. Business dates (`date`, `as_of_date`) stay date-only.

**Add to `app/i18n/__init__.py`:**

```python
def format_datetime(value, locale: str) -> str:
    """Format a datetime value for display, showing both date and time.

    Polish: DD.MM.YYYY HH:MM
    English: YYYY-MM-DD HH:MM
    """
    if not value:
        return "—"
    if hasattr(value, "strftime"):
        if locale == "pl":
            return value.strftime("%d.%m.%Y %H:%M")
        return value.strftime("%Y-%m-%d %H:%M")
    # String handling — "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DDTHH:MM:SS"
    s = str(value).replace("T", " ")
    parts = s.split(" ")
    date_part = parts[0]
    time_part = parts[1][:5] if len(parts) > 1 else ""
    if locale == "pl":
        date_parts = date_part.split("-")
        if len(date_parts) == 3:
            date_part = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
    if time_part:
        return f"{date_part} {time_part}"
    return date_part
```

**Register in `app/main.py`:**

Import `format_datetime` alongside `format_date` and `format_amount`. Create a `@pass_context` wrapper like the others. Register on all 4 template envs.

**Update templates to use `format_datetime` for audit timestamps:**

- `detail.html`: `created_at` → `{{ format_datetime(txn.created_at) }}`
- `detail.html`: `voided_at` → `{{ format_datetime(txn.voided_at) }}` (in both correction and cancellation blocks)

Keep `format_date` for business dates (`txn.date`, `as_of_date`, recent transaction dates).

### 6. Remove "Logged by" from transaction detail

Remove this line from `detail.html`:
```html
<dt>{{ t('detail_logged_by') }}</dt><dd>{{ txn.logged_by_username }}</dd>
```

Keep the `detail_logged_by` key in en.py/pl.py (it's used in the list view column header as `list_col_logged_by`). Just remove the detail-page display.

### 7. Localize category labels

Map each `category.name` from `seed/categories.sql` to a translation key. The pattern is `category_{name}`.

**Add to en.py MESSAGES:**
```python
# Category labels
"category_services": "Services",
"category_products": "Products sold",
"category_internal_transfer": "Internal transfer",
"category_other_income": "Other income",
"category_marketing": "Marketing & advertising",
"category_marketing_commission": "Sales commissions",
"category_rent": "Rent & premises",
"category_utilities": "Utilities",
"category_renovation": "Renovation & repairs",
"category_office_supplies": "Office supplies",
"category_cleaning": "Cleaning services",
"category_consumables": "Operational consumables",
"category_equipment": "Equipment & tools",
"category_contractor_fees": "Contractor & educator fees",
"category_taxes": "Taxes & ZUS",
"category_it_software": "IT & software",
"category_salaries": "Salaries & employee costs",
"category_transport_vehicle": "Vehicle & petrol",
"category_transport_travel": "Travel & transport",
"category_training": "Training & education",
"category_inventory": "Inventory purchases",
"category_other_expense": "Other expense",
```

**Add to pl.py MESSAGES:**
```python
# Category labels
"category_services": "Usługi",
"category_products": "Sprzedaż produktów",
"category_internal_transfer": "Przelew wewnętrzny",
"category_other_income": "Inne przychody",
"category_marketing": "Marketing i reklama",
"category_marketing_commission": "Prowizje sprzedażowe",
"category_rent": "Czynsz i lokal",
"category_utilities": "Media",
"category_renovation": "Remonty i naprawy",
"category_office_supplies": "Artykuły biurowe",
"category_cleaning": "Usługi sprzątania",
"category_consumables": "Materiały eksploatacyjne",
"category_equipment": "Sprzęt i narzędzia",
"category_contractor_fees": "Usługi podwykonawców i edukatorów",
"category_taxes": "Podatki i ZUS",
"category_it_software": "IT i oprogramowanie",
"category_salaries": "Wynagrodzenia i koszty pracownicze",
"category_transport_vehicle": "Pojazd i paliwo",
"category_transport_travel": "Podróże i transport",
"category_training": "Szkolenia i edukacja",
"category_inventory": "Zakupy magazynowe",
"category_other_expense": "Inne wydatki",
```

**Update templates** — everywhere `category_label` is displayed, use translation lookup instead:

The category data from the DB includes `name` (slug) and `label` (English text). We need access to `name` in templates that currently only get `category_label`.

**Option A (preferred — template-only):** The SQL queries already join `c.label AS category_label`. They also have access to `c.name`. Check the queries:

- `app/services/transaction_service.py:8` — `SELECT t.*, c.label AS category_label` — also add `c.name AS category_name`
- `app/routes/dashboard.py:49` — same pattern, add `c.name AS category_name`
- `app/routes/transactions.py:153` — same pattern, add `c.name AS category_name`

Then in templates replace:
```
{{ txn.category_label }}
```
with:
```
{{ t('category_' + txn.category_name) }}
```

For the create form, categories already have `cat.name` available — replace:
```
{{ cat.label }}
```
with:
```
{{ t('category_' + cat.name) }}
```

**Also update allowed files** to include:
```
app/services/transaction_service.py            ← modify (add category_name to SELECT)
app/routes/dashboard.py                        ← modify (add category_name to SELECT)
```

### 8. Fix `void.html` transaction summary formatting

Line 15 of `void.html` currently shows:
```html
<p><strong>{{ txn.date }}</strong> - {{ txn.category_label }} - {{ "{:,.2f}".format(txn.amount) }}</p>
```

Replace with:
```html
<p><strong>{{ format_date(txn.date) }}</strong> — {{ t('category_' + txn.category_name) }} — {{ format_amount(txn.amount) }}</p>
```

### 9. Fix split-view JS direction detection

The split-view JavaScript in `list.html` (lines ~111-119) detects direction by comparing cell text content to `'income'` and `'expense'`. After localising direction display values, Polish locale will render `'Przychód'`/`'Wydatek'`, breaking the JS match.

**Fix:** Add `data-direction="{{ txn.direction }}"` to the direction `<td>` and update the JS to use the data attribute:

```html
<td data-direction="{{ txn.direction }}">{{ t('direction_' + txn.direction) }}</td>
```

```javascript
var dirCell = row.querySelector('[data-direction]');
var direction = dirCell ? dirCell.dataset.direction : '';
if (direction === 'income') incomeRows.push(row.cloneNode(true));
else expenseRows.push(row.cloneNode(true));
```

### 10. Localise direction, payment method, and income type display values

These enum values from the DB must display in the user's locale. Use the existing `direction_*`, `payment_*`, and `income_type_*` keys already in en.py/pl.py.

**Templates to update:**

`list.html`:
- `{{ txn.direction }}` → `{{ t('direction_' + txn.direction) }}`
- `{{ txn.payment_method }}` → `{{ t('payment_' + txn.payment_method) }}`

`detail.html`:
- `{{ txn.direction }}` → `{{ t('direction_' + txn.direction) }}`
- `{{ txn.payment_method }}` → `{{ t('payment_' + txn.payment_method) }}`
- `{{ txn.income_type if txn.income_type else '—' }}` → `{{ t('income_type_' + txn.income_type) if txn.income_type else '—' }}`

`dashboard.html`:
- `{{ txn.direction }}` → `{{ t('direction_' + txn.direction) }}`
- `{{ txn.payment_method }}` → `{{ t('payment_' + txn.payment_method) }}`

`create.html`:
- `{{ pm | capitalize }}` → `{{ t('payment_' + pm) }}`

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all existing tests + any new correction reason tests must pass
```

- [ ] "Direction" renamed to "Transaction Type" in all UI (EN: "Transaction Type" / "Type", PL: "Typ transakcji" / "Typ")
- [ ] "Void/Voided" replaced with "Cancel/Canceled" in all user-facing text
- [ ] Backend names unchanged (`void_transaction`, `void_reason`, `voided_by`, `voided_at`)
- [ ] Corrected transactions show "Correction Details" (not "Cancellation Details") in detail view
- [ ] Corrected transactions show "Corrected" badge (unchanged — already works)
- [ ] Correction flow requires an explicit reason (not hardcoded "Corrected")
- [ ] Audit timestamps (`created_at`, `voided_at`) show date+time
- [ ] Business dates (`date`, `as_of_date`) remain date-only
- [ ] "Logged by" removed from transaction detail page
- [ ] Category labels display translated names in both locales
- [ ] Direction, payment method, income type display translated in both locales
- [ ] Split-view JS still works correctly in both locales
- [ ] `void.html` summary uses `format_date()` and `format_amount()`
- [ ] PL/EN switch works correctly across all affected views
- [ ] No schema changes, no migration changes
- [ ] All tests pass
- [ ] ruff clean

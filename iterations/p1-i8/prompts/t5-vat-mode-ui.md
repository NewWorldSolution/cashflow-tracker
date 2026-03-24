# I8-T5 — VAT Mode UI

**Branch:** `feature/p1-i8/t5-vat-mode-ui`
**Base:** `feature/phase-1/iteration-8` (after T4 merged)
**Depends on:** I8-T4

---

## Goal

Add the automatic/manual VAT mode toggle to the create and correct forms. In automatic mode, the existing VAT fields remain. In manual mode, the user enters `manual_vat_amount` (and `manual_vat_deductible_amount` for cash_out). Internal cash_in hides the toggle entirely. Correction opens with the stored mode preselected.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md
app/routes/transactions.py
app/templates/transactions/create.html
static/form.js
```

---

## Deliverables

### 1. Route changes in `app/routes/transactions.py`

#### Create route (POST)
- Accept `vat_mode` from form (default `automatic` if not provided)
- Accept `manual_vat_amount` and `manual_vat_deductible_amount` when mode is `manual`
- Pass all VAT fields through to validation service (T3 already validates)

#### Correct route (GET)
- Pass stored `vat_mode`, `manual_vat_amount`, `manual_vat_deductible_amount` to template

#### Correct route (POST)
- Same as create POST

### 2. Template changes in `app/templates/transactions/create.html`

Add VAT mode toggle after the category picker section:

```html
<!-- VAT Mode Toggle (hidden for internal cash_in) -->
<div id="vat-mode-section">
  <label>{{ t('form_vat_mode') }}</label>
  <div class="toggle-group">
    <label>
      <input type="radio" name="vat_mode" value="automatic" checked> {{ t('vat_mode_automatic') }}
    </label>
    <label>
      <input type="radio" name="vat_mode" value="manual"> {{ t('vat_mode_manual') }}
    </label>
  </div>
</div>
```

#### Automatic mode fields (existing, shown by default)
- `vat_rate` — existing field
- `vat_deductible_pct` — existing field (cash_out only)

#### Manual mode fields (hidden by default, shown when manual selected)
```html
<div id="manual-vat-fields" style="display: none;">
  <label for="manual_vat_amount">{{ t('form_manual_vat_amount') }}</label>
  <input type="number" id="manual_vat_amount" name="manual_vat_amount" step="0.01" min="0">

  <!-- Cash_out only -->
  <div id="manual-vat-deductible-section">
    <label for="manual_vat_deductible_amount">{{ t('form_manual_vat_deductible_amount') }}</label>
    <input type="number" id="manual_vat_deductible_amount" name="manual_vat_deductible_amount" step="0.01" min="0">
  </div>
</div>
```

#### Correction mode
- Pre-select the stored `vat_mode` radio button
- If stored mode is `manual`, show manual fields with stored values
- If stored mode is `automatic`, show automatic fields with stored values

### 3. JavaScript changes in `static/form.js`

#### VAT mode toggle logic
- When `vat_mode` changes to `automatic`: show vat_rate/vat_deductible_pct fields, hide manual fields
- When `vat_mode` changes to `manual`: hide vat_rate/vat_deductible_pct fields, show manual fields
- Clear hidden fields when switching modes (so they don't submit stale values)

#### Internal cash_in behavior
- When `cash_in_type = internal` is selected: hide the entire vat-mode-section, force automatic mode
- When switching away from internal: show the vat-mode-section again

#### Manual deductible auto-fill
- When user enters `manual_vat_amount` and `manual_vat_deductible_amount` is empty (or hasn't been manually changed): auto-fill `manual_vat_deductible_amount` with the same value
- Track whether the user has manually edited the deductible field — if yes, stop auto-filling
- This auto-fill applies only to cash_out (cash_in has no deductible field)

#### Cash_out only for deductible
- `manual_vat_deductible_amount` field is only shown for `cash_out` direction
- When direction changes to `cash_in`, hide this field

#### Correction initialization
- On page load in correction mode: set the correct toggle state and show/hide the right fields

### 4. i18n labels

Add to both `app/i18n/en.py` and `app/i18n/pl.py`:

| Key | EN | PL |
|-----|----|----|
| `form_vat_mode` | VAT Mode | Tryb VAT |
| `vat_mode_automatic` | Automatic | Automatyczny |
| `vat_mode_manual` | Manual | Ręczny |
| `form_manual_vat_amount` | Manual VAT Amount | Ręczna kwota VAT |
| `form_manual_vat_deductible_amount` | Manual VAT Deductible Amount | Ręczna kwota VAT do odliczenia |

---

## Important Rules

- **T3 already handles validation** — the route just needs to pass fields through. Do not duplicate validation logic in routes or JS.
- **No fake blended rates** — when manual mode is active, do not calculate or display a blended vat_rate percentage.
- **Internal cash_in** — the entire VAT mode section is hidden. The user cannot choose manual mode for internal cash_in.
- **Do NOT add customer_type or document_flow** — that is T6's job.
- **Correction preserves stored mode** — do not re-default to automatic. Show whatever was stored.

---

## Allowed Files

```text
app/routes/transactions.py
app/templates/transactions/create.html
static/form.js
app/i18n/en.py
app/i18n/pl.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] VAT mode toggle (automatic/manual) appears in create form
- [ ] Selecting manual hides vat_rate/vat_deductible_pct and shows manual VAT fields
- [ ] Selecting automatic hides manual fields and shows vat_rate/vat_deductible_pct
- [ ] Internal cash_in hides VAT mode toggle entirely
- [ ] Manual deductible auto-fills from manual VAT amount (cash_out only)
- [ ] Manual deductible field only shown for cash_out direction
- [ ] Correct form pre-selects stored VAT mode and shows correct fields
- [ ] User can switch VAT mode during correction
- [ ] Hidden fields are cleared when switching modes
- [ ] i18n labels added (EN + PL)
- [ ] `ruff check .` passes
- [ ] Form submits successfully in both automatic and manual modes

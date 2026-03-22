# I5-T3 — Transaction Form UX

**Branch:** `feature/p1-i5/t3-form-ux` (from `feature/phase-1/iteration-5`)
**PR target:** `feature/phase-1/iteration-5`
**Depends on:** I5-T1 ✅ DONE

---

## Goal

Make the transaction form comfortable and clear. Restructure into 5 visual sections matching the design reference. No business logic changes — all existing JS behavior must be preserved.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i5/prompt.md                              (design reference section)
app/templates/transactions/create.html                   (current form)
static/form.js                                           (all current JS — must be preserved)
static/style.css                                         (T1 classes available)
Minimal Transaction Entry Form/src/app/components/transaction-form.tsx  (design reference)
```

---

## Allowed Files

```
app/templates/transactions/create.html    ← modify
static/form.js                            ← modify (minimal — spacing/toggle class only)
```

Do NOT modify any other file. No business-rule changes in `form.js` — only minimal JS for UI state/classes required by the new form presentation.

---

## What to Implement

### 1. Restructure `create.html` into 5 sections

Use `.form-section`, `.form-group`, `.form-row`, `.form-label`, `.form-helper` classes from T1.

**Section 1 — Basics:**
```html
<div class="form-section">
  <div class="form-group">
    <label class="form-label">Date</label>
    <input type="date" name="date" value="{{ form_data.get('date', today) }}">
  </div>
  <div class="form-group">
    <label class="form-label">Direction</label>
    <div class="toggle-group">
      <label class="toggle-btn {{ 'active' if form_data.get('direction') == 'income' else '' }}">
        <input type="radio" name="direction" value="income" {{ 'checked' if ... }} style="display:none">
        Income
      </label>
      <label class="toggle-btn {{ 'active' if form_data.get('direction', 'expense') == 'expense' else '' }}">
        <input type="radio" name="direction" value="expense" {{ 'checked' if ... }} style="display:none">
        Expense
      </label>
    </div>
  </div>
</div>
```

The radio inputs are hidden inside the toggle labels. The label click triggers the radio. JS adds/removes `.active` class.

**Section 2 — Amount:**
```html
<div class="form-section">
  <div class="form-group">
    <label class="form-label">Amount</label>
    <input type="number" name="amount" step="0.01" min="0" value="{{ form_data.get('amount', '') }}" placeholder="0.00">
    <div class="form-helper">Enter gross amount (VAT included)</div>
  </div>
</div>
```

**Section 3 — Details:**
```html
<div class="form-section">
  <div class="form-row">
    <div class="form-group">
      <label class="form-label">Category</label>
      <select name="category_id">
        <option value="">— select —</option>
        {% for cat in categories %}
        {% if cat.name != 'internal_transfer' %}
        <option value="{{ cat.category_id }}" data-direction="{{ cat.direction }}" ...>{{ cat.label }}</option>
        {% endif %}
        {% endfor %}
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Payment Method</label>
      <select name="payment_method">...</select>
    </div>
  </div>
  <!-- Income type row — shown/hidden by JS -->
  <div class="form-group" id="income-type-row" style="display:none">
    <label class="form-label">Income Type</label>
    <select name="income_type">...</select>
  </div>
  <!-- Card reminder — shown/hidden by JS -->
  <div id="card-reminder" class="callout callout-info mt-2" style="display:none">
    Log gross amount. Card commission is logged separately at month end from terminal invoice.
  </div>
</div>
```

**Section 4 — VAT:**
```html
<div class="form-section">
  <div class="form-row">
    <div class="form-group">
      <label class="form-label">VAT Rate (%)</label>
      <select name="vat_rate">...</select>
    </div>
    <div class="form-group" id="vat-deductible-row" style="display:none">
      <label class="form-label">VAT Deductible (%)</label>
      <select name="vat_deductible_pct">...</select>
    </div>
  </div>
</div>
```

**Section 5 — Optional:**
```html
<div class="form-section">
  <div class="form-group">
    <label class="form-label">
      Description
      <span id="desc-required" class="text-sm" style="display:none; color: var(--color-destructive);">(required)</span>
    </label>
    <textarea name="description" rows="3" placeholder="Optional notes...">{{ form_data.get('description', '') }}</textarea>
  </div>
</div>
```

**Error display — above the form sections (required). Note: validation returns a flat list of strings, not field-keyed errors. Do NOT attempt per-field error mapping via string matching. Inline field highlighting is optional but the error summary box at top is mandatory:**
```html
{% if errors %}
<div class="error-summary">
  <strong>Please fix the following errors:</strong>
  <ul>
    {% for e in errors %}
    <li>{{ e }}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}
```

**Buttons — below all sections:**
```html
<div class="flex gap-3 mt-4">
  <button type="submit" class="btn btn-primary btn-lg">Save Transaction</button>
  <a href="/transactions/" class="btn btn-secondary btn-lg">Cancel</a>
</div>
```

**Form tag — keep configurable action:**
```html
<form method="post" action="{{ form_action | default('/transactions/new') }}">
```

### 2. Update `static/form.js` (minimal changes)

Add toggle button active class management:

```javascript
// Toggle button active class — add after existing direction change handler
document.querySelectorAll('input[name="direction"]').forEach(radio => {
  radio.addEventListener('change', function () {
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    this.closest('.toggle-btn').classList.add('active');
  });
});
```

This is the ONLY new JS. All existing handlers (category filter, lock/unlock, card reminder, page-load initialization) must remain exactly as they are.

### 3. Critical preservation checklist

Before committing, verify these all still work:
- [ ] Direction toggle shows/hides income-type-row and vat-deductible-row
- [ ] Category filter hides options by direction
- [ ] Category change sets VAT rate and deductible defaults
- [ ] Income type "internal" locks VAT rate to 0 and payment method to cash
- [ ] Card reminder shows when payment_method = card
- [ ] desc-required indicator shows for other_expense/other_income
- [ ] Page-load restoration works on error re-render (5b, 5c, 5d in form.js)
- [ ] form_action variable works for both create and correct flows

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all 94 existing tests must pass
```

- [ ] Form organized into 5 clear sections
- [ ] Direction uses toggle button styling (not plain radio)
- [ ] Gross amount helper text visible
- [ ] Card reminder styled as info callout
- [ ] Error summary box at top of form
- [ ] All JS interactions preserved
- [ ] Mobile: single column, comfortable to fill
- [ ] Correct flow works (form_action variable)

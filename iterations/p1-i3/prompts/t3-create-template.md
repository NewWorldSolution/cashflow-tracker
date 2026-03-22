# I3-T3 — Create Template

**Owner:** Codex
**Branch:** `feature/p1-i3/t3-create-template` (from `feature/phase-1/iteration-3`)
**PR target:** `feature/phase-1/iteration-3`
**Depends on:** I3-T1 ✅ DONE (knows field names and error contract)

---

## Goal

Implement the transaction entry form template. Full field set, inline errors, preserved input on error, all required guardrails.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i3/prompt.md          ← read "Transaction Form — Fields" and "Form.js — Required Behaviour" sections
skills/cash-flow/form_logic/SKILL.md
skills/cash-flow/error_handling/SKILL.md
```

---

## Allowed Files

```
app/templates/transactions/create.html    ← create new
```

Do NOT create `__init__.py` or any other file. Template directories do not need package markers.

---

## What to Implement

### app/templates/transactions/create.html

**Structure:**
```
{% extends "base.html" %}

{% block content %}
  <!-- Error list (shown only when errors is non-empty) -->
  {% if errors %}
    <ul class="errors">
      {% for error in errors %}
        <li>{{ error }}</li>
      {% endfor %}
    </ul>
  {% endif %}

  <form method="post" action="/transactions/new">
    <!-- All form fields here -->
  </form>

  <a href="/transactions/">← Back to transactions</a>
  <script src="/static/form.js"></script>
{% endblock %}
```

**Required fields:**

| Field | HTML | Preserved value |
|-------|------|-----------------|
| `date` | `<input type="date" name="date">` | `value="{{ form_data.get('date', today) }}"` |
| `direction` | `<input type="radio" name="direction" value="income">` + expense | checked if `form_data.get('direction') == 'income'` |
| `amount` | `<input type="number" step="0.01" name="amount">` | `value="{{ form_data.get('amount', '') }}"` |
| `category_id` | `<select name="category_id">` populated from `categories` | selected if `form_data.get('category_id') == category.category_id` |
| `payment_method` | `<select name="payment_method">` | selected if matching `form_data.get('payment_method')` |
| `vat_rate` | `<select name="vat_rate">` with options 0/5/8/23 | selected if matching `form_data.get('vat_rate')` |
| `income_type` | `<select name="income_type">` internal/external | inside `#income-type-row`; preserved |
| `vat_deductible_pct` | `<select name="vat_deductible_pct">` 0/50/100 | inside `#vat-deductible-row`; preserved |
| `description` | `<textarea name="description">` | `{{ form_data.get('description', '') }}` |

**Required labels and text:**
- Amount field label: `"Enter gross amount (VAT included)"` — must be visible at all times
- Submit button: `"Save transaction"`

**Required IDs (form.js depends on these — must match exactly):**

| Element | ID | Initial visibility |
|---------|----|--------------------|
| Card payment warning div | `card-reminder` | `display:none` |
| Income type row | `income-type-row` | `display:none` |
| VAT deductible row | `vat-deductible-row` | `display:none` |
| Description required indicator | `desc-required` | `display:none` |

**Card reminder text** (inside `id="card-reminder"`):
```
Log gross amount. Card commission is logged separately at month end from terminal invoice
```

**Input preservation on error:**
All fields must render with preserved values from `form_data` dict when re-rendering after a failed POST. The route handler passes `form_data` as a dict of normalised submitted values. Use `form_data.get('field_name', '')` for all fields.

**Template variables passed from route:**
- `request` — always present (Jinja2 requirement)
- `categories` — list of category rows from db (for dropdown)
- `errors` — list of error strings (empty on fresh GET)
- `form_data` — dict of preserved values (empty dict `{}` on fresh GET)
- `today` — today's date as string (YYYY-MM-DD) for date field default

---

## Acceptance Check

```bash
python -c "
import os; os.environ['SECRET_KEY'] = 'test'
from fastapi.templating import Jinja2Templates
t = Jinja2Templates(directory='app/templates')
# Check template file exists and Jinja2 can parse it
tmpl = t.get_template('transactions/create.html')
print('template loads ok')
"
```

Manually verify:
- Amount label "Enter gross amount (VAT included)" is present in the HTML
- `id="card-reminder"` element exists with `display:none`
- `id="income-type-row"` element exists with `display:none`
- `id="vat-deductible-row"` element exists with `display:none`

---

## Done

- Template renders without Jinja2 errors
- All required element IDs present
- Input preservation implemented for all fields
- PR open → `feature/phase-1/iteration-3`
- Update `iterations/p1-i3/tasks.md`: I3-T3 status → ✅ DONE with one-line note

# I3-T4 — List Template + form.js

**Owner:** Claude Code
**Branch:** `feature/p1-i3/t4-list-and-js` (from `feature/phase-1/iteration-3`)
**PR target:** `feature/phase-1/iteration-3`
**Depends on:** I3-T2 ✅ DONE (routes merged), I3-T3 ✅ DONE (create template merged)

---

## Goal

Implement the transaction list page and the client-side form behaviour script. No new routes. No server-side logic.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i3/prompt.md          ← read "Form.js — Required Behaviour" section and the /categories response structure
iterations/p1-i3/prompts/t3-create-template.md   ← element IDs that form.js must target
skills/cash-flow/form_logic/SKILL.md
```

---

## Allowed Files

```
app/templates/transactions/list.html    ← create new
static/form.js                          ← create new
```

Do NOT modify any other file.

---

## What to Implement

### app/templates/transactions/list.html

```
{% extends "base.html" %}
{% block content %}
  <a href="/transactions/new">New transaction</a>

  {% if transactions %}
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Category</th>
          <th>Direction</th>
          <th>Amount (gross)</th>
          <th>VAT amount</th>
          <th>Effective cost</th>
          <th>Payment</th>
          <th>Logged by</th>
        </tr>
      </thead>
      <tbody>
        {% for t in transactions %}
          <tr>
            <td>{{ t.date }}</td>
            <td>{{ t.category_label }}</td>
            <td>{{ t.direction }}</td>
            <td>{{ t.amount }}</td>
            <td>{{ t.va }}</td>                 <!-- vat_amount computed in route -->
            <td>{{ t.ec if t.ec else '—' }}</td>  <!-- effective_cost; income rows show dash -->
            <td>{{ t.payment_method }}</td>
            <td>{{ t.logged_by_username }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p>No transactions yet.</p>
  {% endif %}
{% endblock %}
```

Note: `t.va` and `t.ec` are the derived fields attached to each row dict by the route handler (see t2-routes.md). The template just renders whatever it receives — no calculations in the template.

### static/form.js

**Element IDs (defined in create.html — must match exactly):**
- `card-reminder` — card payment warning div
- `income-type-row` — row containing income_type select
- `vat-deductible-row` — row containing vat_deductible_pct select
- `desc-required` — required indicator inside description label

**Behaviour to implement:**

```javascript
document.addEventListener('DOMContentLoaded', function () {

  // 1. Fetch /categories on load and build lookup map
  //    Response fields: category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct
  let categoryMap = {};
  fetch('/categories')
    .then(r => r.json())
    .then(cats => {
      cats.forEach(c => { categoryMap[c.category_id] = c; });
    });

  // 2. Direction change: show/hide conditional rows
  //    When switching, clear dependent fields and release any vat_rate lock
  document.querySelectorAll('input[name="direction"]').forEach(radio => {
    radio.addEventListener('change', function () {
      const isIncome = this.value === 'income';
      document.getElementById('income-type-row').style.display = isIncome ? '' : 'none';
      document.getElementById('vat-deductible-row').style.display = isIncome ? 'none' : '';
      // Clear and unlock on switch
      if (!isIncome) {
        const it = document.querySelector('select[name="income_type"]');
        if (it) it.value = '';
      } else {
        const vd = document.querySelector('select[name="vat_deductible_pct"]');
        if (vd) vd.value = '';
      }
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField) vatRateField.disabled = false;
    });
  });

  // 3. Category change: set defaults and update desc-required indicator
  const categorySelect = document.querySelector('select[name="category_id"]');
  if (categorySelect) {
    categorySelect.addEventListener('change', function () {
      const cat = categoryMap[this.value];
      if (!cat) return;

      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (vatRateField && !vatRateField.disabled) {
        vatRateField.value = cat.default_vat_rate;
      }

      const vdField = document.querySelector('select[name="vat_deductible_pct"]');
      if (vdField && cat.default_vat_deductible_pct != null) {
        vdField.value = cat.default_vat_deductible_pct;
      }

      const descReq = document.getElementById('desc-required');
      if (descReq) {
        descReq.style.display = (cat.name === 'other_expense' || cat.name === 'other_income') ? '' : 'none';
      }
    });
  }

  // 4. income_type change: lock/unlock vat_rate
  const incomeTypeSelect = document.querySelector('select[name="income_type"]');
  if (incomeTypeSelect) {
    incomeTypeSelect.addEventListener('change', function () {
      const vatRateField = document.querySelector('select[name="vat_rate"]');
      if (!vatRateField) return;
      if (this.value === 'internal') {
        vatRateField.value = '0';
        vatRateField.disabled = true;
      } else {
        vatRateField.disabled = false;
      }
    });
  }

  // 5. payment_method change: card reminder
  const paymentSelect = document.querySelector('select[name="payment_method"]');
  if (paymentSelect) {
    paymentSelect.addEventListener('change', function () {
      const reminder = document.getElementById('card-reminder');
      if (reminder) {
        reminder.style.display = this.value === 'card' ? '' : 'none';
      }
    });
  }

});
```

---

## Acceptance Check

```bash
node --check static/form.js
# Expected: no syntax errors, exit code 0
```

Manually verify list.html:
- Renders without Jinja2 errors when `transactions=[]`
- Shows "No transactions yet." when list is empty
- Table columns are: Date, Category, Direction, Amount, VAT amount, Effective cost, Payment, Logged by

---

## Done

- `list.html` renders without Jinja2 errors
- `form.js` passes `node --check`
- PR open → `feature/phase-1/iteration-3`
- Update `iterations/p1-i3/tasks.md`: I3-T4 status → ✅ DONE with one-line note

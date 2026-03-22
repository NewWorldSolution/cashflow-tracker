# I5-T6 — UX Improvements (list tracking, form order, split view)

**Branch:** `feature/p1-i5/t6-ux-improvements` (from `feature/phase-1/iteration-5`)
**PR target:** `feature/phase-1/iteration-5`
**Depends on:** I5-T3 ✅ DONE, I5-T4 ✅ DONE, I5-T5 ✅ DONE

---

## Goal

Improve transaction tracking and form usability based on user feedback. Four changes — all UI/template/JS only. No schema changes, no business logic changes.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i5/tasks.md
app/templates/transactions/list.html        (current list)
app/templates/transactions/detail.html      (current detail)
app/templates/transactions/create.html      (current form)
app/routes/transactions.py                  (route context — will be modified minimally)
static/form.js                              (current JS)
static/style.css                            (available classes)
db/schema.sql                               (understand replacement_transaction_id)
```

---

## Allowed Files

```
app/templates/transactions/list.html     ← modify
app/templates/transactions/detail.html   ← modify
app/templates/transactions/create.html   ← modify
app/routes/transactions.py               ← modify (minimal — add reverse-correction query to detail route only; verify list query before changing)
static/style.css                         ← extend (split-view + badge-corrected classes)
```

Do NOT modify schema, validation, services, or any other file. No business-rule changes.

---

## What to Implement

### 1. List page — add `#ID` column + "Corrected" badge

Add a `#` column as the first column in the transaction table:

```html
<th>#</th>
...
<td><a href="/transactions/{{ t.id }}">#{{ t.id }}</a></td>
```

In `show_all` mode, distinguish corrected transactions from simple voids. A transaction is "corrected" when `replacement_transaction_id` is not null. The route must include `replacement_transaction_id` in the list query results.

```html
{% if show_all %}
<td>
  {% if t.is_active %}
  <span class="badge badge-active">Active</span>
  {% elif t.replacement_transaction_id %}
  <span class="badge badge-corrected">Corrected</span>
  {% else %}
  <span class="badge badge-voided">Voided</span>
  {% endif %}
</td>
{% endif %}
```

Add `.badge-corrected` to `style.css`:
```css
.badge-corrected {
  background: #fef3c7;
  color: #92400e;
}
```

**Route change:** The list query in `app/routes/transactions.py` likely already selects `t.*` which includes `replacement_transaction_id`. Verify this before making changes — if it's already available, no route change is needed for the list. This is a SELECT-only concern — no writes, no logic changes.

### 2. Detail page — bidirectional correction links

Currently the voided original links to its replacement. Add the reverse: when viewing a replacement transaction, show a link back to the original it corrected.

**Route change required:** In the detail route (`get_transaction_detail`), after fetching the transaction, run a second query:

```python
# Check if this transaction is a correction of another
original = db.execute(
    "SELECT id FROM transactions WHERE replacement_transaction_id = ? AND is_active = 0",
    (transaction_id,),
).fetchone()
```

Pass `original_id` to the template context (or `None` if not a correction).

**Template change:** In `detail.html`, when the transaction is active and `original_id` is set, show:

```html
{% if original_id %}
<div class="callout callout-info mt-4">
  This transaction is a correction of <a href="/transactions/{{ original_id }}">#{{ original_id }}</a>.
</div>
{% endif %}
```

### 3. Form — move income type above category

When direction is "income", the income type field (internal/external) determines VAT and payment locking. It should appear **before** the category selector so the user decides internal/external first.

**Template change in `create.html`:** Move the `#income-type-row` div from inside Section 3 (after the form-row) to **before** the form-row in Section 3:

```html
<!-- Section 3 — Details -->
<div class="form-section">
  <!-- Income type row — shown/hidden by JS (above category because it determines locks) -->
  <div class="form-group" id="income-type-row" style="display:none">
    <label class="form-label" for="income_type">Income Type</label>
    <select id="income_type" name="income_type">
      <option value="">— select —</option>
      <option value="internal" ...>Internal</option>
      <option value="external" ...>External</option>
    </select>
  </div>
  <div class="form-row">
    <div class="form-group">
      <label class="form-label" for="category_id">Category</label>
      ...
    </div>
    <div class="form-group">
      <label class="form-label" for="payment_method">Payment Method</label>
      ...
    </div>
  </div>
  <!-- Card reminder stays after payment method -->
  <div id="card-reminder" class="callout callout-info mt-2" style="display:none">...</div>
</div>
```

No JS logic changes needed — the `#income-type-row` element is found by ID regardless of position.

### 4. List page — split view toggle (desktop only)

Add a toggle button next to the existing "Show All / Active Only" button:

```html
<button id="split-view-toggle" class="btn btn-sm btn-secondary" style="display:none;">Split View</button>
```

The button is hidden by default and shown via JS only on screens >= 768px (desktop).

**JS behavior — add as an inline `<script>` block in `list.html` (do NOT put this in `form.js` — that file is for the create form only):**

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('split-view-toggle');
  if (!toggle) return;

  // Only show on desktop
  if (window.innerWidth >= 768) {
    toggle.style.display = '';
  }

  let splitActive = false;

  toggle.addEventListener('click', function() {
    splitActive = !splitActive;
    const tableWrap = document.querySelector('.table-wrap');
    if (!tableWrap) return;

    if (splitActive) {
      toggle.textContent = 'Combined View';
      // Hide the main table
      tableWrap.style.display = 'none';
      // Build split view
      buildSplitView();
    } else {
      toggle.textContent = 'Split View';
      tableWrap.style.display = '';
      // Remove split view
      const existing = document.getElementById('split-view-container');
      if (existing) existing.remove();
    }
  });

  function buildSplitView() {
    // Remove existing if any
    const existing = document.getElementById('split-view-container');
    if (existing) existing.remove();

    const rows = document.querySelectorAll('.table-wrap tbody tr');
    const incomeRows = [];
    const expenseRows = [];

    rows.forEach(row => {
      // Find the direction cell — check cells for 'income' or 'expense' text
      const cells = row.querySelectorAll('td');
      let direction = '';
      cells.forEach(cell => {
        const text = cell.textContent.trim().toLowerCase();
        if (text === 'income' || text === 'expense') direction = text;
      });
      if (direction === 'income') incomeRows.push(row.cloneNode(true));
      else expenseRows.push(row.cloneNode(true));
    });

    const container = document.createElement('div');
    container.id = 'split-view-container';
    container.className = 'split-view';

    container.innerHTML = '<div class="split-view-col"><h3>Income</h3><div class="table-wrap">' +
      '<table><thead>' + document.querySelector('.table-wrap thead').innerHTML + '</thead><tbody></tbody></table></div></div>' +
      '<div class="split-view-col"><h3>Expenses</h3><div class="table-wrap">' +
      '<table><thead>' + document.querySelector('.table-wrap thead').innerHTML + '</thead><tbody></tbody></table></div></div>';

    const [incomeBody, expenseBody] = container.querySelectorAll('tbody');
    incomeRows.forEach(r => incomeBody.appendChild(r));
    expenseRows.forEach(r => expenseBody.appendChild(r));

    if (incomeRows.length === 0) {
      incomeBody.innerHTML = '<tr><td colspan="99" class="text-center text-muted" style="padding:24px;">No income transactions</td></tr>';
    }
    if (expenseRows.length === 0) {
      expenseBody.innerHTML = '<tr><td colspan="99" class="text-center text-muted" style="padding:24px;">No expense transactions</td></tr>';
    }

    document.querySelector('.table-wrap').insertAdjacentElement('afterend', container);
  }
});
```

**CSS to add to `style.css`:**
```css
.split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.split-view-col h3 {
  margin-bottom: 12px;
}
```

---

## Critical Preservation Checklist

Before committing, verify:
- [ ] All existing list functionality works (show_all toggle, links)
- [ ] Detail page shows correct audit trail for voided transactions
- [ ] Detail page shows "replacement" link for voided originals (existing behavior)
- [ ] Detail page shows "corrected from" link for replacement transactions (new)
- [ ] Form still submits correctly for create and correct flows
- [ ] All form.js interactions preserved (direction toggle, category filter, VAT lock, card reminder, desc-required)
- [ ] Split view toggle only appears on desktop
- [ ] Split view correctly separates income/expense rows

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all existing tests must pass
```

- [ ] `#ID` column visible in transaction list
- [ ] "Corrected" badge shows for corrected transactions in show_all mode
- [ ] Detail page links correction pairs bidirectionally
- [ ] Income type field appears above category when direction is income
- [ ] Split view toggle works on desktop, hidden on mobile
- [ ] All existing tests pass
- [ ] No schema changes
- [ ] No business logic changes

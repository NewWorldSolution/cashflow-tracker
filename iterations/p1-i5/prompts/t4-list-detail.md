# I5-T4 — List, Detail & Void Styling

**Branch:** `feature/p1-i5/t4-list-detail-void` (from `feature/phase-1/iteration-5`)
**PR target:** `feature/phase-1/iteration-5`
**Depends on:** I5-T1 ✅ DONE

---

## Goal

Make transaction history readable and the audit trail easy to follow. Style the list, detail, and void templates using the CSS system from T1.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i5/prompt.md
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
static/style.css                         (T1 classes available)
```

---

## Allowed Files

```
app/templates/transactions/list.html      ← modify
app/templates/transactions/detail.html    ← modify
app/templates/transactions/void.html      ← modify
static/style.css                          ← extend (add page-specific classes only: .detail-grid, etc.)
```

Do NOT modify any other file.

---

## What to Implement

### 1. Transaction List (`list.html`)

**Layout:**
```html
{% extends "base.html" %}
{% block content %}
<div class="container">
  <div class="flex justify-between items-center mb-4">
    <h1>Transactions</h1>
    <a href="/transactions/new" class="btn btn-primary">+ New Transaction</a>
  </div>

  <!-- Show all toggle -->
  <div class="mb-4">
    {% if show_all %}
    <a href="/transactions/" class="btn btn-sm btn-secondary">Show Active Only</a>
    {% else %}
    <a href="/transactions/?show_all=true" class="btn btn-sm btn-secondary">Show All (incl. voided)</a>
    {% endif %}
  </div>

  {% if transactions %}
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Category</th>
          <th>Direction</th>
          <th class="text-right">Amount</th>
          <th>Payment</th>
          <th>Logged by</th>
          {% if show_all %}<th>Status</th>{% endif %}
        </tr>
      </thead>
      <tbody>
        {% for t in transactions %}
        <tr class="{{ 'row-voided' if not t.is_active else '' }}">
          <td><a href="/transactions/{{ t.id }}">{{ t.date }}</a></td>
          <td>{{ t.category_label }}</td>
          <td>{{ t.direction }}</td>
          <td class="text-right amount">{{ "{:,.2f}".format(t.amount) }}</td>
          <td>{{ t.payment_method }}</td>
          <td>{{ t.logged_by_username }}</td>
          {% if show_all %}
          <td>
            {% if t.is_active %}
            <span class="badge badge-active">Active</span>
            {% else %}
            <span class="badge badge-voided">Voided</span>
            {% endif %}
          </td>
          {% endif %}
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="empty-state">
    <p>No transactions yet.</p>
    <a href="/transactions/new" class="btn btn-primary mt-4">Create your first transaction</a>
  </div>
  {% endif %}
</div>
{% endblock %}
```

**Key formatting:**
- Amount: `{:,.2f}` — thousands separator + 2 decimals
- Voided rows: `.row-voided` class (50% opacity, strikethrough amount)
- Status badges: `.badge-active` (green) / `.badge-voided` (red)
- Responsive: `.table-wrap` for horizontal scroll on mobile
- Empty state when no transactions

### 2. Transaction Detail (`detail.html`)

**Layout — card-style:**
```html
{% extends "base.html" %}
{% block content %}
<div class="container-narrow">
  <a href="/transactions/" class="text-sm text-muted">← Back to list</a>
  <h1 class="mt-2">Transaction #{{ t.id }}</h1>

  <!-- Status badge -->
  {% if t.is_active %}
  <span class="badge badge-active">Active</span>
  {% else %}
  <span class="badge badge-voided">Voided</span>
  {% endif %}

  <!-- Transaction details card -->
  <div class="card mt-4">
    <dl class="detail-grid">
      <dt>Date</dt><dd>{{ t.date }}</dd>
      <dt>Direction</dt><dd>{{ t.direction }}</dd>
      <dt>Category</dt><dd>{{ t.category_label }}</dd>
      <dt>Amount (gross)</dt><dd>{{ "{:,.2f}".format(t.amount) }}</dd>
      <dt>VAT rate</dt><dd>{{ t.vat_rate }}%</dd>
      {% if t.direction == 'income' %}
      <dt>Income type</dt><dd>{{ t.income_type }}</dd>
      {% endif %}
      {% if t.direction == 'expense' %}
      <dt>VAT deductible</dt><dd>{{ t.vat_deductible_pct }}%</dd>
      {% endif %}
      <dt>Payment</dt><dd>{{ t.payment_method }}</dd>
      {% if t.description %}
      <dt>Description</dt><dd>{{ t.description }}</dd>
      {% endif %}
      <dt>Logged by</dt><dd>{{ t.logged_by_username }}</dd>
      <dt>Created at</dt><dd>{{ t.created_at }}</dd>
    </dl>
  </div>

  <!-- Audit trail (voided transactions only) -->
  {% if not t.is_active %}
  <div class="card mt-4" style="border-color: var(--color-destructive);">
    <h3>Void Details</h3>
    <dl class="detail-grid">
      <dt>Void reason</dt><dd>{{ t.void_reason }}</dd>
      <dt>Voided by</dt><dd>{{ t.voided_by_username }}</dd>
      {% if t.replacement_transaction_id %}
      <dt>Replaced by</dt>
      <dd><a href="/transactions/{{ t.replacement_transaction_id }}">#{{ t.replacement_transaction_id }}</a></dd>
      {% endif %}
    </dl>
  </div>
  {% endif %}

  <!-- Actions (active only) -->
  {% if t.is_active %}
  <div class="flex gap-3 mt-4">
    <a href="/transactions/{{ t.id }}/correct" class="btn btn-secondary">Correct</a>
    <a href="/transactions/{{ t.id }}/void" class="btn btn-destructive">Void</a>
  </div>
  {% endif %}
</div>
{% endblock %}
```

Add `.detail-grid` styles to `static/style.css`. Do not use inline `<style>` blocks — all styles belong in the shared stylesheet:
```css
.detail-grid { display: grid; grid-template-columns: 140px 1fr; gap: 8px 16px; }
.detail-grid dt { font-weight: 500; color: var(--color-muted-fg); }
.detail-grid dd { margin: 0; }
```

### 3. Void Confirmation (`void.html`)

**Warning-styled layout:**
```html
{% extends "base.html" %}
{% block content %}
<div class="container-narrow">
  <a href="/transactions/{{ t.id }}" class="text-sm text-muted">← Cancel</a>
  <h1 class="mt-2">Void Transaction</h1>

  <!-- Warning callout -->
  <div class="callout callout-warning mb-4">
    This action cannot be undone. The transaction will be marked as voided.
  </div>

  <!-- Transaction summary -->
  <div class="card mb-4" style="background: var(--color-hover);">
    <p><strong>{{ t.date }}</strong> — {{ t.category_label }} — {{ "{:,.2f}".format(t.amount) }}</p>
  </div>

  <!-- Errors -->
  {% if errors %}
  <div class="error-summary">
    <ul>
      {% for e in errors %}
      <li>{{ e }}</li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}

  <!-- Form -->
  <form method="post" action="/transactions/{{ t.id }}/void">
    <div class="form-group">
      <label class="form-label">Reason for voiding (required)</label>
      <textarea name="void_reason" rows="2" placeholder="Why is this transaction being voided?">{{ form_data.get('void_reason', '') }}</textarea>
    </div>
    <div class="flex gap-3 mt-4">
      <button type="submit" class="btn btn-destructive btn-lg">Void Transaction</button>
      <a href="/transactions/{{ t.id }}" class="btn btn-secondary btn-lg">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}
```

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all 94 existing tests must pass
```

- [ ] List table is styled with headers, hover, proper alignment
- [ ] Amounts show thousands separator and 2 decimal places
- [ ] Show all mode distinguishes active vs voided (badges + muted rows)
- [ ] Empty state shows when no transactions
- [ ] Detail shows all fields in a clean card layout
- [ ] Voided detail shows audit trail with red border card
- [ ] Void page shows warning callout and destructive button
- [ ] Mobile: table scrolls horizontally, detail and void are readable
- [ ] All existing links and actions still work

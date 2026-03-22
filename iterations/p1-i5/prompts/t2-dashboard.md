# I5-T2 — Real Dashboard

**Branch:** `feature/p1-i5/t2-dashboard` (from `feature/phase-1/iteration-5`)
**PR target:** `feature/phase-1/iteration-5`
**Depends on:** I5-T1 ✅ DONE

---

## Goal

Replace the placeholder dashboard with useful summary content. Users should see key numbers at a glance and have quick access to common actions.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i5/prompt.md
app/templates/dashboard.html
app/routes/dashboard.py
app/templates/base.html          (to see T1 CSS classes available)
static/style.css                 (available component classes)
```

---

## Allowed Files

```
app/templates/dashboard.html    ← rewrite
app/routes/dashboard.py         ← extend
```

Do NOT modify any other file.

---

## What to Implement

### 1. Extend `app/routes/dashboard.py`

Query and pass to template context:

```python
# Opening balance — settings table uses key-value pairs
opening_balance_row = db.execute("SELECT value FROM settings WHERE key = 'opening_balance'").fetchone()
as_of_date_row = db.execute("SELECT value FROM settings WHERE key = 'as_of_date'").fetchone()
opening_balance = opening_balance_row["value"] if opening_balance_row else None
as_of_date = as_of_date_row["value"] if as_of_date_row else None

# Transaction counts
active_count = db.execute("SELECT COUNT(*) FROM transactions WHERE is_active = 1").fetchone()[0]
voided_count = db.execute("SELECT COUNT(*) FROM transactions WHERE is_active = 0").fetchone()[0]

# Totals (active only)
total_income = db.execute(
    "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE is_active = 1 AND direction = 'income'"
).fetchone()[0]
total_expense = db.execute(
    "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE is_active = 1 AND direction = 'expense'"
).fetchone()[0]

# Recent 5 transactions (active only, with category label)
recent = db.execute(
    "SELECT t.id, t.date, t.amount, t.direction, c.label AS category_label, t.payment_method "
    "FROM transactions t JOIN categories c ON t.category_id = c.category_id "
    "WHERE t.is_active = 1 ORDER BY t.created_at DESC LIMIT 5"
).fetchall()
```

Pass all to template: `opening_balance`, `as_of_date`, `active_count`, `voided_count`, `total_income`, `total_expense`, `recent`.

### 2. Rewrite `app/templates/dashboard.html`

Use CSS classes from T1 (`static/style.css`). Layout:

**Summary cards (grid — 2x2 on desktop, stacked on mobile):**
```html
<div class="dashboard-grid">
  <div class="card">
    <div class="text-sm text-muted">Opening Balance</div>
    <div class="card-value">{{ opening_balance | default('Not set') }}</div>
    <div class="text-sm text-muted">as of {{ as_of_date | default('—') }}</div>
  </div>
  <div class="card">
    <div class="text-sm text-muted">Total Income</div>
    <div class="card-value">{{ "%.2f"|format(total_income) }}</div>
  </div>
  <div class="card">
    <div class="text-sm text-muted">Total Expenses</div>
    <div class="card-value">{{ "%.2f"|format(total_expense) }}</div>
  </div>
  <div class="card">
    <div class="text-sm text-muted">Transactions</div>
    <div class="card-value">{{ active_count }} active</div>
    <div class="text-sm text-muted">{{ voided_count }} voided</div>
  </div>
</div>
```

Add `.dashboard-grid` and `.card-value` styles inline or in a `<style>` block if T1 doesn't cover them. Prefer adding to `style.css` if scope allows.

**Quick actions:**
```html
<div class="flex gap-3 mt-4 mb-6">
  <a href="/transactions/new" class="btn btn-primary">+ New Transaction</a>
  <a href="/transactions/" class="btn btn-secondary">View All Transactions</a>
</div>
```

**Recent transactions (last 5):**
- Compact table with date, category, direction, amount, payment method
- Date links to detail (`/transactions/{{ t.id }}`)
- If no transactions: show empty state message
- Amount right-aligned

---

## Acceptance Check

```bash
ruff check app/routes/dashboard.py
pytest -v   # all 94 existing tests must pass
```

- [ ] Dashboard shows opening balance with as-of date
- [ ] Summary cards show real counts and totals
- [ ] Recent transactions table shows last 5
- [ ] Quick action links work
- [ ] Responsive: cards stack on mobile
- [ ] Empty state shows when no transactions exist

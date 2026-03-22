# QA Review — P1-I5: UI/UX Polish
**Reviewer:** QA agent
**Branch:** `feature/phase-1/iteration-5`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i5/tasks.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 5. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What this iteration was supposed to deliver

1. CSS system with custom properties, base element styles, and component classes
2. Improved base template with viewport meta, styled nav, flash message rendering
3. Real dashboard with opening balance, transaction counts/totals, recent 5, quick actions
4. Restructured transaction form with 5 sections, toggle buttons, and clear error display
5. Styled transaction list, detail, and void pages
6. Session-based flash messages after create, void, correct
7. 4 new flash tests (total 98)
8. Mobile-responsive layout on all pages
9. No business logic changes, no validation changes, no schema changes

---

## Review steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-5
git pull origin feature/phase-1/iteration-5
```

### Step 2 — Full suite and lint

```bash
pytest -v
# Expected: 98 passed, 0 failed

ruff check .
# Expected: clean
```

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected implementation files (all must be present):

```text
static/style.css
app/templates/base.html
app/templates/dashboard.html
app/routes/dashboard.py
app/templates/transactions/create.html
static/form.js
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
app/routes/transactions.py
app/main.py
tests/test_transactions.py
```

Iteration planning/docs files will also appear in the diff — this is expected:

```text
iterations/p1-i5/prompt.md
iterations/p1-i5/tasks.md
iterations/p1-i5/run.md
iterations/p1-i5/prompts/*.md
iterations/p1-i5/reviews/*.md
```

**Must NOT be modified (frozen files):**

```text
db/schema.sql
db/init_db.py
seed/categories.sql
seed/users.sql
app/services/validation.py
app/services/calculations.py
app/services/transaction_service.py
app/routes/auth.py
app/routes/settings.py
app/services/auth_service.py
tests/test_auth.py
tests/test_init_db.py
tests/test_validation.py
tests/test_calculations.py
```

Any frozen file appearing in the diff = `BLOCKED`.

### Step 4 — Architecture checks

```bash
# No business logic in templates
grep -rn "db\.\|execute\|sqlite3\|validate_\|void_transaction" app/templates/
# Expected: no output

# No stored derived values
grep -n "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" app/routes/transactions.py
# Pre-existing in GET list handler — verify not in any new INSERT

# Flash pop must be in Python, not Jinja2
grep -n "session.pop\|session\[" app/templates/
# Expected: no session manipulation in templates (render from context only)

# No hard deletes
grep -rn "DELETE FROM" app/
# Expected: no output
```

### Step 5 — Visual and functional checks

Verify by code inspection:

- [ ] CSS custom properties define all colors, spacing, typography
- [ ] Nav renders with brand, links, and active state
- [ ] SANDBOX banner still present in base.html
- [ ] Dashboard shows opening balance, counts, totals, recent 5
- [ ] Form has 5 sections with toggle buttons for direction
- [ ] Form preserves all JS selector IDs (income-type-row, vat-deductible-row, card-reminder, desc-required)
- [ ] Error summary box at top of form
- [ ] List table has formatted amounts, hover states, badges in show_all mode
- [ ] Detail page shows audit trail for voided transactions
- [ ] Void page has warning callout and destructive button
- [ ] Flash messages set in routes before redirect
- [ ] Flash messages rendered in base.html from context (not direct session access)
- [ ] Responsive: form-row collapses to single column, table scrolls horizontally

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

Full list with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Architecture Violations

If none: `None.`

### 5. Acceptance Criteria Check

- [PASS|FAIL] pytest: 98 passed, 0 failed
- [PASS|FAIL] ruff clean
- [PASS|FAIL] CSS system with custom properties
- [PASS|FAIL] base template: viewport meta, CSS link, nav, flash, SANDBOX
- [PASS|FAIL] dashboard shows real data
- [PASS|FAIL] form restructured into 5 sections with toggle buttons
- [PASS|FAIL] error display: summary box at top (no per-field string matching)
- [PASS|FAIL] list: formatted amounts, badges, empty state, responsive
- [PASS|FAIL] detail: card layout, audit trail
- [PASS|FAIL] void: warning callout, destructive button
- [PASS|FAIL] flash messages work and clear after one display
- [PASS|FAIL] 4 new flash tests pass
- [PASS|FAIL] no business logic changes (validation.py, calculations.py, transaction_service.py unchanged)
- [PASS|FAIL] no schema changes
- [PASS|FAIL] frozen files unchanged
- [PASS|FAIL] mobile responsive on all pages
- [PASS|FAIL] form.js: no business-rule changes — only minimal UI-state/class changes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

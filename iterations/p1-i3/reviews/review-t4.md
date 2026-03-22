# Review — I3-T4: List Template + form.js
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i3/t4-list-and-js`
**PR target:** `feature/phase-1/iteration-3`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/templates/transactions/list.html
static/form.js
```

### Required behaviour

- `list.html` extends `base.html`
- empty state when no transactions
- expected table columns including derived values
- `form.js` fetches `/categories`
- `form.js` manages conditional rows, reminder, and VAT locking

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i3/t4-list-and-js
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-3
# Expected: app/templates/transactions/list.html and static/form.js only
```

### Step 3 — list.html structure

```bash
grep -n "extends\|No transactions yet\|New transaction\|VAT amount\|Effective cost" app/templates/transactions/list.html
# Expected:
# {% extends "base.html" %}
# "New transaction" link present
# "No transactions yet." empty state
# "VAT amount" and "Effective cost" column headers
```

Verify all 8 expected table columns exist:

```bash
grep -n "Date\|Category\|Direction\|Amount\|VAT amount\|Effective cost\|Payment\|Logged by" app/templates/transactions/list.html
# Expected: all 8 present as <th> headers
```

### Step 4 — form.js: /categories fetch

```bash
grep -n "fetch.*categories\|categoryMap\|category_id" static/form.js
# Expected:
# fetch('/categories') call
# categoryMap built from response
# c.category_id or similar used as lookup key
```

### Step 5 — form.js: conditional row toggles

Read `static/form.js`. Verify direction change handler:
- `income-type-row` shown when direction = income
- `vat-deductible-row` shown when direction = expense
- On direction switch, dependent field is cleared

```bash
grep -n "income-type-row\|vat-deductible-row\|card-reminder\|desc-required" static/form.js
# Expected: all 4 IDs present
```

### Step 6 — form.js: vat_rate locking for internal income

This is a critical UI contract with Rule 8 (internal income → vat_rate must be 0). Verify:

```bash
grep -n "disabled\|internal\|vatRateField\|vat_rate" static/form.js
# Expected:
# vatRateField.disabled = true when income_type === 'internal'
# vatRateField.value = '0' set before disabling
# vatRateField.disabled = false when income_type switches away from 'internal'
```

Also verify that direction switching RELEASES the vat_rate lock:

```bash
grep -n "disabled = false" static/form.js
# Expected: appears in BOTH income_type change handler (non-internal) AND direction change handler
```

### Step 7 — form.js: category default VAT applies only when not locked

Read the category change handler. When income_type is 'internal' and vat_rate is locked (disabled), the category change must NOT override the locked value of 0.

```bash
grep -n "disabled\|vatRateField" static/form.js
# Expected: category change handler checks vatRateField.disabled before setting vatRateField.value
```

### Step 8 — form.js: vanilla JS only

```bash
grep -n "require\|import\|jquery\|jQuery\|React\|Vue\|angular" static/form.js
# Expected: no output — vanilla JS only
```

### Step 9 — form.js syntax check

```bash
node --check static/form.js
# Expected: no syntax errors, exit code 0
```

### Step 10 — No server-side logic in templates

Verify neither template contains any Python-like logic that should be in the route:

```bash
grep -n "vat_amount\|net_amount\|effective_cost\|Decimal\|calculate" app/templates/transactions/list.html
# Expected: only template variable rendering ({{ t.va }}, {{ t.ec }}) — no calculations
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every item implemented correctly with file and line references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/templates/transactions/list.html` and `static/form.js`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] list.html extends base.html
- [PASS|FAIL] list.html renders empty state ("No transactions yet.")
- [PASS|FAIL] list.html includes all 8 expected columns including VAT amount and Effective cost
- [PASS|FAIL] form.js fetches /categories and builds a lookup map
- [PASS|FAIL] form.js toggles income-type-row, vat-deductible-row, card-reminder, desc-required by exact IDs
- [PASS|FAIL] form.js sets vatRateField.disabled = true (not just hidden) for internal income
- [PASS|FAIL] form.js sets vatRateField.value = '0' before disabling
- [PASS|FAIL] form.js releases vat_rate lock on income_type change to non-internal
- [PASS|FAIL] form.js releases vat_rate lock on direction change
- [PASS|FAIL] form.js category change respects locked state (does not override disabled vat_rate)
- [PASS|FAIL] form.js uses vanilla JS only
- [PASS|FAIL] node --check static/form.js passes
- [PASS|FAIL] Scope: only list.html and form.js modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

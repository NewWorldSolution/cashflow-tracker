# Review — I3-T4: List Template + form.js
**Reviewer:** Claude Code
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
```

### Step 4 — form.js structure

Read `static/form.js` and verify:
- fetches `/categories`
- toggles `income-type-row`, `vat-deductible-row`, `card-reminder`, `desc-required`
- locks/unlocks `vat_rate` for internal/external income
- uses vanilla JS only

### Step 5 — Syntax check

```bash
node --check static/form.js
# Expected: no syntax errors
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
- [PASS|FAIL] list.html renders empty state correctly
- [PASS|FAIL] list.html includes expected columns including derived fields
- [PASS|FAIL] form.js fetches /categories and builds a lookup map
- [PASS|FAIL] form.js toggles all required UI elements by the agreed IDs
- [PASS|FAIL] form.js locks vat_rate for internal income and unlocks for external income
- [PASS|FAIL] form.js uses vanilla JS only
- [PASS|FAIL] node --check static/form.js passes
- [PASS|FAIL] Scope: only list.html and form.js modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

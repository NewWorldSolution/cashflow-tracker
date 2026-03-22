# Review — I3-T3: Create Template
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i3/t3-create-template`
**PR target:** `feature/phase-1/iteration-3`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/templates/transactions/create.html
```

### Required behaviour

- extends `base.html`
- posts to `/transactions/new`
- renders all required form fields
- renders errors list above the form
- preserves values via `form_data`
- includes exact IDs required by `form.js`

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i3/t3-create-template
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-3
# Expected: app/templates/transactions/create.html only
```

### Step 3 — Required fields and IDs

```bash
grep -n 'name="date"\|name="direction"\|name="amount"\|name="category_id"\|name="payment_method"\|name="vat_rate"\|name="income_type"\|name="vat_deductible_pct"\|name="description"\|card-reminder\|income-type-row\|vat-deductible-row\|desc-required' app/templates/transactions/create.html
```

### Step 4 — Structure checks

Verify:
- `{% extends "base.html" %}`
- error block above the form
- amount label text exactly `Enter gross amount (VAT included)`
- `<script src="/static/form.js">`

### Step 5 — Template load check

```bash
python -c "
from fastapi.templating import Jinja2Templates
t = Jinja2Templates(directory='app/templates')
t.get_template('transactions/create.html')
print('template loads ok')
"
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
  file: app/templates/transactions/create.html:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/templates/transactions/create.html`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] Template file exists
- [PASS|FAIL] Extends base.html
- [PASS|FAIL] Form posts to /transactions/new
- [PASS|FAIL] All required fields are present
- [PASS|FAIL] Error list appears above the form
- [PASS|FAIL] form_data preservation is implemented
- [PASS|FAIL] Amount label text matches exactly
- [PASS|FAIL] Required form.js IDs all exist
- [PASS|FAIL] Script include points to /static/form.js
- [PASS|FAIL] Template loads without Jinja2 errors
- [PASS|FAIL] Scope: only app/templates/transactions/create.html modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

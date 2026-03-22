# Review — I3-T3: Create Template
**Reviewer:** Codex
**Implemented by:** Claude Code
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
app/templates/transactions/create.html    ← only this file
```

### Required behaviour

- Extends `base.html`
- All 9 form fields with input preservation via `form_data.get()`
- All 4 required element IDs with `display:none` initial state
- Amount label text exactly: `"Enter gross amount (VAT included)"`
- `<script src="/static/form.js">` at bottom of content block
- Inline error list when `errors` is non-empty

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
# No __init__.py, no Python files, no other templates
```

### Step 3 — Template loads without error

```bash
python -c "
import os; os.environ['SECRET_KEY'] = 'test'
from fastapi.templating import Jinja2Templates
t = Jinja2Templates(directory='app/templates')
tmpl = t.get_template('transactions/create.html')
print('template loads ok')
"
```

### Step 4 — extends base.html

```bash
grep -n "extends" app/templates/transactions/create.html
# Expected: {% extends "base.html" %}
```

### Step 5 — Required element IDs with display:none

All four IDs must exist with `display:none` initial state:

```bash
grep -n "card-reminder\|income-type-row\|vat-deductible-row\|desc-required" app/templates/transactions/create.html
# Expected: all four IDs present
```

For each ID, verify `display:none` is set (inline style or class). Missing ID = `CHANGES REQUIRED`. Missing `display:none` = field will be visible on initial render = major issue.

```bash
grep -n "display:none\|display: none" app/templates/transactions/create.html
# Expected: at least 4 occurrences (one per required hidden element)
```

### Step 6 — form_data.get() preservation on all fields

Read the template. Every form field must use `form_data.get('field_name', ...)` to restore its value on re-render. A field that hardcodes an empty default without `form_data.get()` will lose user input on validation failure.

```bash
grep -n "form_data" app/templates/transactions/create.html
# Expected: multiple occurrences — one per field
# Cross-check against the 9 required fields:
# date, direction, amount, category_id, payment_method, vat_rate,
# income_type, vat_deductible_pct, description
```

Verify specifically that `direction` radio buttons use `form_data.get('direction')` for the `checked` condition.

### Step 7 — Amount label text

```bash
grep -n "gross amount\|VAT included" app/templates/transactions/create.html
# Expected: "Enter gross amount (VAT included)" present
```

If missing or paraphrased: minor (confusing UX — user may not know to enter gross).

### Step 8 — Card reminder text

```bash
grep -n "card-reminder" app/templates/transactions/create.html
# Must contain the element; verify the text inside matches:
# "Log gross amount. Card commission is logged separately at month end from terminal invoice"
```

### Step 9 — vat_rate options

```bash
grep -n "vat_rate" app/templates/transactions/create.html
# Expected: select element with options 0, 5, 8, 23
grep -n "value=\"0\"\|value=\"5\"\|value=\"8\"\|value=\"23\"" app/templates/transactions/create.html
```

### Step 10 — form.js script tag

```bash
grep -n "form.js" app/templates/transactions/create.html
# Expected: <script src="/static/form.js"></script>
# Must be inside {% block content %} at the bottom, NOT in <head>
```

### Step 11 — Error list

```bash
grep -n "{% if errors %}\|class=\"errors\"\|{% for error in errors %}" app/templates/transactions/create.html
# Expected: {% if errors %} block with loop rendering each error
```

### Step 12 — Submit button and form action

```bash
grep -n "Save transaction\|action=\"/transactions/new\"\|method=\"post\"" app/templates/transactions/create.html
# Expected: all three present
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

Files modified outside `app/templates/transactions/create.html`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] Template loads without Jinja2 errors
- [PASS|FAIL] extends base.html
- [PASS|FAIL] id="card-reminder" present with display:none
- [PASS|FAIL] id="income-type-row" present with display:none
- [PASS|FAIL] id="vat-deductible-row" present with display:none
- [PASS|FAIL] id="desc-required" present with display:none
- [PASS|FAIL] All 9 fields render with form_data.get() preservation
- [PASS|FAIL] Amount label text is "Enter gross amount (VAT included)"
- [PASS|FAIL] vat_rate select has options 0, 5, 8, 23
- [PASS|FAIL] <script src="/static/form.js"> present at bottom of content block
- [PASS|FAIL] Error list renders when errors is non-empty
- [PASS|FAIL] Submit button text is "Save transaction"
- [PASS|FAIL] Scope: only create.html modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

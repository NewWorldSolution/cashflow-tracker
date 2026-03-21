# Review — I1-T4: Base Template + UI
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i1/t4-ui`
**PR target:** `feature/phase-1/iteration-1`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/templates/base.html                        ← base layout with mandatory SANDBOX banner
app/templates/settings/opening_balance.html    ← opening balance form
```

Two files only. No Python files. No JavaScript files.

### Required behaviour

1. `base.html` — SANDBOX banner visible on every page; exact wording: "SANDBOX — this is a test environment. Data may be discarded."
2. `base.html` — `{% block content %}{% endblock %}` for child templates
3. `opening_balance.html` — extends `base.html`
4. Form: method POST, action `/settings/opening-balance`
5. Fields: `opening_balance` (number, step=0.01, min=0.01) and `as_of_date` (date input)
6. Fields pre-populated from context: `current_balance` and `current_date`
7. Error shown inline (above the form) when `error` context variable is not None
8. Form values preserved on error — input not reset
9. No JavaScript files created
10. No Python files modified

---

## Architecture principles to check

| # | Principle |
|---|-----------|
| 5 | No silent failures — errors must be visible inline, not suppressed |
| 2 | No LLM or dynamic logic in templates — Jinja2 only |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i1/t4-ui
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-1
# Expected: app/templates/base.html, app/templates/settings/opening_balance.html only
```

Any Python file = scope violation. Any `.js` file = scope violation.

### Step 3 — SANDBOX banner

Read `app/templates/base.html`.

```bash
grep -n "SANDBOX" app/templates/base.html
# Expected: the exact wording present
```

Check:
- Banner is visible by default (not hidden, not commented out)
- Wording contains "SANDBOX" and "test environment" and "Data may be discarded"
- Banner is inside `base.html`, not in the child template

### Step 4 — Template inheritance

```bash
grep -n "extends\|block content" app/templates/settings/opening_balance.html
# Expected: {% extends "base.html" %} and {% block content %}
```

### Step 5 — Form action and method

```bash
grep -n "form\|action\|method" app/templates/settings/opening_balance.html
# Expected: method="post" action="/settings/opening-balance"
```

### Step 6 — Field names

```bash
grep -n "name=" app/templates/settings/opening_balance.html
# Expected: name="opening_balance" and name="as_of_date"
```

Field names must match exactly what `app/routes/settings.py` expects.

### Step 7 — Error display

Read the opening_balance.html template. Verify:
- Error block is conditional: `{% if error %}`
- Shown above the form fields
- Uses the `error` context variable

```bash
grep -n "error\|if error" app/templates/settings/opening_balance.html
```

### Step 8 — Value preservation

Read the form fields. Verify:
- `opening_balance` input has `value="{{ current_balance ... }}"` (preserves submitted value)
- `as_of_date` input has `value="{{ current_date }}"` (preserves submitted value)

### Step 9 — No JavaScript

```bash
find . -name "*.js" -newer app/templates/base.html 2>/dev/null
# Expected: no output
grep -n "<script" app/templates/base.html app/templates/settings/opening_balance.html
# Expected: no output (or only if referencing a static JS file from a prior task — but no JS was in any prior task)
```

### Step 10 — Render test

```bash
SECRET_KEY=test-key python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app)
r = client.get('/settings/opening-balance')
print(r.status_code)  # Expected: 200
assert 'SANDBOX' in r.text, 'SANDBOX banner missing from response'
assert 'opening_balance' in r.text, 'opening_balance field missing'
print('Render test: OK')
"
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

File and line references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: app/templates/...:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/templates/base.html` and `app/templates/settings/opening_balance.html`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] SANDBOX banner in base.html with exact required wording
- [PASS|FAIL] Banner visible by default (not hidden)
- [PASS|FAIL] opening_balance.html extends base.html
- [PASS|FAIL] Form: method=POST action=/settings/opening-balance
- [PASS|FAIL] Fields: name=opening_balance (number) and name=as_of_date (date)
- [PASS|FAIL] Fields pre-populated from current_balance and current_date context vars
- [PASS|FAIL] Error shown inline when error context var is not None
- [PASS|FAIL] No JavaScript files created
- [PASS|FAIL] No Python files modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

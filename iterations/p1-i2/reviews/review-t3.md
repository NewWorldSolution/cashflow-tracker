# Review — I2-T3: Login Template
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i2/t3-login-template`
**PR target:** `feature/phase-1/iteration-2`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/templates/auth/login.html   ← login form: username + password + Sign in
```

### Required template behaviour

| Requirement | Detail |
|-------------|--------|
| Extends | `base.html` — SANDBOX banner inherited |
| Form | `method="post"`, `action="/auth/login"` |
| Username field | `type="text"`, `name="username"`, value repopulated from `{{ username or '' }}` |
| Password field | `type="password"`, `name="password"` — never `type="text"` |
| Submit | Button text: "Sign in" |
| Error display | `{% if error %}` block, visible above form when error is set |
| Error CSS class | Uses `.error` class from base.html |
| JavaScript | None |
| External CSS | None |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i2/t3-login-template
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-2
# Expected: app/templates/auth/login.html only
```

### Step 3 — File exists

```bash
ls app/templates/auth/login.html
```

### Step 4 — Password field type

```bash
grep -n "type=" app/templates/auth/login.html
```

Verify:
- Username: `type="text"` (or no type attr — defaults to text)
- Password: `type="password"` — never `type="text"`

If password field has `type="text"`: `CHANGES REQUIRED` (critical security issue).

### Step 5 — Form action

```bash
grep -n "action\|method" app/templates/auth/login.html
```

- `method="post"` (or `method="POST"`)
- `action="/auth/login"`

### Step 6 — Extends base.html

```bash
grep -n "extends" app/templates/auth/login.html
# Expected: {% extends "base.html" %}
```

If missing: SANDBOX banner will not appear.

### Step 7 — Error display

```bash
grep -n "error" app/templates/auth/login.html
```

Verify:
- `{% if error %}` block present
- Error rendered inside a `.error` CSS class element
- Error block appears before or above the form inputs (not below)

### Step 8 — Username preserved on error

```bash
grep -n "username" app/templates/auth/login.html
```

Verify `value="{{ username or '' }}"` (or equivalent) on the username input.

### Step 9 — Password NOT preserved

Read the password input field. Verify it has no `value` attribute — password must be cleared on reload.

### Step 10 — No JavaScript or external resources

```bash
grep -n "<script\|<link\|cdn\|javascript" app/templates/auth/login.html
# Expected: no output
```

### Step 11 — Jinja2 syntax check (render test)

```bash
python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app, follow_redirects=False)
client.post('/settings/opening-balance', data={'opening_balance': '50000', 'as_of_date': '2026-01-01'})
r = client.get('/auth/login')
assert r.status_code == 200, f'Expected 200, got {r.status_code}'
assert 'Sign in' in r.text, 'Submit button text missing'
assert 'SANDBOX' in r.text, 'SANDBOX banner missing — base.html not extended'
print('login template render: OK')
"
```

Note: requires T2 (auth routes) to be merged first. If T2 is not yet on the iteration branch, verify by reading the template source directly instead.

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
  file: app/templates/auth/login.html:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/templates/auth/login.html`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] Template file exists at app/templates/auth/login.html
- [PASS|FAIL] Extends base.html (SANDBOX banner inherited)
- [PASS|FAIL] Form method="post" and action="/auth/login"
- [PASS|FAIL] Username field: type="text", name="username"
- [PASS|FAIL] Password field: type="password" — NOT type="text"
- [PASS|FAIL] Submit button text: "Sign in"
- [PASS|FAIL] Error block: {% if error %}, uses .error CSS class, positioned above form inputs
- [PASS|FAIL] Username value preserved on error: value="{{ username or '' }}"
- [PASS|FAIL] Password has no value attribute (cleared on reload)
- [PASS|FAIL] No JavaScript
- [PASS|FAIL] No external CSS frameworks
- [PASS|FAIL] Scope: only app/templates/auth/login.html modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

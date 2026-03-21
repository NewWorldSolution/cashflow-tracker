# I2-T3 — Login Template
**Agent:** Codex
**Branch:** `feature/p1-i2/t3-login-template`
**PR target:** `feature/phase-1/iteration-2`

---

## Before starting — read these files in order

```
CLAUDE.md                                        ← architecture rules — read first
iterations/p1-i2/tasks.md                       ← confirm I2-T1 is ✅ DONE, set I2-T3 to IN PROGRESS
skills/cash-flow/error_handling/SKILL.md         ← error messages surface inline, never via flash or alert()
```

**Dependency:** I2-T1 must be ✅ DONE (establishes the error message contract). If it is not, stop and wait.
This task runs in parallel with I2-T2. I2-T2 does not need to be DONE before starting.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-2
git worktree add -b feature/p1-i2/t3-login-template ../cashflow-tracker-i2t3 feature/phase-1/iteration-2
cd ../cashflow-tracker-i2t3
```

---

## What already exists

```
app/templates/base.html    ← base layout with SANDBOX banner — extends this
```

---

## What to build

### Allowed files (this task only)

```
app/templates/auth/login.html   ← new: login form
```

No Python files. No `__init__.py` — template directories are not Python packages.
Do not modify `app/templates/base.html` — nav/logout update is T4.

---

## app/templates/auth/login.html — implement exactly this

```html
{% extends "base.html" %}

{% block title %}Sign in — cashflow-tracker{% endblock %}

{% block content %}
<h1>Sign in</h1>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="post" action="/auth/login">
    <div>
        <label for="username">Username</label><br>
        <input
            type="text"
            id="username"
            name="username"
            value="{{ username or '' }}"
            autocomplete="username"
            required
        >
    </div>
    <div>
        <label for="password">Password</label><br>
        <input
            type="password"
            id="password"
            name="password"
            autocomplete="current-password"
            required
        >
    </div>
    <div>
        <button type="submit">Sign in</button>
    </div>
</form>
{% endblock %}
```

---

## Template requirements

| Requirement | Detail |
|-------------|--------|
| Extends | `base.html` — SANDBOX banner inherited automatically |
| Form action | `POST /auth/login` |
| Username field | `type="text"`, `name="username"`, `id="username"` |
| Password field | `type="password"`, `name="password"` — **never** `type="text"` |
| Submit button | Label: "Sign in" |
| Error display | `{% if error %}` block above the form, uses `.error` CSS class from base.html |
| Username preserved | `value="{{ username or '' }}"` — repopulated on error |
| Password cleared | No `value` attribute on password field — browser clears it on reload |
| JavaScript | None required — pure HTML form |
| External CSS | None — consistent with project stack |

---

## Error message contract (from I2-T1 auth_service)

The route handler (T2) passes an `error` variable to this template:

| Scenario | `error` value |
|----------|--------------|
| No error (initial GET) | `None` |
| Either field empty | `"Username and password are required"` |
| Wrong username | `"Invalid credentials"` |
| Wrong password | `"Invalid credentials"` |

The template must render the error message exactly as passed — do not hardcode or reformat it.
The same message for wrong username and wrong password is intentional — it does not reveal which field failed.

---

## Acceptance check

```bash
# Template renders without Jinja2 errors when error=None
python -c "
import os
os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app)
# Must post opening balance first so gate passes
client.post('/settings/opening-balance', data={'opening_balance': '50000', 'as_of_date': '2026-01-01'})
r = client.get('/auth/login')
assert r.status_code == 200, f'Expected 200, got {r.status_code}'
assert 'Sign in' in r.text
assert 'SANDBOX' in r.text
print('login template: OK')
"
```

Note: this check requires T2 (auth routes) to be merged into the iteration branch. If T2 is not yet merged, verify by manual Jinja2 render inspection instead.

---

## Commit and PR

```bash
git add app/templates/auth/login.html
git commit -m "feat: login form template with inline error and SANDBOX banner (I2-T3)"
git push -u origin feature/p1-i2/t3-login-template
gh pr create \
  --base feature/phase-1/iteration-2 \
  --head feature/p1-i2/t3-login-template \
  --title "I2-T3: Login template" \
  --body "Login form: username (text) + password (password) + Sign in. Extends base.html. Inline error above form. Username preserved on error, password cleared. No JS, no external CSS."
```

Update `iterations/p1-i2/tasks.md` — set I2-T3 to ✅ DONE with note: "auth/login.html: form with inline error, username preserved, extends base.html."

---

## Acceptance checklist

- [ ] Template file exists at `app/templates/auth/login.html`
- [ ] Extends `base.html`
- [ ] SANDBOX banner inherited (no need to repeat it in the template)
- [ ] Form `method="post"` and `action="/auth/login"`
- [ ] Username field: `type="text"`, `name="username"`, value repopulated on error
- [ ] Password field: `type="password"`, `name="password"` — **not** `type="text"`
- [ ] Submit button text: "Sign in"
- [ ] Error block uses `{% if error %}` — renders only when error is set
- [ ] Error displayed above the form, using `.error` CSS class
- [ ] No JavaScript
- [ ] No external CSS frameworks
- [ ] Ruff clean (no Python files, but ruff will check any .py in scope)

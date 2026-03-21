# I1-T4 — Base Template + UI
**Agent:** Claude Code
**Branch:** `feature/p1-i1/t4-ui`
**PR target:** `feature/phase-1/iteration-1`

---

## Before starting — read these files in order

```
CLAUDE.md                                    ← architecture rules
iterations/p1-i1/tasks.md                   ← confirm I1-T2 AND I1-T3 are both DONE
app/main.py                                  ← understand template directory and app structure
app/routes/settings.py                       ← understand the form action, field names, and error variable
skills/cash-flow/error_handling/SKILL.md     ← inline errors, form must not reset
```

Both I1-T2 and I1-T3 must be DONE before you start. If either is not DONE, stop and wait.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-1

# Confirm both T2 and T3 are merged
python -c "from app.main import get_db; print('T2 OK')"
python -c "from app.routes.settings import router; print('T3 OK')"

git worktree add -b feature/p1-i1/t4-ui ../cashflow-tracker-t4 feature/phase-1/iteration-1
cd ../cashflow-tracker-t4
```

---

## What already exists (do not recreate)

```
app/main.py             ← Jinja2Templates configured with directory="app/templates"
app/routes/settings.py  ← GET/POST /settings/opening-balance
                           Template context: request, current_balance, current_date, error (str | None)
```

The template context variables from `settings.py`:
- `request` — always present (required by FastAPI Jinja2 templates)
- `current_balance` — float or None (pre-populate amount field if set)
- `current_date` — str in YYYY-MM-DD format (pre-populate date field)
- `error` — str or None (show inline if not None)

---

## What to build

### Allowed files (this task only)

```
app/templates/base.html                        ← new: base layout with SANDBOX banner
app/templates/settings/opening_balance.html    ← new: opening balance form
```

No Python files. No JavaScript. No CSS files (inline styles only if needed for the banner).

---

## app/templates/base.html

Requirements:
- SANDBOX banner — **mandatory on every page** — wording exactly: `"SANDBOX — this is a test environment. Data may be discarded."`
- Banner must be visible and clearly distinguishable (use a style or class — not hidden)
- Standard HTML5 boilerplate (`<!DOCTYPE html>`, `<meta charset>`, `<meta viewport>`)
- `{% block content %}{% endblock %}` for child templates
- Title block: `{% block title %}cashflow-tracker{% endblock %}`
- No JavaScript framework, no external CSS CDN — keep it minimal for now

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}cashflow-tracker{% endblock %}</title>
    <style>
        .sandbox-banner {
            background: #ff4444;
            color: white;
            text-align: center;
            padding: 8px;
            font-weight: bold;
            font-size: 14px;
        }
        /* minimal base styles only */
        body { font-family: sans-serif; margin: 0; padding: 0; }
        main { max-width: 900px; margin: 24px auto; padding: 0 16px; }
        .error { color: #cc0000; background: #fff0f0; border: 1px solid #ffcccc; padding: 8px; border-radius: 4px; margin-bottom: 12px; }
    </style>
</head>
<body>
    <div class="sandbox-banner">
        SANDBOX — this is a test environment. Data may be discarded.
    </div>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

---

## app/templates/settings/opening_balance.html

Requirements:
- Extends `base.html`
- Form method POST, action `/settings/opening-balance`
- Two fields: `opening_balance` (number, step 0.01) and `as_of_date` (date input)
- Error shown inline when `error` is not None — above the form, inside `.error` class
- Input fields pre-populated with `current_balance` and `current_date` from template context
- Submit button
- No JavaScript required

```html
{% extends "base.html" %}

{% block title %}Opening Balance Setup — cashflow-tracker{% endblock %}

{% block content %}
<h1>Opening Balance Setup</h1>
<p>Set the starting cash position before logging transactions.</p>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="post" action="/settings/opening-balance">
    <div>
        <label for="opening_balance">Opening balance (PLN)</label><br>
        <input
            type="number"
            id="opening_balance"
            name="opening_balance"
            step="0.01"
            min="0.01"
            value="{{ current_balance if current_balance else '' }}"
            required
        >
    </div>
    <br>
    <div>
        <label for="as_of_date">As of date</label><br>
        <input
            type="date"
            id="as_of_date"
            name="as_of_date"
            value="{{ current_date }}"
            required
        >
    </div>
    <br>
    <button type="submit">Save opening balance</button>
</form>
{% endblock %}
```

---

## Rules

- **SANDBOX banner** must appear on every page that extends `base.html`. It is not optional decoration.
- **Error display** — when `error` is set (not None), show it above the form fields. The form values must be preserved — use the context variables to pre-populate.
- **No JavaScript** — plain HTML form. No JS files in this task.
- **No external CSS or fonts** — keep the template self-contained with minimal inline styles.
- **No modification to Python files** — this task is templates only.

---

## Verify manually after implementing

```bash
# Start the app
SECRET_KEY=test-key python -m uvicorn app.main:app --reload

# Open http://localhost:8000/settings/opening-balance in a browser
# Check:
# 1. SANDBOX banner visible at the top
# 2. Form renders with both fields
# 3. Submit valid data → redirects to /
# 4. Submit invalid data (e.g. -100) → returns to form with error, values preserved
```

---

## Commit and PR

```bash
git add app/templates/
git commit -m "feat: base template with SANDBOX banner and opening balance form (I1-T4)"
git push -u origin feature/p1-i1/t4-ui
gh pr create \
  --base feature/phase-1/iteration-1 \
  --head feature/p1-i1/t4-ui \
  --title "I1-T4: Base template + opening balance UI" \
  --body "base.html with mandatory SANDBOX banner. opening_balance.html form with inline error display and value preservation on failure."
```

Update `iterations/p1-i1/tasks.md` — set I1-T4 to ✅ DONE.

---

## Acceptance checklist

- [ ] SANDBOX banner visible when loading `/settings/opening-balance`
- [ ] Banner wording exact: "SANDBOX — this is a test environment. Data may be discarded."
- [ ] Form submits to POST `/settings/opening-balance`
- [ ] `opening_balance` field pre-populated from `current_balance` context variable
- [ ] `as_of_date` field pre-populated from `current_date` context variable
- [ ] Error message shown inline when `error` context variable is not None
- [ ] Form values preserved on 400 response (not reset)
- [ ] No JavaScript files created
- [ ] No Python files modified
- [ ] Ruff clean (no Python files to check — confirm `ruff check .` exits 0)

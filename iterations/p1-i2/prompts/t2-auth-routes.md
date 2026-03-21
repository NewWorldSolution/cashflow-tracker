# I2-T2 — Auth Routes + Placeholder Dashboard
**Agent:** Claude Code
**Branch:** `feature/p1-i2/t2-auth-routes`
**PR target:** `feature/phase-1/iteration-2`

---

## Before starting — read these files in order

```
CLAUDE.md                                        ← architecture rules — read first
iterations/p1-i2/tasks.md                       ← confirm I2-T1 is ✅ DONE, set I2-T2 to IN PROGRESS
skills/cash-flow/schema/SKILL.md                 ← users table structure
skills/cash-flow/auth_logic/SKILL.md             ← session identity rules
skills/cash-flow/error_handling/SKILL.md         ← no silent failures, inline errors only
```

**Dependency:** I2-T1 must be ✅ DONE before starting. If it is not, stop and wait.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-2
git worktree add -b feature/p1-i2/t2-auth-routes ../cashflow-tracker-i2t2 feature/phase-1/iteration-2
cd ../cashflow-tracker-i2t2
```

---

## What already exists

```
app/main.py                   ← provides get_db() dependency — use it in routes
app/services/auth_service.py  ← T1 deliverable: get_user_by_username, verify_password, get_current_user
app/templates/base.html       ← base layout (no nav yet — T4 adds nav/logout)
```

Verify T1 imports before writing a line of code:

```bash
python -c "from app.services.auth_service import get_user_by_username, verify_password, get_current_user; print('T1 ok')"
```

---

## What to build

### Allowed files (this task only)

```
app/routes/auth.py          ← new: GET/POST /auth/login + POST /auth/logout
app/routes/dashboard.py     ← new: GET / placeholder dashboard
app/templates/dashboard.html ← new: minimal dashboard template
```

Do not modify `app/main.py` — router registration is T4's job.
Do not create `app/templates/auth/login.html` — that is T3 (Codex).

---

## app/routes/auth.py — implement exactly this

```python
import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.main import get_db
from app.services.auth_service import get_current_user, get_user_by_username, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/auth/login", response_class=HTMLResponse)
async def get_login(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> HTMLResponse:
    """Render login form. Redirect to / if already authenticated."""
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@router.post("/auth/login")
async def post_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """Validate credentials, create session, redirect to /."""

    def render_error(msg: str) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": msg, "username": username},
            status_code=401,
        )

    # Step 1 — empty field check (exact error message required)
    if not username or not password:
        return render_error("Username and password are required")

    # Step 2 — user lookup
    user = get_user_by_username(db, username)
    if user is None:
        return render_error("Invalid credentials")

    # Step 3 — password check
    if not verify_password(password, user["password_hash"]):
        return render_error("Invalid credentials")

    # Step 4 — session fixation prevention: clear before setting
    request.session.clear()
    request.session["user_id"] = user["id"]  # integer, never username string

    return RedirectResponse(url="/", status_code=302)


@router.post("/auth/logout")
async def post_logout(request: Request):
    """Clear session and redirect to login. Must be POST — GET logout is a security issue."""
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)
```

---

## app/routes/dashboard.py — implement exactly this

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request) -> HTMLResponse:
    """Placeholder dashboard — confirms authenticated access.

    AuthGate middleware guarantees request.state.user is set before this
    handler is called. No DB queries needed for this placeholder.
    Full dashboard content is out of scope for P1-I2.
    """
    return templates.TemplateResponse(request, "dashboard.html", {})
```

---

## app/templates/dashboard.html — implement exactly this

```html
{% extends "base.html" %}

{% block title %}Dashboard — cashflow-tracker{% endblock %}

{% block content %}
<h1>Dashboard</h1>
<p>Logged in as: <strong>{{ request.state.user["username"] }}</strong></p>
{% endblock %}
```

---

## Login POST logic — exact sequence

This is already implemented in the `post_login` function above. For reference:

```
1. Read username + password from form data
2. If either empty → render form with error: "Username and password are required" (401)
3. get_user_by_username(db, username)
4. If None → render form with error: "Invalid credentials" (401)
5. verify_password(password, user["password_hash"])
6. If False → render form with error: "Invalid credentials" (401)
7. session.clear()              ← session fixation prevention
8. session["user_id"] = user["id"]  ← integer, never username string
9. Redirect to / (302)
```

**Never** reveal which field caused login failure — "Invalid credentials" is the only message for both wrong username and wrong password.

---

## Acceptance check

```bash
python -c "from app.routes.auth import router; print('auth router ok')"
python -c "from app.routes.dashboard import router; print('dashboard router ok')"
```

---

## Commit and PR

```bash
git add app/routes/auth.py app/routes/dashboard.py app/templates/dashboard.html
git commit -m "feat: login/logout routes and placeholder dashboard (I2-T2)"
git push -u origin feature/p1-i2/t2-auth-routes
gh pr create \
  --base feature/phase-1/iteration-2 \
  --head feature/p1-i2/t2-auth-routes \
  --title "I2-T2: Auth routes + placeholder dashboard" \
  --body "GET/POST /auth/login, POST /auth/logout, GET /. Session fixation prevention. Identical error messages for wrong username and wrong password. Dashboard placeholder shows authenticated username."
```

Update `iterations/p1-i2/tasks.md` — set I2-T2 to ✅ DONE with note: "auth.py: login/logout; dashboard.py: GET /; dashboard.html: placeholder."

---

## Acceptance checklist

Verify these on your own branch, without waiting for T3 or T4:

- [ ] Auth and dashboard routers import without error
- [ ] `get_login` handler redirects to `/` when `get_current_user` returns a user (read code — not end-to-end testable until T3 + T4 merge)
- [ ] `POST /auth/login` with valid credentials redirects to `/` (302)
- [ ] `POST /auth/login` with empty fields returns 401 with "Username and password are required"
- [ ] `POST /auth/login` with wrong username returns 401 with "Invalid credentials"
- [ ] `POST /auth/login` with wrong password returns 401 with "Invalid credentials"
- [ ] Error message is identical for wrong username and wrong password
- [ ] `session.clear()` called before `session["user_id"] = user["id"]` on login
- [ ] `session["user_id"]` stores integer (`user["id"]`), never a username string
- [ ] `POST /auth/logout` clears session and redirects to `/auth/login`
- [ ] `app/main.py` not modified
- [ ] Ruff clean

## Post-merge verification (after T3 and T4 merge into iteration branch)

- [ ] `GET /auth/login` returns 200 when no session and opening balance is set
- [ ] `GET /` with valid session returns 200 and renders dashboard.html

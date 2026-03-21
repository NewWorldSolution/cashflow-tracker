# I2-T4 — Middleware + Base Template
**Agent:** Claude Code
**Branch:** `feature/p1-i2/t4-middleware`
**PR target:** `feature/phase-1/iteration-2`

---

## Before starting — read these files in order

```
CLAUDE.md                                        ← architecture rules — read first
iterations/p1-i2/tasks.md                       ← confirm I2-T2 and I2-T3 are both ✅ DONE, set I2-T4 to IN PROGRESS
skills/cash-flow/auth_logic/SKILL.md             ← session identity rules
skills/cash-flow/error_handling/SKILL.md         ← no silent failures
```

**Dependencies:** I2-T2 AND I2-T3 must both be ✅ DONE before starting. If either is not, stop and wait.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-2
git worktree add -b feature/p1-i2/t4-middleware ../cashflow-tracker-i2t4 feature/phase-1/iteration-2
cd ../cashflow-tracker-i2t4
```

---

## What already exists (verify before modifying)

```
app/main.py                    ← modify: replace OpeningBalanceGate with AuthGate, register routers
app/templates/base.html        ← modify: add nav with logout button and username display
app/services/auth_service.py   ← T1: get_opening_balance, get_current_user — call these, never reimplement
app/routes/auth.py             ← T2: auth router to register
app/routes/dashboard.py        ← T2: dashboard router to register
app/templates/auth/login.html  ← T3: login template (must render correctly after base.html update)
```

Verify all dependencies before starting:

```bash
python -c "
from app.services.auth_service import get_opening_balance, get_current_user
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
import os; os.path.exists('app/templates/auth/login.html') and print('all deps ok')
"
```

---

## What to build

### Allowed files (this task only)

```
app/main.py              ← replace OpeningBalanceGate with AuthGate; register auth + dashboard routers
app/templates/base.html  ← add nav with logout button and logged-in username
```

No other files. Do not create new files. Do not modify routes or service layer.

---

## app/main.py — exact changes required

### 1. Add imports (at top of file, with existing imports)

```python
from starlette.middleware.base import BaseHTTPMiddleware
# BaseHTTPMiddleware is already imported — verify it is there before adding
```

### 2. Define EXEMPT_PATHS, EXEMPT_PREFIXES, and _is_exempt() — add before AuthGate class

```python
EXEMPT_PATHS = {"/settings/opening-balance", "/auth/login", "/auth/logout", "/favicon.ico"}
EXEMPT_PREFIXES = ("/static", "/docs", "/openapi.json")


def _is_exempt(path: str) -> bool:
    """Return True if path bypasses both opening-balance and auth gates.

    Normalises trailing slash so /auth/login/ matches /auth/login.
    Prefix check uses the normalised path for consistency.
    """
    normalised = path.rstrip("/") or "/"
    if normalised in EXEMPT_PATHS:
        return True
    return any(normalised.startswith(prefix) for prefix in EXEMPT_PREFIXES)
```

### 3. Add AuthGate class — replace the existing OpeningBalanceGate class

Remove `OpeningBalanceGate` entirely. Add `AuthGate` in its place:

```python
class AuthGate(BaseHTTPMiddleware):
    """Single middleware enforcing both opening-balance and auth checks.

    Evaluation order:
      1. Exempt route? → pass through unchanged.
      2. Opening balance set? → no → redirect /settings/opening-balance
      3. Valid session user? → no → redirect /auth/login
      4. Attach user to request.state.user → pass through.

    Uses a single DB connection (try/finally) for both checks.
    Calls auth_service functions — no raw SQL in middleware.
    """

    async def dispatch(self, request: Request, call_next):
        if _is_exempt(request.url.path):
            return await call_next(request)

        from app.services.auth_service import get_current_user, get_opening_balance

        conn = _connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        try:
            if get_opening_balance(conn) is None:
                return RedirectResponse(url="/settings/opening-balance", status_code=302)
            user = get_current_user(request, conn)
        finally:
            conn.close()

        if user is None:
            request.session.clear()
            return RedirectResponse(url="/auth/login", status_code=302)

        request.state.user = user
        return await call_next(request)
```

### 4. Update create_app() — register routers and swap middleware

```python
def create_app(database_url: str | None = None) -> FastAPI:
    global DATABASE_URL
    if database_url:
        DATABASE_URL = database_url

    conn = _connect(DATABASE_URL)
    initialise_db(conn)
    conn.close()

    app = FastAPI(title="cashflow-tracker", lifespan=lifespan)

    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    app.add_middleware(AuthGate)  # ← replaces OpeningBalanceGate

    from app.routes.settings import router as settings_router
    from app.routes.auth import router as auth_router          # ← new
    from app.routes.dashboard import router as dashboard_router  # ← new

    app.include_router(settings_router)
    app.include_router(auth_router)       # ← new
    app.include_router(dashboard_router)  # ← new

    return app
```

**Critical:** Replace `app.add_middleware(OpeningBalanceGate)` with `app.add_middleware(AuthGate)`.
Do NOT add a second middleware alongside the existing one. Starlette executes middlewares in reverse
`add_middleware()` order (last added = outermost = runs first). Two separate middlewares are
error-prone to order correctly — use one combined AuthGate.

---

## app/templates/base.html — exact changes required

Add a `<nav>` bar between the sandbox banner and `<main>`. Show the logged-in username and a logout
button when the user is authenticated. The logout button must be a POST form — never a link.

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
        nav {
            background: #f5f5f5;
            border-bottom: 1px solid #ddd;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 16px;
        }
        nav span { font-size: 14px; color: #555; }
        nav button {
            font-size: 13px;
            padding: 4px 10px;
            cursor: pointer;
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
    {% if request.state.user %}
    <nav>
        <span>{{ request.state.user["username"] }}</span>
        <form method="post" action="/auth/logout" style="margin:0">
            <button type="submit">Sign out</button>
        </form>
    </nav>
    {% endif %}
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**Notes on the nav:**
- `{% if request.state.user %}` is safe in Jinja2 — accessing a missing state attribute returns
  Jinja2 `Undefined` (falsy), not a Python exception.
- Logout is a `<form method="post">` — never an `<a href>` link.
- Nav is hidden on login page and other exempt routes (request.state.user is not set there).

---

## Acceptance check — run after implementation

```bash
# App starts
python -c "
import os; os.environ['SECRET_KEY'] = 'test-key'
from app.main import create_app
app = create_app(database_url=':memory:')
print('app start: OK')
"

# Auth gate: no session → redirect to /auth/login (after opening balance is set)
python -c "
import os; os.environ['SECRET_KEY'] = 'test-key'
from fastapi.testclient import TestClient
from app.main import create_app
app = create_app(database_url=':memory:')
client = TestClient(app, raise_server_exceptions=True, follow_redirects=False)
client.post('/settings/opening-balance', data={'opening_balance': '50000', 'as_of_date': '2026-01-01'})
r = client.get('/')
assert r.status_code == 302
assert '/auth/login' in r.headers['location']
print('auth gate: OK')
"
```

---

## Commit and PR

```bash
git add app/main.py app/templates/base.html
git commit -m "feat: AuthGate middleware + nav with logout, replaces OpeningBalanceGate (I2-T4)"
git push -u origin feature/p1-i2/t4-middleware
gh pr create \
  --base feature/phase-1/iteration-2 \
  --head feature/p1-i2/t4-middleware \
  --title "I2-T4: AuthGate middleware + base template nav" \
  --body "Replaces OpeningBalanceGate with single AuthGate (opening balance + auth in correct order). Registers auth and dashboard routers. Adds nav with username and POST logout button to base.html."
```

Update `iterations/p1-i2/tasks.md` — set I2-T4 to ✅ DONE with note: "AuthGate replaces OpeningBalanceGate; auth + dashboard routers registered; nav with logout added to base.html."

---

## Acceptance checklist

- [ ] App starts without error when SECRET_KEY is set
- [ ] `AuthGate` exists and `OpeningBalanceGate` is fully removed
- [ ] `_is_exempt()` normalises trailing slash and uses `normalised.startswith()` for prefix checks
- [ ] `EXEMPT_PATHS` includes `/settings/opening-balance`, `/auth/login`, `/auth/logout`, `/favicon.ico`
- [ ] `EXEMPT_PREFIXES` includes `/static`, `/docs`, `/openapi.json`
- [ ] AuthGate uses single `conn` with `try/finally conn.close()` for both checks
- [ ] AuthGate calls `get_opening_balance(conn)` and `get_current_user(request, conn)` — no inline SQL
- [ ] `conn.row_factory = sqlite3.Row` set after `_connect()` in AuthGate
- [ ] `app.add_middleware(AuthGate)` replaces `app.add_middleware(OpeningBalanceGate)` — not added alongside
- [ ] `auth_router` and `dashboard_router` registered in `create_app()`
- [ ] `GET /` with no session → 302 → `/auth/login` (after opening balance set)
- [ ] `GET /` with valid session → 200
- [ ] Nav with username and POST logout button in `base.html`
- [ ] Nav hidden when `request.state.user` is not set (login page, etc.)
- [ ] Logout button is `<form method="post">` — not a link
- [ ] 11 existing tests still pass (`pytest -v`)
- [ ] Ruff clean

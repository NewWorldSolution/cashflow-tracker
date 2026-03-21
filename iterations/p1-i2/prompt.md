# cashflow-tracker Task Prompt — P1-I2: Authentication

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/validation.py → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores the actual gross cash; VAT is extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or any reporting layer |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly; block the save, never default silently |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost` are computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point; route handlers and templates call it, never re-implement it |

---

## Repository State

- **Iteration branch:** `feature/phase-1/iteration-2`
- **Base branch:** `main` (P1-I1 merged 2026-03-21)
- **Tests passing:** 11 (all from P1-I1)
- **Ruff:** clean
- **Last completed iteration:** P1-I1 — Foundation (schema, seed data, opening balance gate)
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I2 |
| Title | Authentication — Login, Logout, Session Protection |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 2 — Authentication |
| Feature branch | `feature/phase-1/iteration-2` |
| Depends on | P1-I1 (schema, users seed, opening balance gate) |
| Blocks | P1-I3 (Transaction entry form — requires authenticated session) |
| PR scope | Task branches PR into `feature/phase-1/iteration-2`. The iteration branch PRs into `main` as one final PR. Do not combine iterations. Do not push partial work. |

---

## Task Goal

This iteration adds session-based authentication to the application. After P1-I2, every route except `/settings/opening-balance`, `/auth/login`, and `/auth/logout` requires a valid authenticated session. Unauthenticated requests redirect to `/auth/login`. Authenticated requests that hit `/auth/login` redirect to the dashboard (or opening balance setup if not yet configured).

Authentication is username/password only. No OAuth, no magic links, no token-based auth. This is a private 3-user internal tool — simplicity and reliability matter more than sophistication.

---

## Files to Read Before Starting

### Mandatory — read these for every task, in this order

```
CLAUDE.md                                              ← constitution — read first, always
project.md                                             ← current state and what this iteration delivers
skills/cash-flow/schema/SKILL.md                       ← full table structure — users table is the auth source
skills/cash-flow/auth_logic/SKILL.md                   ← session identity rules (users.id FK, never name string)
skills/cash-flow/error_handling/SKILL.md               ← no silent failures, inline errors, block on any failure
```

### Task-specific

```
skills/generic/code_writer/SKILL.md                   ← code quality rules
```

---

## What P1-I1 Established (Contracts This Iteration Must Respect)

```python
# Database — already exists, do not modify schema
# users table: id, username, password_hash, telegram_user_id, created_at
# Seed users (test credentials):
#   username=owner,     password=owner123
#   username=assistant, password=assistant123
#   username=wife,      password=wife123

# Available in app/main.py — use as-is, do not reimport or redefine:
def get_db() -> sqlite3.Connection: ...   # returns a live db connection

# Opening balance gate — already in app/main.py middleware:
# Any route other than /settings/opening-balance redirects there when balance is not set.
# P1-I2 must NOT remove or bypass this gate.
# P1-I2 adds a second gate: authentication.
# Order of evaluation: opening balance check FIRST, then auth check.

# Session contract established by P1-I1:
# session['user_id'] must store users.id (integer) — never username string
# This contract is now in use — do not change it.
```

---

## Existing Code This Task Builds On

```
app/main.py              ← already exists — register auth router and replace middleware here
app/templates/base.html  ← already exists — add logout link to nav, show logged-in username
```

Do not rewrite files that already exist. Make only the changes specified for this iteration.

---

## What to Build

### New files

```
app/routes/auth.py
  ← GET  /auth/login   — login form (redirect to / if already authenticated)
  ← POST /auth/login   — validate credentials, create session, redirect to /
  ← POST /auth/logout  — clear session, redirect to /auth/login

app/routes/dashboard.py
  ← GET /  — placeholder dashboard (protected route; shows "Logged in as: {username}")
  ← This is a minimal landing page for P1-I2. Full dashboard comes in a later iteration.

app/templates/dashboard.html
  ← extends base.html; displays username from request.state.user; no data queries needed

app/services/auth_service.py
  ← get_user_by_username(db, username) → users row or None
  ← verify_password(plain, hashed) → bool
  ← get_current_user(request, db) → users row or None
  ← require_auth(request) → users row (reads request.state.user — never redirects; middleware already guarantees it is set)

app/templates/auth/login.html
  ← login form: username + password fields
  ← inline error on failed login (do not reveal which field is wrong)
  ← SANDBOX banner inherited from base.html

tests/test_auth.py
  ← all tests listed in "Tests Required" section below
```

### Modified files

```
app/main.py
  ← register auth router and dashboard router
  ← replace OpeningBalanceGate with a single AuthGate middleware that enforces
    both opening balance and authentication in the correct sequence (see Auth middleware section)

app/templates/base.html
  ← add logout link in nav (POST form to /auth/logout)
  ← show current username in nav when authenticated
```

### Files that must NOT be modified

```
db/schema.sql            ← frozen after P1-I1
db/init_db.py            ← frozen after P1-I1
seed/categories.sql      ← frozen after P1-I1
seed/users.sql           ← frozen after P1-I1
app/routes/settings.py   ← P1-I1 deliverable — do not touch
```

---

## Authentication Logic — Exact Behaviour

### Login flow

```
GET /auth/login
  → if session['user_id'] exists and is valid → redirect to /
  → else → render login form (empty, no error)

POST /auth/login
  → read username + password from form
  → if username empty or password empty → render form with error: "Username and password are required"
  → query users WHERE username = ? (case-sensitive)
  → if user not found → render form with error: "Invalid credentials" (do not reveal which field is wrong)
  → bcrypt.checkpw(password.encode("utf-8"), user.password_hash)  ← encode to bytes before check
  → if mismatch → render form with error: "Invalid credentials"
  → if match → session.clear()  ← prevent session fixation
              → session['user_id'] = user.id (integer) → redirect to /
```

### Logout flow

```
POST /auth/logout
  ← must be POST, not GET (GET logout is a security issue — CSRF)
  → clear session
  → redirect to /auth/login
```

### Auth middleware — single AuthGate, correct evaluation order

P1-I2 **replaces** the existing `OpeningBalanceGate` with a single `AuthGate` middleware that
handles both checks. Do not add a second middleware alongside the existing one — Starlette
executes middlewares in reverse `add_middleware` order (last added = outermost = runs first),
which makes two separate middlewares error-prone to order correctly.

```python
# In create_app(), replace:
#   app.add_middleware(OpeningBalanceGate)
# With:
#   app.add_middleware(AuthGate)

# Exact-match exempt paths + prefix-exempt paths (static files, etc.)
EXEMPT_PATHS = {"/settings/opening-balance", "/auth/login", "/auth/logout"}
EXEMPT_PREFIXES = ("/static",)  # extend here for future API routes

def _is_exempt(path: str) -> bool:
    # Normalise trailing slash: /auth/login/ == /auth/login
    normalised = path.rstrip("/") or "/"
    if normalised in EXEMPT_PATHS:
        return True
    return any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES)


class AuthGate(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Step 1 — exempt routes bypass both checks
        if _is_exempt(request.url.path):
            return await call_next(request)

        # Step 2 — opening balance must be set (takes priority over auth)
        conn = _connect(DATABASE_URL)
        try:
            row = conn.execute("SELECT value FROM settings WHERE key = 'opening_balance'").fetchone()
        except sqlite3.OperationalError:
            row = None
        finally:
            conn.close()
        if row is None:
            return RedirectResponse(url="/settings/opening-balance", status_code=302)

        # Step 3 — user must be authenticated
        # Use get_current_user() from auth_service — do not reimplement the lookup inline.
        # Import inside the method to avoid circular imports at module level.
        from app.services.auth_service import get_current_user
        user = get_current_user(request, _connect(DATABASE_URL))
        if user is None:
            request.session.clear()  # clear zombie session if user was deleted
            return RedirectResponse(url="/auth/login", status_code=302)

        # Step 4 — attach user and proceed
        request.state.user = user
        return await call_next(request)
```

### Security rules

```
- Password field must use type="password" in HTML — never type="text"
- Do not reveal which field (username or password) caused login failure
- Logout must be POST — never GET
- session['user_id'] stores users.id integer — never username string
- bcrypt only — never plaintext comparison; encode password as UTF-8 bytes before checkpw()
- session.clear() before setting session['user_id'] on login (session fixation prevention)
- If session['user_id'] exists but user not found in db → session.clear() then redirect
- No hardcoded credentials anywhere in application code
- Session cookie is httponly and SameSite=lax (configured in P1-I1 SessionMiddleware — do not change)
- CSRF: explicit CSRF tokens are out of scope for P1-I2; SameSite=lax cookie mitigates the primary risk
  TODO: CSRF protection required before Phase 3 (transaction write endpoints introduce real financial risk)
```

---

## Edge Cases to Handle Explicitly

| Edge case | Expected behaviour |
|-----------|-------------------|
| Empty username submitted | Render form with error: "Username and password are required" |
| Empty password submitted | Render form with error: "Username and password are required" |
| Username not found in db | Render form with error: "Invalid credentials" — do not reveal it was the username |
| Wrong password | Render form with error: "Invalid credentials" — do not reveal it was the password |
| session['user_id'] exists but user deleted from db | Treat as unauthenticated — clear session, redirect to /auth/login |
| Authenticated user hits GET /auth/login | Redirect to / — do not show login form to authenticated users |
| POST /auth/logout with no session | Clear session (no-op), redirect to /auth/login — no error |
| Non-exempt route hit before opening balance set | Opening balance redirect takes priority over auth redirect. Note: exempt routes (/auth/login, /auth/logout, /settings/opening-balance) bypass both gates entirely — they are always reachable. |
| SQL injection attempt in username field | Parameterised queries prevent this — never use string interpolation |

---

## Tests Required

```python
# tests/test_auth.py

def test_login_page_loads(client):
    # GET /auth/login returns 200

def test_login_success_redirects(client):
    # POST /auth/login with owner/owner123 → redirect to /

def test_login_sets_session_user_id(client):
    # After successful login, session['user_id'] == users.id integer (not username string)

def test_login_wrong_password(client):
    # POST with correct username, wrong password → 200, "Invalid credentials" in response

def test_login_wrong_username(client):
    # POST with unknown username → 200, "Invalid credentials" in response

def test_login_empty_fields(client):
    # POST with empty username and password → 200, "Username and password are required"

def test_login_does_not_reveal_field(client):
    # Error message is identical for wrong username and wrong password

def test_logout_clears_session(client):
    # Login, then POST /auth/logout → session cleared, redirect to /auth/login

def test_logout_must_be_post(client):
    # GET /auth/logout → 405 Method Not Allowed

def test_protected_route_unauthenticated(client):
    # GET / without session → redirect to /auth/login

def test_protected_route_authenticated(client):
    # Login, then GET / → 200 (no redirect)

def test_authenticated_user_skips_login(client):
    # Login, then GET /auth/login → redirect to /

def test_opening_balance_gate_before_auth(client):
    # Fresh db (no opening balance set) → any route redirects to /settings/opening-balance, not /auth/login
```

---

## What NOT to Do

- Do not modify `db/schema.sql` — schema is frozen after P1-I1
- Do not add a `last_login` column or any other schema change — out of scope
- Do not implement password reset — out of scope for this iteration
- Do not implement "remember me" or persistent sessions — out of scope
- Do not use GET for logout — security issue
- Do not store username string in session — always `users.id` integer
- Do not reveal which field caused login failure in error messages
- Do not use string interpolation in SQL queries — parameterised queries only
- Do not rewrite `app/main.py` — replace `OpeningBalanceGate` with `AuthGate`, add router registration, nothing else
- Do not remove the opening balance gate — it must remain active
- Do not use `except: pass` or any silent exception swallowing
- Do not modify files outside the allowed list

---

## Handoff: What P1-I3 Needs From This Iteration

After P1-I2 merges, the following will be available for P1-I3 (Transaction Entry Form):

```python
# Authentication service available:
from app.services.auth_service import require_auth

# Usage in P1-I3 routes:
@router.get("/transactions/new")
async def new_transaction(request: Request, db=Depends(get_db)):
    user = require_auth(request)   # reads request.state.user set by AuthGate middleware
    # user.id is available for logged_by field

# Session contract (unchanged from P1-I1):
# session['user_id'] = users.id (integer)

# All routes in P1-I3 are protected by default via AuthGate middleware
# P1-I3 does not need to add auth checks per route — middleware handles it
# require_auth() is a convenience for routes that need the user object explicitly
```

---

## Execution Workflow

Follow this sequence exactly. Do not skip or reorder steps.

### Step 0 — Branch setup

```bash
git checkout main
git pull origin main
git checkout -b feature/phase-1/iteration-2
git push -u origin feature/phase-1/iteration-2

gh pr create \
  --base main \
  --head feature/phase-1/iteration-2 \
  --title "P1-I2: Authentication — Login, Logout, Session Protection" \
  --body "Work in progress. See iterations/p1-i2/prompt.md for full task spec." \
  --draft
```

### Step 1 — Verify baseline

```bash
pytest
# Expected: 11 tests pass (P1-I1), exit code 0

ruff check .
# Expected: clean, exit code 0
```

If either fails: stop. Do not proceed until baseline is clean.

### Step 2 — Read before writing

Read all files listed in "Files to Read Before Starting" in order. Do not write a line of implementation until you understand the auth rules and session contract.

### Step 3 — Plan before multi-file changes

This task touches more than 2 files. Present the full implementation plan (which files, what changes, in what order) before writing any code. Wait for confirmation.

### Step 4 — Implement

Build in this order:
1. `app/services/auth_service.py` — service layer first, no routes yet
2. `app/routes/auth.py` — login/logout routes after service is complete
3. `app/routes/dashboard.py` + `app/templates/dashboard.html` — placeholder dashboard (GET /)
4. `app/templates/auth/login.html` — login template
5. `app/main.py` — register auth + dashboard routers, replace middleware
6. `app/templates/base.html` — add logout link + username display
7. `tests/test_auth.py` — tests last, after all implementation complete

### Step 5 — Test and lint

```bash
pytest
# Must pass: all 11 P1-I1 tests + all 13 new auth tests = 24 total. Zero failures.

ruff check .
# Must be clean. Fix all issues before committing.
```

Do not submit if either command fails.

### Step 6 — Verify scope

```bash
git diff --name-only main
```

Every file in the output must appear in the allowed files list. Revert any unexpected file before committing.

### Step 7 — Commit and mark PR ready

```bash
git add <specific files — do not use git add -A>
git commit -m "feat: session-based authentication with login, logout, and route protection (P1-I2)

Adds username/password login via bcrypt verification, session-based auth
middleware, and route protection for all non-exempt paths. Auth gate evaluates
after opening balance gate. Logout is POST-only. Session stores users.id integer.
Error messages do not reveal which field caused login failure.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

gh pr ready feature/phase-1/iteration-2
```

---

## Definition of Done

This iteration is complete when ALL of the following are true:

- [ ] GET `/auth/login` renders login form for unauthenticated users
- [ ] POST `/auth/login` with valid credentials creates session and redirects to `/`
- [ ] POST `/auth/login` with invalid credentials renders form with "Invalid credentials" — same message regardless of which field is wrong
- [ ] POST `/auth/logout` clears session and redirects to `/auth/login`
- [ ] GET `/auth/logout` returns 405
- [ ] All routes except `/settings/opening-balance`, `/auth/login`, `/auth/logout` redirect unauthenticated requests to `/auth/login`
- [ ] Opening balance gate still evaluated first — takes priority over auth gate
- [ ] `session['user_id']` stores `users.id` integer — never username string
- [ ] Authenticated user hitting GET `/auth/login` is redirected to `/`
- [ ] All 24 tests pass (11 from P1-I1 + 13 new) — zero failures
- [ ] Ruff clean (`ruff check .` exit code 0)
- [ ] Only allowed files modified (`git diff --name-only main`)
- [ ] Feature branch pushed, draft PR opened, marked ready for review
- [ ] No `except: pass`, no plaintext passwords, no GET logout, no username stored in session

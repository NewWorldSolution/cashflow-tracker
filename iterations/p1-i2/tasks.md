# P1-I2 — Authentication: Login, Logout, Session Protection
## Task Board

**Status:** ⏳ WAITING — not started
**Last updated:** 2026-03-21 — board created, awaiting bootstrap
**Iteration branch:** `feature/phase-1/iteration-2` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-2` → `main` ← QA agent approves before merge

---

## Dependency Map

```
I2-T1 (auth service)
  ├── I2-T2 (auth routes)    ──┐
  └── I2-T3 (login template) ──┴──► I2-T4 (middleware + base template) ──► I2-T5 (tests + close)
```

T2 and T3 run in parallel once T1 is DONE.
T4 must wait for both T2 and T3 to be DONE.
T5 closes the iteration — runs last.

---

## Tasks

| ID    | Title                          | Owner       | Status     | Depends on   | Branch                          |
|-------|--------------------------------|-------------|------------|--------------|---------------------------------|
| I2-T1 | Auth service layer             | Codex       | ⏳ WAITING | —            | `feature/p1-i2/t1-auth-service` |
| I2-T2 | Auth routes (login/logout)     | Claude Code | ⏳ WAITING | I2-T1        | `feature/p1-i2/t2-auth-routes`  |
| I2-T3 | Login template                 | Codex       | ⏳ WAITING | I2-T1        | `feature/p1-i2/t3-login-template` |
| I2-T4 | Middleware + base template     | Claude Code | ⏳ WAITING | I2-T2, I2-T3 | `feature/p1-i2/t4-middleware`   |
| I2-T5 | Tests + ruff + PR ready        | Claude Code | ⏳ WAITING | I2-T4        | `feature/p1-i2/t5-tests`        |

---

## Prompts & Reviews

| Task  | Implementation prompt                       | Review prompt                            | Reviewer    |
|-------|---------------------------------------------|------------------------------------------|-------------|
| I2-T1 | `iterations/p1-i2/prompts/t1-auth-service.md` | `iterations/p1-i2/reviews/review-t1.md` | Claude Code |
| I2-T2 | `iterations/p1-i2/prompts/t2-auth-routes.md`  | `iterations/p1-i2/reviews/review-t2.md` | Codex       |
| I2-T3 | `iterations/p1-i2/prompts/t3-login-template.md` | `iterations/p1-i2/reviews/review-t3.md` | Claude Code |
| I2-T4 | `iterations/p1-i2/prompts/t4-middleware.md`   | `iterations/p1-i2/reviews/review-t4.md` | Codex       |
| I2-T5 | `iterations/p1-i2/prompts/t5-tests.md`        | `iterations/p1-i2/reviews/review-t5.md` | Codex       |
| —     | —                                           | `iterations/p1-i2/reviews/review-iteration.md` | Claude Code (QA) |

---

## Task Details

### I2-T1 — Auth service layer (Codex)

**Goal:** Pure service layer. No routes, no templates. Business logic only.

**Allowed files:**
```
app/services/__init__.py
app/services/auth_service.py
```

**Functions to implement:**
```python
get_user_by_username(db, username) → Row | None
  # SELECT from users WHERE username = ? (parameterised — never string interpolation)
  # Returns full users row or None

verify_password(plain_password: str, password_hash: str) → bool
  # bcrypt.checkpw only — never plaintext comparison

get_current_user(request: Request, db) → Row | None
  # Read session['user_id'] — must be integer
  # Query users WHERE id = ?
  # If user not found (deleted) → return None

require_auth(request: Request) → Row
  # Reads request.state.user — set by AuthGate middleware for all non-exempt routes
  # If None → raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
  # If found → return user row
  # P1-I3 uses this as a dependency in every protected route (middleware already blocked unauthenticated requests)
```

**Security rules:**
- Parameterised queries only — never string interpolation in SQL
- bcrypt only — never plaintext comparison; encode password as UTF-8 bytes before `checkpw()`
- session['user_id'] must be integer — never username string
- If session['user_id'] exists but user not in db → `session.clear()` then treat as unauthenticated
- On login success: `session.clear()` first, then set `session['user_id']` (session fixation prevention)

**Acceptance check:**
```bash
python -c "from app.services.auth_service import get_user_by_username, verify_password; print('imports ok')"
```

---

### I2-T2 — Auth routes + placeholder dashboard (Claude Code)

**Goal:** Login/logout route handlers and a minimal placeholder dashboard at `/`.

**Depends on:** I2-T1 (auth_service.py must exist and be importable)

**Allowed files:**
```
app/routes/auth.py
app/routes/dashboard.py
app/templates/dashboard.html
```

**Routes to implement:**
```
GET  /auth/login   → render login form (redirect to / if already authenticated)
POST /auth/login   → validate credentials, set session, redirect to /
POST /auth/logout  → clear session, redirect to /auth/login
GET  /             → placeholder dashboard: render dashboard.html (protected by AuthGate middleware)
```

**Dashboard route (app/routes/dashboard.py):**
```python
# Minimal placeholder — full dashboard is out of scope for P1-I2.
# GET / renders dashboard.html with request.state.user (set by AuthGate).
# No DB queries needed. No data — just confirms authenticated access.
```

**Dashboard template (app/templates/dashboard.html):**
```
- Extends base.html (inherits SANDBOX banner and nav)
- Shows: "Logged in as: {{ request.state.user['username'] }}"
- No tables, no forms beyond the inherited logout button
```

**Login POST logic (exact sequence):**
```
1. Read username + password from form data
2. If either empty → return form with error: "Username and password are required"
3. get_user_by_username(db, username)
4. If None → return form with error: "Invalid credentials"
5. verify_password(password, user.password_hash)
6. If False → return form with error: "Invalid credentials"
7. session.clear()              ← session fixation prevention
8. session['user_id'] = user.id  ← integer, never username string
9. Redirect to /
```

**Acceptance check:**
- Router imports without error
- GET /auth/login returns 200 when opening balance is set and user is not authenticated

---

### I2-T3 — Login template (Codex)

**Goal:** Clean, minimal login form. Inherits SANDBOX banner from base.html.

**Depends on:** I2-T1 (knows the error message contract)

**Allowed files:**
```
app/templates/auth/login.html
app/templates/auth/__init__.py   ← empty if needed
```

**Template requirements:**
```
- Extends base.html (inherits SANDBOX banner automatically)
- Form action: POST /auth/login
- Fields: username (type="text"), password (type="password")
- Submit button: "Sign in"
- Error display: inline, above the form, only when error variable is set
- Input values preserved on error (username repopulated, password cleared)
- No JavaScript required — pure HTML form
- No external CSS frameworks — consistent with project stack
```

**Acceptance check:**
- Template renders without Jinja2 errors when error=None
- Template renders with error message when error="Invalid credentials"
- Password field uses type="password" — never type="text"

---

### I2-T4 — Middleware + base template update (Claude Code)

**Goal:** Wire auth into the application. Register router. Add auth gate to middleware. Update nav.

**Depends on:** I2-T2 (routes exist), I2-T3 (template exists)

**Allowed files:**
```
app/main.py
app/templates/base.html
```

**Changes to app/main.py:**
```python
# 1. Register auth router
from app.routes.auth import router as auth_router
app.include_router(auth_router)

# 2. Replace OpeningBalanceGate with AuthGate — a single middleware that handles both checks.
#    IMPORTANT: do NOT add a second middleware alongside the existing one.
#    Starlette executes middlewares in reverse add_middleware() order (last added = outermost = runs first).
#    Two separate middlewares are error-prone to order correctly — use one combined class.
#
#    AuthGate evaluation order (see prompt.md for full implementation):
#      → Is route exempt (/settings/opening-balance, /auth/login, /auth/logout)? → allow through
#      → Is opening_balance set in settings? → no → redirect /settings/opening-balance
#      → Is session['user_id'] valid (user exists in db)? → no → redirect /auth/login
#      → Attach user to request.state.user → allow through
#
# In create_app():
#   Replace: app.add_middleware(OpeningBalanceGate)
#   With:    app.add_middleware(AuthGate)
#
# Also register dashboard router:
#   from app.routes.dashboard import router as dashboard_router
#   app.include_router(dashboard_router)
```

**Changes to app/templates/base.html:**
```
- Add logout button to nav: POST form to /auth/logout
- Show current username in nav (from request.state.user if available)
- Logout button only visible when user is authenticated
```

**Critical rule:** Replace `OpeningBalanceGate` with `AuthGate` — do not add a second middleware alongside it. Add the auth router registration. No other changes to `app/main.py`.

**Acceptance check:**
- App starts without error
- GET / without session → redirects to /auth/login (AuthGate blocks it)
- GET / with valid session → 200 (dashboard_router handles it, returns dashboard.html)

---

### I2-T5 — Tests + ruff + PR ready (Claude Code)

**Goal:** Full test suite green, ruff clean, iteration closed.

**Depends on:** I2-T4 (all implementation complete)

**Allowed files:**
```
tests/test_auth.py
iterations/p1-i2/tasks.md   ← status update only (closure step 5)
```

**Fixture requirements:**
```python
# Most auth tests need opening balance already set — otherwise every request
# redirects to /settings/opening-balance before auth logic is reached.
# Use two fixtures:

@pytest.fixture
def client(tmp_path):
    # Fresh db, opening balance PRE-SET, no authenticated session.
    # POST to /settings/opening-balance before yielding the client.

@pytest.fixture
def fresh_client(tmp_path):
    # Fresh db, NO opening balance set.
    # Used only for test_opening_balance_gate_before_auth.
```

**Tests to implement (13 total):**
```python
test_login_page_loads
test_login_success_redirects
test_login_sets_session_user_id
test_login_wrong_password
test_login_wrong_username
test_login_empty_fields
test_login_does_not_reveal_field
test_logout_clears_session
test_logout_must_be_post
test_protected_route_unauthenticated
test_protected_route_authenticated
test_authenticated_user_skips_login
test_opening_balance_gate_before_auth
```

**Closure steps:**
1. `pytest` — 24 tests pass (11 from P1-I1 + 13 new), exit code 0
2. `ruff check .` — clean, exit code 0
3. `git diff --name-only feature/phase-1/iteration-2` — only allowed files
4. `gh pr ready feature/phase-1/iteration-2`
5. Update this file: Status → ✔ COMPLETE, Last updated → today

---

## Agent Rules

1. **Read this file first.** Find your task. Confirm status is WAITING before starting.
2. **Update status to IN PROGRESS** before writing a line of code.
3. **Check dependencies.** Never start if any dep is not ✅ DONE.
4. **Worktree:** check out `feature/phase-1/iteration-2` first, then create your task branch from it.
5. **PR targets the iteration branch**, not `main`. One task per PR.
6. **After completing:** set status to ✅ DONE. Add one-line note: what you produced.
7. **Never touch another agent's task.** Add notes under your own task only.
8. **If blocked:** set status to 🚫 BLOCKED with reason. Stop and wait.
9. **No `except: pass`, no plaintext passwords, no GET logout, no username in session.**
10. Read your task prompt: `iterations/p1-i2/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency or bootstrap |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-2` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

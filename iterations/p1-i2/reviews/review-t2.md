# Review — I2-T2: Auth Routes + Placeholder Dashboard
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i2/t2-auth-routes`
**PR target:** `feature/phase-1/iteration-2`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/routes/auth.py           ← GET /auth/login, POST /auth/login, POST /auth/logout
app/routes/dashboard.py      ← GET / placeholder dashboard
app/templates/dashboard.html ← extends base.html, shows username from request.state.user
```

### Required route behaviour

| Route | Required behaviour |
|-------|--------------------|
| `GET /auth/login` | Returns 200 (login form); redirects to `/` if already authenticated |
| `POST /auth/login` | Validates credentials; session fixation prevention; stores `user.id` integer; redirects to `/` |
| `POST /auth/logout` | Clears session; redirects to `/auth/login` |
| `GET /auth/logout` | 405 Method Not Allowed (GET logout is a security issue) |
| `GET /` | Renders dashboard.html with `request.state.user` (set by AuthGate) |

### Login POST exact sequence

```
1. Empty username or password → 401, "Username and password are required"
2. User not found → 401, "Invalid credentials"
3. Wrong password → 401, "Invalid credentials"
4. session.clear()  ← session fixation prevention
5. session["user_id"] = user["id"]  ← integer, never username string
6. Redirect to / (302)
```

---

## Architecture principles to check

| # | Principle | Check |
|---|-----------|-------|
| 5 | No silent failures — no `except: pass` | grep |
| 6 | Identity via integer FK — `session["user_id"]` must be `user["id"]` integer | read code |
| 8 | No business logic reimplemented — must call `get_user_by_username` and `verify_password` from auth_service | grep |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i2/t2-auth-routes
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-2
# Expected: app/routes/auth.py, app/routes/dashboard.py, app/templates/dashboard.html only
```

### Step 3 — Imports and router

```bash
python -c "from app.routes.auth import router; print('auth router ok')"
python -c "from app.routes.dashboard import router; print('dashboard router ok')"
```

### Step 4 — No inline auth logic

```bash
grep -n "checkpw\|bcrypt\|SELECT.*username\|SELECT.*users" app/routes/auth.py
# Expected: no output
# auth_service must provide all user lookup and password verification
```

### Step 5 — Session fixation prevention

Read `post_login` in `app/routes/auth.py`. Verify `session.clear()` is called **before**
`session["user_id"] = ...`.

```bash
grep -n "session.clear\|session\[" app/routes/auth.py
```

`session.clear()` must appear before `session["user_id"]`. If order is reversed: `CHANGES REQUIRED` (critical).

### Step 6 — Integer session, not username string

```bash
grep -n "session\[.user_id.\]" app/routes/auth.py
```

Must assign `user["id"]` (integer FK), never `user["username"]` or any string.

### Step 7 — Error message equality

Read `post_login`. Verify:
- Wrong username: error is `"Invalid credentials"` exactly
- Wrong password: error is `"Invalid credentials"` exactly
- The same message is returned in both cases — never reveals which field failed

```bash
grep -n "Invalid credentials\|Username and password" app/routes/auth.py
```

Exactly 2 distinct messages: `"Username and password are required"` and `"Invalid credentials"`.

### Step 8 — Logout is POST-only

```bash
grep -n "logout" app/routes/auth.py
```

Verify logout handler uses `@router.post`, not `@router.get` or `@router.api_route`.

### Step 9 — Dashboard template

Read `app/templates/dashboard.html`. Verify:
- Extends `base.html`
- Shows `request.state.user["username"]` (or equivalent)
- No DB query references in the template

### Step 10 — No silent failures

```bash
grep -n "except.*pass\|except:$" app/routes/auth.py app/routes/dashboard.py
# Expected: no output
```

### Step 11 — app/main.py not modified

```bash
git diff feature/phase-1/iteration-2 -- app/main.py
# Expected: no output — this file must not be touched in T2
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

Files modified outside `app/routes/auth.py`, `app/routes/dashboard.py`, `app/templates/dashboard.html`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] GET /auth/login importable and router registered without error
- [PASS|FAIL] GET /auth/login redirects to / when user already authenticated
- [PASS|FAIL] POST /auth/login: empty fields → 401, "Username and password are required"
- [PASS|FAIL] POST /auth/login: wrong username → 401, "Invalid credentials"
- [PASS|FAIL] POST /auth/login: wrong password → 401, "Invalid credentials"
- [PASS|FAIL] Error message identical for wrong username and wrong password
- [PASS|FAIL] session.clear() called before session["user_id"] = user["id"] on login
- [PASS|FAIL] session["user_id"] stores user["id"] integer — not username string
- [PASS|FAIL] POST /auth/logout clears session and redirects to /auth/login
- [PASS|FAIL] Logout uses @router.post — not @router.get
- [PASS|FAIL] GET / handler exists in dashboard.py
- [PASS|FAIL] dashboard.html extends base.html and shows username
- [PASS|FAIL] No inline bcrypt/SQL in auth.py — calls auth_service functions only
- [PASS|FAIL] app/main.py not modified
- [PASS|FAIL] No except: pass or silent failures
- [PASS|FAIL] Scope: only the 3 allowed files modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

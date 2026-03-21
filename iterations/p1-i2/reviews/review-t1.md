# Review — I2-T1: Auth Service Layer
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i2/t1-auth-service`
**PR target:** `feature/phase-1/iteration-2`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Your job is to verify it exactly matches the spec. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/services/__init__.py         ← empty package init
app/services/auth_service.py     ← 5 functions: get_user_by_username, verify_password,
                                    get_opening_balance, get_current_user, require_auth
```

### Required behaviour per function

| Function | Key requirements |
|----------|-----------------|
| `get_user_by_username(db, username)` | Parameterised query only; returns full row or None |
| `verify_password(plain, hash)` | `bcrypt.checkpw` only; `plain.encode("utf-8")` before call |
| `get_opening_balance(db)` | Returns value string or None; catches `sqlite3.OperationalError` |
| `get_current_user(request, db)` | `isinstance(user_id, int)` guard; `session.clear()` on deleted user |
| `require_auth(request)` | Reads `request.state.user`; raises `RuntimeError` if missing; never redirects |

---

## Architecture principles to check

| # | Principle | Check |
|---|-----------|-------|
| 5 | No silent failures — no `except: pass` anywhere | grep |
| 6 | Identity via integer FK — session stores `users.id` int, never username | read code |
| 8 | Validation in service layer — this file IS the service layer; no business logic in routes | N/A here |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i2/t1-auth-service
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-2
# Expected: app/services/__init__.py, app/services/auth_service.py only
# Any other file = scope violation
```

### Step 3 — File existence

```bash
ls app/services/__init__.py app/services/auth_service.py
python -c "
from app.services.auth_service import (
    get_user_by_username,
    verify_password,
    get_opening_balance,
    get_current_user,
    require_auth,
)
print('all 5 functions importable')
"
```

All 5 must import without error.

### Step 4 — No SQL injection surface

```bash
grep -n "f\".*SELECT\|f'.*SELECT\|%.*SELECT\|format.*SELECT" app/services/auth_service.py
# Expected: no output — parameterised queries only, never string interpolation
```

### Step 5 — bcrypt correct usage

```bash
grep -n "checkpw\|encode\|utf-8\|utf8" app/services/auth_service.py
```

Verify:
- `bcrypt.checkpw(plain_password.encode("utf-8"), ...)` — UTF-8 encoding present
- No plaintext comparison (`==`) of passwords anywhere

```bash
grep -n "password.*==" app/services/auth_service.py
# Expected: no output
```

### Step 6 — isinstance guard in get_current_user

```bash
grep -n "isinstance" app/services/auth_service.py
```

Must find `isinstance(user_id, int)` before any DB query. If missing: `CHANGES REQUIRED` (critical).

### Step 7 — session.clear() on deleted user

Read `get_current_user` in full. Verify that when `db.execute(...).fetchone()` returns `None`
(user deleted from db), the function calls `request.session.clear()` before returning `None`.

```bash
grep -n "session.clear" app/services/auth_service.py
```

Must appear inside `get_current_user`.

### Step 8 — get_opening_balance OperationalError handling

```bash
grep -n "OperationalError" app/services/auth_service.py
```

Must catch `sqlite3.OperationalError` and return `None`. If missing: major issue (app will crash on
first request before schema is created).

### Step 9 — require_auth contract

Read `require_auth` in full. Verify:
- Reads `request.state.user` (or uses `getattr(request.state, "user", None)`)
- Raises `RuntimeError` if user is None — not `HTTPException(403)`, not `RedirectResponse`
- Returns the user row directly

```bash
grep -n "RuntimeError\|HTTPException\|RedirectResponse" app/services/auth_service.py
```

`RuntimeError` must appear; `HTTPException` and `RedirectResponse` must NOT appear in `require_auth`.

### Step 10 — No silent failures

```bash
grep -n "except.*pass\|except:$" app/services/auth_service.py
# Expected: no output
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
  file: app/services/auth_service.py:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/services/__init__.py` and `app/services/auth_service.py`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] All 5 functions importable from app.services.auth_service
- [PASS|FAIL] get_user_by_username uses parameterised query only
- [PASS|FAIL] verify_password encodes plain_password as UTF-8 bytes before checkpw()
- [PASS|FAIL] get_opening_balance catches sqlite3.OperationalError → returns None
- [PASS|FAIL] get_current_user validates isinstance(user_id, int) before querying
- [PASS|FAIL] get_current_user calls session.clear() when user not found in db
- [PASS|FAIL] require_auth raises RuntimeError (not HTTPException) when state.user missing
- [PASS|FAIL] No string interpolation in SQL queries
- [PASS|FAIL] No plaintext password comparison
- [PASS|FAIL] No except: pass or silent exception swallowing
- [PASS|FAIL] Scope: only app/services/__init__.py and app/services/auth_service.py modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

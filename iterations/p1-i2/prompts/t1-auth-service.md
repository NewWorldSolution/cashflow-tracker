# I2-T1 — Auth Service Layer
**Agent:** Codex
**Branch:** `feature/p1-i2/t1-auth-service`
**PR target:** `feature/phase-1/iteration-2`

---

## Before starting — read these files in order

```
CLAUDE.md                                        ← architecture rules — read first
iterations/p1-i2/tasks.md                       ← confirm I2-T1 status is WAITING, set to IN PROGRESS
skills/cash-flow/schema/SKILL.md                 ← users table structure, password_hash column
skills/cash-flow/auth_logic/SKILL.md             ← session identity rules (users.id integer, never username)
skills/cash-flow/error_handling/SKILL.md         ← no silent failures
```

No dependencies — this is the first task. Start immediately.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-2
git worktree add -b feature/p1-i2/t1-auth-service ../cashflow-tracker-i2t1 feature/phase-1/iteration-2
cd ../cashflow-tracker-i2t1
```

---

## What already exists

```
app/main.py              ← provides _connect(DATABASE_URL) and get_db() — do not modify
app/routes/settings.py   ← frozen after P1-I1 — do not touch
db/schema.sql            ← frozen — users table: id, username, password_hash, telegram_user_id, created_at
```

---

## What to build

### Allowed files (this task only)

```
app/services/__init__.py    ← new: empty package init
app/services/auth_service.py ← new: 5 functions — business logic only, no routes, no templates
```

Do not create routes. Do not create templates. Do not modify `app/main.py`.

---

## app/services/auth_service.py — implement exactly this

```python
import sqlite3

import bcrypt
from fastapi import Request


def get_user_by_username(db: sqlite3.Connection, username: str):
    """Return the full users row for the given username, or None if not found.

    Uses a parameterised query — never string interpolation.
    """
    return db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if plain_password matches the stored bcrypt hash.

    Encodes the plain password to UTF-8 bytes before calling checkpw().
    Never compares passwords in plaintext.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def get_opening_balance(db: sqlite3.Connection) -> str | None:
    """Return the opening_balance value from settings, or None if not set.

    Catches sqlite3.OperationalError (settings table not yet created) and
    returns None — allows AuthGate to redirect before schema exists.
    Used by AuthGate so that no raw SQL appears in middleware.
    """
    try:
        row = db.execute(
            "SELECT value FROM settings WHERE key = 'opening_balance'"
        ).fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None


def get_current_user(request: Request, db: sqlite3.Connection):
    """Return the users row for the session user, or None if unauthenticated.

    Reads session['user_id']. Validates it is an integer — rejects malformed
    or legacy string sessions. If the user_id is valid but not found in the
    database (deleted account), clears the session and returns None.
    """
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        request.session.clear()
    return row


def require_auth(request: Request):
    """Return the authenticated user row from request.state.user.

    AuthGate sets request.state.user for every non-exempt route before the
    route handler is called. This function is a convenience accessor for route
    handlers that need the user object explicitly (e.g. to get user.id for
    logged_by).

    Raises RuntimeError if request.state.user is not set — this indicates
    developer misuse (calling require_auth on an exempt route or before
    AuthGate runs), not a user-facing error. Never redirects.
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise RuntimeError(
            "require_auth() called but request.state.user is not set. "
            "Ensure AuthGate middleware runs before this route handler."
        )
    return user
```

---

## Security rules — do not deviate

- Parameterised queries only — never `f"SELECT ... WHERE username = '{username}'"` or similar
- `bcrypt.checkpw` only — never `==` comparison of passwords
- `plain_password.encode("utf-8")` before `checkpw()` — do not pass a raw string
- `session['user_id']` must be an integer — `isinstance(user_id, int)` check is mandatory
- If user is deleted (row is None after valid user_id): `session.clear()`, return None
- `require_auth` raises `RuntimeError` only — never `HTTPException`, never `RedirectResponse`

---

## Worktree setup — verify baseline before writing any code

```bash
pytest
ruff check .
# Expected: 11 passed, ruff clean
```

If baseline fails: stop and raise a BLOCKED note in tasks.md.

---

## Acceptance check

```bash
python -c "
from app.services.auth_service import (
    get_user_by_username,
    verify_password,
    get_opening_balance,
    get_current_user,
    require_auth,
)
print('imports ok')
"
```

All 5 names must import without error.

---

## Commit and PR

```bash
git add app/services/__init__.py app/services/auth_service.py
git commit -m "feat: auth service layer — user lookup, password verify, session user (I2-T1)"
git push -u origin feature/p1-i2/t1-auth-service
gh pr create \
  --base feature/phase-1/iteration-2 \
  --head feature/p1-i2/t1-auth-service \
  --title "I2-T1: Auth service layer" \
  --body "Pure service layer: get_user_by_username, verify_password, get_opening_balance, get_current_user, require_auth. No routes. No templates. Parameterised queries. bcrypt UTF-8."
```

Update `iterations/p1-i2/tasks.md` — set I2-T1 to ✅ DONE with note: "auth_service.py: 5 functions, parameterised queries, bcrypt UTF-8, isinstance session guard."

---

## Acceptance checklist

- [ ] `app/services/__init__.py` exists and is empty
- [ ] All 5 functions importable from `app.services.auth_service`
- [ ] `get_user_by_username` uses parameterised query only — no string interpolation
- [ ] `verify_password` calls `bcrypt.checkpw` with `plain_password.encode("utf-8")`
- [ ] `get_opening_balance` catches `sqlite3.OperationalError` and returns None
- [ ] `get_current_user` validates `isinstance(user_id, int)` before querying
- [ ] `get_current_user` calls `session.clear()` if user is not found in db
- [ ] `require_auth` raises `RuntimeError` (not HTTPException) if `request.state.user` is missing
- [ ] No routes, no templates, no modifications to `app/main.py`
- [ ] Ruff clean

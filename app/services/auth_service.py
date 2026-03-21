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
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), password_hash.encode("utf-8")
    )


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

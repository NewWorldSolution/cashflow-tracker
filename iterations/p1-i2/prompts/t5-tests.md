# I2-T5 — Tests + Ruff + PR Ready
**Agent:** Claude Code
**Branch:** `feature/p1-i2/t5-tests`
**PR target:** `feature/phase-1/iteration-2`

---

## Before starting — read these files in order

```
CLAUDE.md                                        ← architecture rules — read first
iterations/p1-i2/tasks.md                       ← confirm I2-T4 (and all prior tasks) are ✅ DONE, set I2-T5 to IN PROGRESS
skills/generic/qa_runner/SKILL.md                ← test against acceptance criteria, not code assumptions
skills/cash-flow/auth_logic/SKILL.md             ← session identity rules
```

**All prior tasks (T1–T4) must show ✅ DONE in `tasks.md`.** If any is not DONE, stop and wait.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-2

# Verify full stack is present
python -c "from app.main import create_app; print('app ok')"
python -c "from app.routes.auth import router; print('auth router ok')"
python -c "from app.routes.dashboard import router; print('dashboard router ok')"
python -c "from app.services.auth_service import require_auth; print('auth service ok')"
ls app/templates/auth/login.html app/templates/dashboard.html app/templates/base.html

git worktree add -b feature/p1-i2/t5-tests ../cashflow-tracker-i2t5 feature/phase-1/iteration-2
cd ../cashflow-tracker-i2t5
```

---

## What to build

### Allowed files (this task only)

```
tests/test_auth.py                  ← new: 14 auth tests
iterations/p1-i2/tasks.md          ← status update only (closure step 5)
```

Do not modify any existing files other than `tasks.md`.

---

## Fixtures — implement both

```python
import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    """TestClient with a temporary database, opening balance PRE-SET.

    Most auth tests need the opening balance set — otherwise AuthGate redirects
    to /settings/opening-balance before any auth logic is reached.
    """
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = f"sqlite:///./{db_path}"

    from app.main import create_app
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        # Pre-set opening balance so AuthGate's balance check passes
        c.post(
            "/settings/opening-balance",
            data={"opening_balance": "50000", "as_of_date": "2026-01-01"},
            follow_redirects=True,
        )
        yield c


@pytest.fixture
def fresh_client(tmp_path):
    """TestClient with a temporary database, NO opening balance set.

    Used only for test_opening_balance_gate_before_auth — verifies that
    AuthGate redirects to /settings/opening-balance, not /auth/login,
    when the balance has never been configured.
    """
    db_path = str(tmp_path / "fresh.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = f"sqlite:///./{db_path}"

    from app.main import create_app
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        yield c
```

---

## tests/test_auth.py — implement all 14 tests

```python
"""Tests for P1-I2: login, logout, session protection, and auth gate ordering."""
import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

# fixtures: client, fresh_client (defined above — include in same file)


# ── login page ────────────────────────────────────────────────────────────────

def test_login_page_loads(client):
    """GET /auth/login returns 200 when opening balance is set and no session."""
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert "Sign in" in r.text


def test_login_success_redirects(client):
    """POST with valid credentials redirects to /."""
    r = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert r.status_code == 302
    assert r.headers["location"] == "/"


def test_login_sets_session_user_id(client):
    """After successful login, session['user_id'] is an integer (not username string)."""
    r = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert r.status_code == 302
    # Verify integer in session by following redirect and checking dashboard renders
    r2 = client.get("/", cookies=r.cookies)
    assert r2.status_code == 200
    assert "owner" in r2.text  # username shown in dashboard


def test_login_wrong_password(client):
    """Correct username, wrong password → 401, 'Invalid credentials'."""
    r = client.post("/auth/login", data={"username": "owner", "password": "wrongpass"})
    assert r.status_code == 401
    assert "Invalid credentials" in r.text


def test_login_wrong_username(client):
    """Unknown username → 401, 'Invalid credentials'."""
    r = client.post("/auth/login", data={"username": "nobody", "password": "owner123"})
    assert r.status_code == 401
    assert "Invalid credentials" in r.text


def test_login_empty_fields(client):
    """Empty username and password → 401, 'Username and password are required'."""
    r = client.post("/auth/login", data={"username": "", "password": ""})
    assert r.status_code == 401
    assert "Username and password are required" in r.text


def test_login_does_not_reveal_field(client):
    """Error message is identical for wrong username and wrong password."""
    r_user = client.post("/auth/login", data={"username": "nobody", "password": "x"})
    r_pass = client.post("/auth/login", data={"username": "owner", "password": "wrong"})
    assert "Invalid credentials" in r_user.text
    assert "Invalid credentials" in r_pass.text
    # Same generic message for both — neither reveals which field failed
    assert r_user.status_code == r_pass.status_code == 401


# ── logout ────────────────────────────────────────────────────────────────────

def test_logout_clears_session(client):
    """Login then logout — session is cleared, redirect to /auth/login."""
    login = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert login.status_code == 302
    logout = client.post("/auth/logout", cookies=login.cookies)
    assert logout.status_code == 302
    assert "/auth/login" in logout.headers["location"]
    # After logout, protected route must redirect to login again
    r = client.get("/", cookies=logout.cookies)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]


def test_logout_must_be_post(client):
    """GET /auth/logout returns 405 Method Not Allowed."""
    r = client.get("/auth/logout")
    assert r.status_code == 405


# ── protected routes ──────────────────────────────────────────────────────────

def test_protected_route_unauthenticated(client):
    """GET / without session → 302 → /auth/login."""
    r = client.get("/")
    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]


def test_protected_route_authenticated(client):
    """Login then GET / → 200 (no redirect)."""
    login = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert login.status_code == 302
    r = client.get("/", cookies=login.cookies)
    assert r.status_code == 200


def test_authenticated_user_skips_login(client):
    """Authenticated user hitting GET /auth/login is redirected to /."""
    login = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert login.status_code == 302
    r = client.get("/auth/login", cookies=login.cookies)
    assert r.status_code == 302
    assert r.headers["location"] == "/"


# ── gate ordering ─────────────────────────────────────────────────────────────

def test_opening_balance_gate_before_auth(fresh_client):
    """No opening balance set → any route redirects to /settings/opening-balance, not /auth/login."""
    r = fresh_client.get("/")
    assert r.status_code == 302
    assert "/settings/opening-balance" in r.headers["location"]
    assert "/auth/login" not in r.headers["location"]


def test_deleted_user_treated_as_unauthenticated(client):
    """session['user_id'] set to a valid int that does not exist in db → redirect to /auth/login."""
    # Manually inject a session with a non-existent user_id
    # Use the session cookie mechanism: log in, then corrupt the session
    # Simplest approach: log in as owner, then delete owner from db, then hit protected route
    login = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert login.status_code == 302

    # Delete owner from db
    db_path = os.environ.get("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM users WHERE username = 'owner'")
    conn.commit()
    conn.close()

    # Hit protected route with the now-stale session
    r = client.get("/", cookies=login.cookies)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]
```

---

## Closure sequence — run in this exact order

### 1. Run all tests

```bash
pytest -v
# Expected: 25 passed (11 from P1-I1 + 14 new), 0 failed, exit code 0
# If any test fails: fix the implementation or open a BLOCKED note in tasks.md
```

### 2. Ruff

```bash
ruff check .
# Expected: no issues, exit code 0
# Fix all issues before continuing
```

### 3. Scope verification

```bash
git diff --name-only feature/phase-1/iteration-2
# Only tests/test_auth.py must appear (plus iterations/p1-i2/tasks.md after step 5)
# Unexpected files = stop and investigate
```

### 4. Commit and push

```bash
git add tests/test_auth.py
git commit -m "test: 14 auth tests — login, logout, session protection, gate ordering (I2-T5)"
git push -u origin feature/p1-i2/t5-tests
```

### 5. Open PR

```bash
gh pr create \
  --base feature/phase-1/iteration-2 \
  --head feature/p1-i2/t5-tests \
  --title "I2-T5: Auth tests + iteration close" \
  --body "14 tests: login success/failure, session user_id type, logout POST-only, protected route access, auth gate ordering, deleted user handling. 25 total pass. Ruff clean."
```

### 6. Mark PR ready (after all task PRs merged to iteration branch)

```bash
gh pr ready feature/phase-1/iteration-2
```

### 7. Update tasks.md

Set I2-T5 to ✅ DONE and iteration Status to ✔ COMPLETE in `iterations/p1-i2/tasks.md`.

---

## Acceptance checklist

- [ ] 14 tests exist in `tests/test_auth.py` — all 14 names match the spec exactly
- [ ] Two fixtures: `client` (balance pre-set) and `fresh_client` (no balance)
- [ ] `test_login_sets_session_user_id` verifies integer session via dashboard render, not just redirect
- [ ] `test_login_does_not_reveal_field` checks error messages are identical for wrong user/pass
- [ ] `test_logout_must_be_post` verifies 405 on GET
- [ ] `test_opening_balance_gate_before_auth` uses `fresh_client` fixture
- [ ] `test_deleted_user_treated_as_unauthenticated` deletes user from db and hits protected route
- [ ] `pytest -v` → 25 passed (11 P1-I1 + 14 new), exit code 0
- [ ] `ruff check .` → clean, exit code 0
- [ ] Scope: only `tests/test_auth.py` modified (plus tasks.md status update)
- [ ] tasks.md Status updated to ✔ COMPLETE

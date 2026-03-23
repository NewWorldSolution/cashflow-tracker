"""Tests for P1-I2: login, logout, session protection, and auth gate ordering."""
import os
import sqlite3

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
        c.db_path = db_path  # expose for tests that need direct DB access
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


# ── login page ────────────────────────────────────────────────────────────────

def test_login_page_loads(client):
    """GET /auth/login returns 200 when opening balance is set and no session."""
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert "Logowanie" in r.text


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
    """Correct username, wrong password → 401, translated error."""
    r = client.post("/auth/login", data={"username": "owner", "password": "wrongpass"})
    assert r.status_code == 401
    assert "Nieprawidłowe dane logowania" in r.text


def test_login_wrong_username(client):
    """Unknown username → 401, translated error."""
    r = client.post("/auth/login", data={"username": "nobody", "password": "owner123"})
    assert r.status_code == 401
    assert "Nieprawidłowe dane logowania" in r.text


def test_login_empty_fields(client):
    """Empty username and password → 401, translated error."""
    r = client.post("/auth/login", data={"username": "", "password": ""})
    assert r.status_code == 401
    assert "Nazwa użytkownika i hasło są wymagane" in r.text


def test_login_does_not_reveal_field(client):
    """Error message is identical for wrong username and wrong password."""
    r_user = client.post("/auth/login", data={"username": "nobody", "password": "x"})
    r_pass = client.post("/auth/login", data={"username": "owner", "password": "wrong"})
    assert "Nieprawidłowe dane logowania" in r_user.text
    assert "Nieprawidłowe dane logowania" in r_pass.text
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
    login = client.post("/auth/login", data={"username": "owner", "password": "owner123"})
    assert login.status_code == 302

    # Delete owner from db using path stored on the fixture client — no hardcoded fallback
    conn = sqlite3.connect(client.db_path)
    conn.execute("DELETE FROM users WHERE username = 'owner'")
    conn.commit()
    conn.close()

    # Hit protected route with the now-stale session
    r = client.get("/", cookies=login.cookies)
    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]

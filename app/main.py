import os
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from jinja2 import pass_context

from app.i18n import format_amount, format_date, format_datetime, translate
from db.init_db import initialise_db

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cashflow.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT not in ("production", "development", "test"):
    raise ValueError(
        f"ENVIRONMENT must be 'production', 'development', or 'test', got: {ENVIRONMENT!r}"
    )

ALLOWED_HOSTS_RAW = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS: list[str] = [h.strip() for h in ALLOWED_HOSTS_RAW.split(",") if h.strip()]

_env_locale = os.getenv("DEFAULT_LOCALE", "pl").lower()
if _env_locale not in ("en", "pl"):
    _env_locale = "pl"

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Copy .env.example to .env and set a strong secret key."
    )


_memory_keeper: sqlite3.Connection | None = None

EXEMPT_PATHS = {
    "/settings/opening-balance", "/auth/login", "/auth/logout", "/favicon.ico",
    "/lang/en", "/lang/pl",
}
EXEMPT_PREFIXES = ("/static", "/docs", "/openapi.json")


def _is_postgres(url: str) -> bool:
    return url.startswith("postgresql://") or url.startswith("postgres://")


def _connect(url: str):
    """Return a live database connection for the given URL.

    Returns sqlite3.Connection for SQLite URLs.
    Returns a raw psycopg2 connection for PostgreSQL URLs.

    NOTE: The raw psycopg2 connection is NOT yet compatible with the service
    layer — it uses ? placeholders and sqlite3.Row-style access. T3 wraps
    this in _PgConnectionWrapper to solve both problems. T1 intentionally
    returns the raw connection so T3 has a clean foundation to wrap.

    :memory: uses file::memory:?cache=shared so all connections in the process
    share the same in-memory database. A module-level keeper connection is held
    open so SQLite does not destroy the database between request connections.
    """
    if _is_postgres(url):
        import psycopg2

        conn = psycopg2.connect(url)
        conn.autocommit = False
        return conn

    sqlite_path = url.removeprefix("sqlite:///./").removeprefix("sqlite:///")

    global _memory_keeper
    if sqlite_path in (":memory:", ""):
        if _memory_keeper is None:
            _memory_keeper = sqlite3.connect(
                "file::memory:?cache=shared", uri=True, check_same_thread=False
            )
        return sqlite3.connect(
            "file::memory:?cache=shared", uri=True, check_same_thread=False
        )
    return sqlite3.connect(sqlite_path, check_same_thread=False)


def get_db():
    """FastAPI dependency — returns a live database connection.

    Usage in route:
        db = Depends(get_db)
    """
    conn = _connect(DATABASE_URL)
    if not _is_postgres(DATABASE_URL):
        conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _is_exempt(path: str) -> bool:
    """Return True if path bypasses both opening-balance and auth gates."""
    normalised = path.rstrip("/") or "/"
    if normalised in EXEMPT_PATHS:
        return True
    return any(normalised.startswith(prefix) for prefix in EXEMPT_PREFIXES)


class AuthGate(BaseHTTPMiddleware):
    """Single middleware enforcing both opening-balance and auth checks."""

    async def dispatch(self, request: Request, call_next):
        if _is_exempt(request.url.path):
            return await call_next(request)

        from app.services.auth_service import get_current_user, get_opening_balance

        conn = _connect(DATABASE_URL)
        if not _is_postgres(DATABASE_URL):
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


class LocaleMiddleware(BaseHTTPMiddleware):
    """Read locale from session and expose on request state."""

    async def dispatch(self, request: Request, call_next):
        request.state.locale = request.session.get("locale", _env_locale)
        return await call_next(request)


class FlashMessageMiddleware(BaseHTTPMiddleware):
    """Pop flash data from the session and expose it on the request state."""

    async def dispatch(self, request: Request, call_next):
        request.state.flash = request.session.pop("flash", None)
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise database on startup."""
    conn = _connect(DATABASE_URL)
    initialise_db(conn)
    conn.close()
    yield


def create_app(database_url: str | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        database_url: Override the database path (used in tests).
    """
    global DATABASE_URL
    if database_url:
        DATABASE_URL = database_url

    if ENVIRONMENT == "production" and not ALLOWED_HOSTS:
        raise RuntimeError(
            "ALLOWED_HOSTS must be set in production. "
            "Example: ALLOWED_HOSTS=mycashflow.azurewebsites.net"
        )

    # NOTE: SQL placeholder style — SQLite uses ?, PostgreSQL uses %s.
    # Service layer uses ? throughout. T3 (pg-migration) handles placeholder
    # compatibility via a thin adapter or by patching the query layer.

    # Eager init — idempotent (CREATE IF NOT EXISTS / INSERT OR IGNORE).
    # Runs here so TestClient without a context manager has a ready schema.
    # Lifespan runs the same call again on production startup — harmless.
    conn = _connect(DATABASE_URL)
    initialise_db(conn)
    conn.close()

    app = FastAPI(
        title="cashflow-tracker",
        lifespan=lifespan,
        debug=(ENVIRONMENT == "development"),
    )

    app.add_middleware(AuthGate)
    app.add_middleware(LocaleMiddleware)
    app.add_middleware(FlashMessageMiddleware)
    if ENVIRONMENT == "production":
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        session_cookie="session",
        max_age=8 * 60 * 60,
        https_only=(ENVIRONMENT == "production"),
        same_site="lax",
    )

    from app.routes.settings import router as settings_router
    from app.routes.auth import router as auth_router
    from app.routes.dashboard import router as dashboard_router
    from app.routes.transactions import router as transactions_router

    app.include_router(settings_router)
    app.include_router(auth_router)
    app.include_router(dashboard_router)
    app.include_router(transactions_router)

    # Register t() as a Jinja2 global on every route module's template env.
    # Uses @pass_context so {{ t('key') }} can read locale from request.state.
    @pass_context
    def _t(context, key: str) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", _env_locale)
        return translate(key, locale)

    from app.routes.settings import templates as settings_tpl
    from app.routes.auth import templates as auth_tpl
    from app.routes.dashboard import templates as dashboard_tpl
    from app.routes.transactions import templates as transactions_tpl

    @pass_context
    def _format_date(context, value) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", _env_locale)
        return format_date(value, locale)

    @pass_context
    def _format_amount(context, value) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", _env_locale)
        return format_amount(value, locale)

    @pass_context
    def _format_datetime(context, value) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", _env_locale)
        return format_datetime(value, locale)

    for tpl in (settings_tpl, auth_tpl, dashboard_tpl, transactions_tpl):
        tpl.env.globals["t"] = _t
        tpl.env.globals["format_date"] = _format_date
        tpl.env.globals["format_amount"] = _format_amount
        tpl.env.globals["format_datetime"] = _format_datetime

    @app.get("/lang/{locale}")
    async def switch_language(locale: str, request: Request):
        if locale in ("en", "pl"):
            request.session["locale"] = locale
        referer = request.headers.get("referer", "/")
        return RedirectResponse(url=referer, status_code=302)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


app = create_app()

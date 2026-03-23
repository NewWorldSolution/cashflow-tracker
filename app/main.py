import os
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from jinja2 import pass_context

from app.i18n import DEFAULT_LOCALE, format_amount, format_date, format_datetime, translate
from db.init_db import initialise_db

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")
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


def _connect(url: str) -> sqlite3.Connection:
    """Open a SQLite connection, using shared-cache URI for :memory: databases.

    :memory: uses file::memory:?cache=shared so all connections in the process
    share the same in-memory database. A module-level keeper connection is held
    open so SQLite does not destroy the database between request connections.
    """
    global _memory_keeper
    if url == ":memory:":
        if _memory_keeper is None:
            _memory_keeper = sqlite3.connect(
                "file::memory:?cache=shared", uri=True, check_same_thread=False
            )
        return sqlite3.connect(
            "file::memory:?cache=shared", uri=True, check_same_thread=False
        )
    return sqlite3.connect(url, check_same_thread=False)


def get_db() -> sqlite3.Connection:
    """FastAPI dependency — returns a live SQLite connection.

    Usage in route:
        db: sqlite3.Connection = Depends(get_db)
    """
    conn = _connect(DATABASE_URL)
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
        request.state.locale = request.session.get("locale", DEFAULT_LOCALE)
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

    # Eager init — idempotent (CREATE IF NOT EXISTS / INSERT OR IGNORE).
    # Runs here so TestClient without a context manager has a ready schema.
    # Lifespan runs the same call again on production startup — harmless.
    conn = _connect(DATABASE_URL)
    initialise_db(conn)
    conn.close()

    app = FastAPI(title="cashflow-tracker", lifespan=lifespan)

    app.add_middleware(AuthGate)
    app.add_middleware(LocaleMiddleware)
    app.add_middleware(FlashMessageMiddleware)
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

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
        locale = getattr(getattr(request, "state", None), "locale", DEFAULT_LOCALE)
        return translate(key, locale)

    from app.routes.settings import templates as settings_tpl
    from app.routes.auth import templates as auth_tpl
    from app.routes.dashboard import templates as dashboard_tpl
    from app.routes.transactions import templates as transactions_tpl

    @pass_context
    def _format_date(context, value) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", DEFAULT_LOCALE)
        return format_date(value, locale)

    @pass_context
    def _format_amount(context, value) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", DEFAULT_LOCALE)
        return format_amount(value, locale)

    @pass_context
    def _format_datetime(context, value) -> str:
        request = context.get("request")
        locale = getattr(getattr(request, "state", None), "locale", DEFAULT_LOCALE)
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

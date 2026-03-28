import os
import json
import logging
import sqlite3
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
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
    "/health",
}
EXEMPT_PREFIXES = ("/static", "/docs", "/openapi.json")


class _PgRow(dict):
    """Mapping row that also supports positional access for legacy callers."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class _PgCursorWrapper:
    """Wrap a psycopg2 cursor and normalise row access patterns."""

    def __init__(self, cursor):
        self._cursor = cursor

    def _wrap_row(self, row):
        if row is None:
            return None
        if isinstance(row, dict):
            return _PgRow(row)
        return row

    def fetchone(self):
        return self._wrap_row(self._cursor.fetchone())

    def fetchall(self):
        return [self._wrap_row(row) for row in self._cursor.fetchall()]

    def fetchmany(self, size=None):
        if size is None:
            rows = self._cursor.fetchmany()
        else:
            rows = self._cursor.fetchmany(size)
        return [self._wrap_row(row) for row in rows]

    def __iter__(self):
        for row in self._cursor:
            yield self._wrap_row(row)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class _PgConnectionWrapper:
    """Wrap psycopg2 so service-layer code can keep using SQLite-style SQL."""

    def __init__(self, conn):
        self._conn = conn

    def _adapt_sql(self, sql: str) -> str:
        if sql.strip() == "SELECT last_insert_rowid()":
            return "SELECT LASTVAL()"
        return sql.replace("?", "%s")

    def execute(self, sql: str, params=None):
        import psycopg2.extras

        adapted = self._adapt_sql(sql)
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if params is None:
            cur.execute(adapted)
        else:
            cur.execute(adapted, params)
        return _PgCursorWrapper(cur)

    def executescript(self, sql: str):
        for stmt in [s.strip() for s in sql.split(";\n") if s.strip()]:
            self.execute(stmt)
        self._conn.commit()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def _is_postgres(target) -> bool:
    if isinstance(target, str):
        return target.startswith("postgresql://") or target.startswith("postgres://")
    if isinstance(target, _PgConnectionWrapper):
        return True
    return type(target).__module__.startswith("psycopg2")


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
        )


def _configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    if ENVIRONMENT == "production":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(name)s  %(message)s")
        )
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


_configure_logging()
logger = logging.getLogger(__name__)


def _connect(url: str):
    """Return a live database connection for the given URL.

    Returns sqlite3.Connection for SQLite URLs.
    Returns _PgConnectionWrapper for PostgreSQL URLs.

    :memory: uses file::memory:?cache=shared so all connections in the process
    share the same in-memory database. A module-level keeper connection is held
    open so SQLite does not destroy the database between request connections.
    """
    if _is_postgres(url):
        import psycopg2

        conn = psycopg2.connect(url)
        conn.autocommit = False
        return _PgConnectionWrapper(conn)

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
    if not _is_postgres(conn):
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
        if not _is_postgres(conn):
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


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %d %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise database on startup."""
    conn = _connect(DATABASE_URL)
    initialise_db(conn)
    conn.close()
    logger.info(
        "cashflow-tracker started [environment=%s, database=%s]",
        ENVIRONMENT,
        "postgresql" if _is_postgres(DATABASE_URL) else "sqlite",
    )
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

    # Eager init — idempotent (CREATE IF NOT EXISTS / ON CONFLICT DO NOTHING).
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
    app.state.environment = ENVIRONMENT

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
    app.add_middleware(RequestLoggingMiddleware)

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

    @app.get("/health")
    async def health_check():
        try:
            conn = _connect(DATABASE_URL)
            try:
                if _is_postgres(DATABASE_URL):
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                else:
                    conn.execute("SELECT 1")
            finally:
                conn.close()
            db_status = "connected"
            status_code = 200
        except Exception:
            db_status = "unreachable"
            status_code = 503

        return JSONResponse(
            content={
                "status": "healthy" if status_code == 200 else "unhealthy",
                "database": db_status,
                "version": "1.0.0",
                "environment": ENVIRONMENT,
            },
            status_code=status_code,
        )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


app = create_app()

if ENVIRONMENT == "production":
    from whitenoise import WhiteNoise

    app = WhiteNoise(app, root="static/", prefix="static")

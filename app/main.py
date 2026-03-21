import os
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

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


class OpeningBalanceGate(BaseHTTPMiddleware):
    """Middleware that enforces the opening balance setup requirement.

    Redirects all requests to /settings/opening-balance (302) when the
    opening_balance setting is not present in the database.
    /settings/opening-balance is exempt so the setup form is always reachable.
    A missing opening balance is not a warning — it is a hard block.
    """

    EXEMPT_PATHS = {"/settings/opening-balance"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in self.EXEMPT_PATHS:
            conn = _connect(DATABASE_URL)
            try:
                row = conn.execute(
                    "SELECT value FROM settings WHERE key = 'opening_balance'"
                ).fetchone()
            except sqlite3.OperationalError:
                # settings table not yet created — treat as not set
                row = None
            finally:
                conn.close()
            if row is None:
                return RedirectResponse(url="/settings/opening-balance", status_code=302)
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

    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    app.add_middleware(OpeningBalanceGate)

    from app.routes.settings import router as settings_router
    app.include_router(settings_router)

    return app


app = create_app()

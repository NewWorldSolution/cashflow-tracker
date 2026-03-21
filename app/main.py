import os
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
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


def get_db() -> sqlite3.Connection:
    """FastAPI dependency — returns a live SQLite connection.

    Usage in route:
        db: sqlite3.Connection = Depends(get_db)
    """
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


async def require_opening_balance(request: Request, db: sqlite3.Connection = Depends(get_db)):
    """Redirect to opening balance setup if it has not been set.

    Applied as a dependency to all routes except /settings/opening-balance.
    A missing opening balance is not a warning — it is a hard block.
    """
    exempt_paths = {"/settings/opening-balance"}
    if request.url.path in exempt_paths:
        return

    row = db.execute(
        "SELECT value FROM settings WHERE key = 'opening_balance'"
    ).fetchone()

    if row is None:
        return RedirectResponse(url="/settings/opening-balance", status_code=302)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise database on startup."""
    conn = sqlite3.connect(DATABASE_URL)
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

    app = FastAPI(title="cashflow-tracker", lifespan=lifespan)

    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

    # Register routers — settings router registered after I1-T3 merges
    # app.include_router(settings_router)

    return app


app = create_app()

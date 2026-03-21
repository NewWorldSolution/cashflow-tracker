# I1-T2 — FastAPI Skeleton
**Agent:** Claude Code
**Branch:** `feature/p1-i1/t2-fastapi`
**PR target:** `feature/phase-1/iteration-1`

---

## Before starting — read these files in order

```
CLAUDE.md                                    ← architecture rules
iterations/p1-i1/tasks.md                   ← confirm I1-T1 is DONE before proceeding
skills/cash-flow/schema/SKILL.md             ← table structure and db boundary rules
skills/cash-flow/auth_logic/SKILL.md         ← identity rules: session stores users.id (int), never username string
skills/cash-flow/error_handling/SKILL.md     ← no silent failures
```

Confirm I1-T1 is DONE in `tasks.md`. If it is not DONE, stop and wait.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-1
git worktree add -b feature/p1-i1/t2-fastapi ../cashflow-tracker-t2 feature/phase-1/iteration-1
cd ../cashflow-tracker-t2
```

---

## What already exists (from I1-T1)

```
db/__init__.py
db/schema.sql
db/init_db.py          ← provides initialise_db(conn)
seed/categories.sql
seed/users.sql
seed/__init__.py
requirements.txt       ← all deps installed
.env.example
.gitignore
```

Do not recreate or modify any of these.

---

## What to build

### Allowed files (this task only)

```
app/__init__.py         ← new: empty package init
app/main.py             ← new: FastAPI app factory, middleware, db dependency, opening balance gate
app/routes/__init__.py  ← new: empty package init
```

Do not create `app/routes/settings.py` — that is I1-T3 (Codex).
Do not create templates — that is I1-T4.

---

## app/main.py — implement exactly this

### Environment and startup

```python
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
```

### Database dependency

```python
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
```

### Opening balance gate

```python
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
```

### Lifespan and app factory

```python
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
```

---

## Rules

- **SECRET_KEY missing** → `RuntimeError` at import time, not at request time. The app must not start silently with a weak default.
- **Opening balance gate** → hard redirect (302), not a flash warning. Applied to every route except `/settings/opening-balance`.
- **`get_db()`** → yields a connection with `row_factory = sqlite3.Row` so rows are accessible by column name. Always closes the connection in `finally`.
- **Session middleware** → `SessionMiddleware` from `starlette`. `secret_key` is `SECRET_KEY` from env.
- **No validation logic in this file** — `app/main.py` is infrastructure only.

---

## Test baseline

```bash
# Verify the baseline before writing any code
pytest
ruff check .
# Both must exit 0 (0 tests at this point is fine)
```

After implementing:

```bash
# Start the app — confirm it starts without error
SECRET_KEY=test-key DATABASE_URL=./test.db uvicorn app.main:app --port 8001
# Expected: Uvicorn running, no crash

# Confirm missing key fails
unset SECRET_KEY
python -c "from app.main import app"
# Expected: RuntimeError mentioning SECRET_KEY
```

---

## Commit and PR

```bash
git add app/__init__.py app/main.py app/routes/__init__.py
git commit -m "feat: FastAPI skeleton with session middleware and opening balance gate (I1-T2)"
git push -u origin feature/p1-i1/t2-fastapi
gh pr create \
  --base feature/phase-1/iteration-1 \
  --head feature/p1-i1/t2-fastapi \
  --title "I1-T2: FastAPI skeleton" \
  --body "App factory, session middleware, get_db() dependency, opening balance redirect gate. SECRET_KEY missing fails loudly at startup."
```

Update `iterations/p1-i1/tasks.md` — set I1-T2 to ✅ DONE.

---

## Acceptance checklist

- [ ] `from app.main import app` fails with `RuntimeError` when `SECRET_KEY` is not set
- [ ] App starts normally when `SECRET_KEY` is present
- [ ] `get_db()` yields a `sqlite3.Connection` with `row_factory = sqlite3.Row`
- [ ] Any request to a non-exempt path redirects to `/settings/opening-balance` when balance is not set
- [ ] `/settings/opening-balance` is not redirected (exempt)
- [ ] No validation logic in `app/main.py`
- [ ] Ruff clean

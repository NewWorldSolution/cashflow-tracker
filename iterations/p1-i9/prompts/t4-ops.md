# I9-T4 — Health Check + Logging + Static Files + SANDBOX Removal

**Branch:** `feature/p1-i9/t4-ops`
**Base:** `feature/phase-1/iteration-9` (after T2 merged)
**Depends on:** I9-T2

---

## Goal

Add production-ready operational features: a health check endpoint for Azure monitoring, structured logging (JSON in production, plain in dev), request logging middleware, WhiteNoise for static file serving in production, and the SANDBOX banner removal. After this task the app is operationally observable and signals to users that data is now permanent.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i9/prompt.md
app/main.py                          ← ENVIRONMENT variable from T2
app/templates/base.html              ← current SANDBOX banner location
app/routes/transactions.py           ← example route for health check style reference
```

---

## Deliverables

### 1. Health check endpoint `GET /health`

Add a `/health` route directly in `app/main.py` (not in a separate router file — it's a single endpoint).

The endpoint:
1. Checks database connectivity by running a cheap query
2. Returns 200 + JSON body if healthy
3. Returns 503 + JSON body if the database is unreachable

```python
from fastapi.responses import JSONResponse

@app.get("/health")
async def health_check():
    try:
        conn = _connect(DATABASE_URL)
        conn.execute("SELECT 1")
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
```

Add `/health` to `EXEMPT_PATHS` so unauthenticated monitoring probes can hit it:

```python
EXEMPT_PATHS = {
    "/settings/opening-balance", "/auth/login", "/auth/logout",
    "/favicon.ico", "/lang/en", "/lang/pl",
    "/health",   # ← add
}
```

### 2. Structured logging

Add logging configuration to `app/main.py`, called once at module level (before `create_app()`).

**Development / test** — standard format, INFO level:
```
2026-03-27 12:00:00 INFO     app.main  Application starting [environment=development]
```

**Production** — JSON format, INFO level:
```json
{"timestamp": "2026-03-27T12:00:00Z", "level": "INFO", "logger": "app.main", "message": "..."}
```

Implementation:

```python
import logging
import json
import sys
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        })


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
```

### 3. Request logging middleware

Add `RequestLoggingMiddleware` to `app/main.py`. Log every request at INFO level with method, path, status code, and response time.

```python
import time

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
```

Add `RequestLoggingMiddleware` in `create_app()` — register it **last** so it wraps all other middleware and measures total response time. Starlette applies middleware in reverse registration order (LIFO), so add it after `SessionMiddleware`:

```python
app.add_middleware(RequestLoggingMiddleware)  # outermost — added last
```

Do NOT log sensitive paths (passwords are in POST bodies, not paths — path logging is safe). Do NOT log request/response bodies.

### 4. Static file serving with WhiteNoise

The current `app.mount("/static", StaticFiles(...))` works for development but serves files via Python in production. WhiteNoise is the recommended lightweight static file server for FastAPI/WSGI apps on Azure App Service.

Add `whitenoise>=6.0.0` to `requirements.txt`.

Wrap the app with WhiteNoise at **module level**, after `create_app()`, conditional on `ENVIRONMENT`:

```python
# bottom of main.py — after create_app()
from whitenoise import WhiteNoise

app = create_app()

if ENVIRONMENT == "production":
    app = WhiteNoise(app, root="static", prefix="static")
```

- In production: `uvicorn app.main:app` gets the WhiteNoise-wrapped ASGI app. WhiteNoise intercepts all `/static/*` requests before they reach FastAPI — the `app.mount("/static", StaticFiles(...))` inside `create_app()` remains present but is never reached for static paths in production.
- In development: `app` is the plain FastAPI instance; `StaticFiles` serves `/static/` as before.

Do NOT use `app.middleware_stack = None` — that is an internal FastAPI detail and is not a safe or supported operation.

### 5. Remove SANDBOX banner from `base.html`

The SANDBOX banner at lines 10–12 of `app/templates/base.html` has been visible since I1. It must be removed at go-live.

Make the banner conditional on `ENVIRONMENT` rather than hard-removing it, so the template stays useful in dev:

**Current `base.html` lines 10–12:**
```html
    <div class="sandbox-banner">
        {{ t('sandbox_banner') }}
    </div>
```

**Replace with:**
```html
    {% if request.app.state.environment != 'production' %}
    <div class="sandbox-banner">
        {{ t('sandbox_banner') }}
    </div>
    {% endif %}
```

To make `request.app.state.environment` available, set it on app startup in `create_app()`:

```python
app.state.environment = ENVIRONMENT
```

This way:
- `ENVIRONMENT=production` → banner hidden → users see production app
- `ENVIRONMENT=development` (default) → banner visible → clear sandbox signal during dev

### 6. Log startup message

In the lifespan function, log the startup state:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = _connect(DATABASE_URL)
    initialise_db(conn)
    conn.close()
    logger.info(
        "cashflow-tracker started [environment=%s, database=%s]",
        ENVIRONMENT,
        "postgresql" if _is_postgres_url(DATABASE_URL) else "sqlite",
    )
    yield
```

Where `_is_postgres_url(url)` checks the URL string directly (not a connection object) — used here since no connection is open at log time:

```python
def _is_postgres_url(url: str) -> bool:
    return url.startswith(("postgresql://", "postgres://"))
```

---

## Important Rules

- **`/health` must not require authentication** — add to `EXEMPT_PATHS`
- **Do not log passwords, session tokens, or personal data** — path-only logging is safe
- **SANDBOX banner must still show in `development`** — conditional, not hard-deleted
- **WhiteNoise wraps production only** — dev still uses FastAPI's `StaticFiles`
- **Do not change any route paths** — no breaking URL changes
- **Do not add any new business logic or validation**

---

## Allowed Files

```text
app/main.py
app/templates/base.html
requirements.txt       ← add whitenoise
iterations/p1-i9/tasks.md
```

---

## Acceptance Criteria

- [ ] `GET /health` returns `{"status": "healthy", "database": "connected", ...}` with status 200
- [ ] `GET /health` returns status 503 when database is unreachable
- [ ] `/health` is in `EXEMPT_PATHS` — no auth required
- [ ] JSON logging active when `ENVIRONMENT=production`
- [ ] Plain text logging active when `ENVIRONMENT=development`
- [ ] Request logging middleware logs method, path, status, response time for every request
- [ ] `whitenoise>=6.0.0` in `requirements.txt`
- [ ] WhiteNoise wraps the app when `ENVIRONMENT=production`
- [ ] SANDBOX banner hidden when `ENVIRONMENT=production`
- [ ] SANDBOX banner still visible when `ENVIRONMENT=development`
- [ ] `app.state.environment` set in `create_app()`
- [ ] Startup log message emitted
- [ ] `pytest -v` passes
- [ ] `ruff check .` passes

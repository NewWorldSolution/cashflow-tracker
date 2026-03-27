# Review — I9-T4: Health Check + Logging + Static Files + SANDBOX Removal
**Branch:** `feature/p1-i9/t4-ops`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompts/t4-ops.md`, `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `GET /health` endpoint in `app/main.py` — returns `{"status", "database", "version", "environment"}`, HTTP 200 when healthy, 503 when DB unreachable
- `/health` added to `EXEMPT_PATHS` — no authentication required
- `_JsonFormatter` + `_configure_logging()` in `app/main.py` — JSON format in production, plain text in development; called once at module level
- `RequestLoggingMiddleware` logging method, path, status code, response time (ms) — registered last in `create_app()` so it wraps all other middleware
- `whitenoise>=6.0.0` added to `requirements.txt`
- WhiteNoise wraps the ASGI app at module level when `ENVIRONMENT == "production"`; dev uses FastAPI's `StaticFiles` mount as-is
- SANDBOX banner in `app/templates/base.html` made conditional: visible when `ENVIRONMENT != production`, hidden in production
- `app.state.environment = ENVIRONMENT` set in `create_app()` so the template can read it
- Startup log message emitted from the lifespan function
- No schema changes, no route changes, no CI/CD work

---

## Review Steps

1. **Diff scope** — confirm only these files appear:
   - `app/main.py`
   - `app/templates/base.html`
   - `requirements.txt`
   - iteration planning files under `iterations/p1-i9/`
   Any other files need justification.

2. **`GET /health` endpoint**
   - Defined in `app/main.py` (not in a separate router file)
   - Runs a real DB query (`SELECT 1`) wrapped in a try/except
   - Returns `JSONResponse` with `status`, `database`, `version`, `environment` keys
   - Returns HTTP 200 when query succeeds, HTTP 503 when exception is raised
   - `/health` present in `EXEMPT_PATHS` — not gated by `AuthGate`

3. **Logging**
   - `_JsonFormatter` produces JSON with `timestamp`, `level`, `logger`, `message` keys
   - `_configure_logging()` called at module level, before `create_app()`
   - `ENVIRONMENT == "production"` → JSON formatter; other environments → plain text formatter
   - `logger = logging.getLogger(__name__)` defined at module level
   - No passwords, session tokens, or personal data in logged fields

4. **`RequestLoggingMiddleware`**
   - Logs method, path, status code, and response time in milliseconds
   - Registered in `create_app()` after `SessionMiddleware` (so it is outermost — wraps everything)
   - Does NOT log request/response bodies

5. **WhiteNoise**
   - `whitenoise>=6.0.0` in `requirements.txt`
   - `app = WhiteNoise(app, root="static", prefix="static")` at module level, conditional on `ENVIRONMENT == "production"`
   - Dev path still uses `app.mount("/static", StaticFiles(...))` — unchanged

6. **SANDBOX banner in `base.html`**
   - Wrapped in `{% if request.app.state.environment != 'production' %}` … `{% endif %}`
   - Banner HTML is preserved — just conditionally rendered
   - `app.state.environment = ENVIRONMENT` set in `create_app()` so the Jinja2 context can read it

7. **Startup log**
   - Lifespan function emits an INFO log stating environment and database engine

8. **No scope creep**
   - No schema or route changes
   - No new business logic or validation
   - No CI/CD pipeline files added here (T5 scope)

9. **Run tests and lint:**

```bash
pytest -v
ruff check .
```

Additionally, manually verify:
- `curl http://localhost:8000/health` → `{"status": "healthy", ...}` with 200
- Stop the database (or set `DATABASE_URL` to an invalid URL) → `{"status": "unhealthy", "database": "unreachable"}` with 503

---

## Required Output Format

### 1. Verdict

```text
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```text
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/main.py`, `app/templates/base.html`, `requirements.txt`, and iteration planning files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] `GET /health` defined in `app/main.py`
- [PASS|FAIL] `/health` in `EXEMPT_PATHS` — no auth required
- [PASS|FAIL] health endpoint runs a real DB query (not hardcoded)
- [PASS|FAIL] returns HTTP 200 when DB reachable
- [PASS|FAIL] returns HTTP 503 when DB unreachable
- [PASS|FAIL] response body includes `status`, `database`, `version`, `environment`
- [PASS|FAIL] JSON logging active when `ENVIRONMENT=production`
- [PASS|FAIL] plain text logging active when `ENVIRONMENT=development`
- [PASS|FAIL] `RequestLoggingMiddleware` logs method, path, status, response time
- [PASS|FAIL] middleware registered outermost (after `SessionMiddleware`)
- [PASS|FAIL] no sensitive data logged
- [PASS|FAIL] `whitenoise>=6.0.0` in `requirements.txt`
- [PASS|FAIL] WhiteNoise wraps app when `ENVIRONMENT=production`
- [PASS|FAIL] SANDBOX banner hidden when `ENVIRONMENT=production`
- [PASS|FAIL] SANDBOX banner visible when `ENVIRONMENT=development`
- [PASS|FAIL] `app.state.environment` set in `create_app()`
- [PASS|FAIL] startup log message emitted from lifespan
- [PASS|FAIL] no schema, route, service, or CI/CD changes
- [PASS|FAIL] `pytest -v` passes
- [PASS|FAIL] `ruff check .` passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

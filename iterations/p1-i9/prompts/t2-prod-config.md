# I9-T2 — Production Config + Secrets

**Branch:** `feature/p1-i9/t2-prod-config`
**Base:** `feature/phase-1/iteration-9` (after T1 merged)
**Depends on:** I9-T1

---

## Goal

Harden the application configuration for production. After this task: all secrets come from environment variables, no hardcoded values exist, the app behaves differently in `production` vs `development` vs `test` environments (allowed hosts, session security), and a `.env.example` documents every variable an operator needs to set.

This task is **configuration only** — no new features, no schema changes, no route changes.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i9/prompt.md
app/main.py
```

---

## Deliverables

### 1. `ENVIRONMENT` variable and mode detection

Add `ENVIRONMENT` detection to `app/main.py`. Three valid values: `production`, `development`, `test`.

```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if ENVIRONMENT not in ("production", "development", "test"):
    raise ValueError(
        f"ENVIRONMENT must be 'production', 'development', or 'test', got: {ENVIRONMENT!r}"
    )
```

Do NOT use `assert` — it is silently disabled when Python runs with the `-O` (optimise) flag, which some production runtimes enable.

Use `ENVIRONMENT` to gate:
- Debug mode: enabled only in `development`
- Structured logging: JSON only in `production`
- SANDBOX banner: visible when `ENVIRONMENT != production` (T4 implements the template side)

### 2. `SECRET_KEY` enforcement

Already enforced — `main.py` raises `RuntimeError` if `SECRET_KEY` is missing. No change needed. Verify it still works after refactoring.

### 3. `ALLOWED_HOSTS` validation

Add allowed hosts checking for production. Parse from environment:

```python
ALLOWED_HOSTS_RAW = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS: list[str] = [h.strip() for h in ALLOWED_HOSTS_RAW.split(",") if h.strip()]
```

In `create_app()`, if `ENVIRONMENT == "production"` and `ALLOWED_HOSTS` is empty, raise `RuntimeError`:

```python
if ENVIRONMENT == "production" and not ALLOWED_HOSTS:
    raise RuntimeError(
        "ALLOWED_HOSTS must be set in production. "
        "Example: ALLOWED_HOSTS=mycashflow.azurewebsites.net"
    )
```

Add `TrustedHostMiddleware` from Starlette when `ENVIRONMENT == "production"`:

```python
from starlette.middleware.trustedhost import TrustedHostMiddleware

if ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
```

### 4. Session cookie security

In `create_app()`, configure `SessionMiddleware` with production-appropriate settings:

```python
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session",
    max_age=8 * 60 * 60,           # 8 hours
    https_only=(ENVIRONMENT == "production"),  # secure cookie in prod
    same_site="lax",
)
```

### 5. `DEFAULT_LOCALE` from environment

The default locale is `pl` in production. Allow override via environment:

```python
_env_locale = os.getenv("DEFAULT_LOCALE", "pl").lower()
if _env_locale not in ("en", "pl"):
    _env_locale = "pl"
```

In `LocaleMiddleware`, use `_env_locale` as the fallback instead of the hardcoded `DEFAULT_LOCALE` import:

```python
request.state.locale = request.session.get("locale", _env_locale)
```

### 6. Create `.env.example`

Create `.env.example` at the repo root with every required and optional variable documented:

```dotenv
# ============================================================
# cashflow-tracker — environment variable template
# Copy to .env for local development.
# In production, set these as Azure App Service Application Settings.
# ============================================================

# REQUIRED — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=replace-with-a-strong-random-secret-key

# Database connection
# Local dev (SQLite):    omit or set to sqlite:///./cashflow.db
# Production (Postgres): postgresql://user:password@host:5432/dbname
DATABASE_URL=sqlite:///./cashflow.db

# Application environment: production | development | test
ENVIRONMENT=development

# Default UI locale: pl | en
DEFAULT_LOCALE=pl

# Allowed hostnames in production (comma-separated)
# Required when ENVIRONMENT=production
# Example: ALLOWED_HOSTS=mycashflow.azurewebsites.net
ALLOWED_HOSTS=
```

### 7. Ensure `.env` is in `.gitignore`

Check `.gitignore` — if `.env` is not listed, add it. `.env.example` must NOT be in `.gitignore`.

---

## Important Rules

- **No schema changes** — this task is config only
- **No new routes** — health check endpoint is T4's scope
- **Do not hardcode secrets** — every secret must come from environment
- **`development` must still work without `ALLOWED_HOSTS`** — only production enforces this
- **Existing tests must pass** — tests run without `ENVIRONMENT` set (defaults to `development`), no `ALLOWED_HOSTS` required
- **Do NOT add CORS middleware** — this is an internal tool with no cross-origin callers

---

## Allowed Files

```text
app/main.py
.env.example            ← create
.gitignore              ← check/update only
iterations/p1-i9/tasks.md
```

---

## Acceptance Criteria

- [ ] `ENVIRONMENT` variable read from env, defaults to `development`, validated against allowed values
- [ ] `ALLOWED_HOSTS` enforced in production (`RuntimeError` if empty)
- [ ] `TrustedHostMiddleware` added when `ENVIRONMENT == "production"`
- [ ] Session cookie uses `https_only=True` in production, `False` in dev/test
- [ ] Session `max_age` set to 8 hours
- [ ] `DEFAULT_LOCALE` read from environment, defaults to `pl`
- [ ] `.env.example` created with all variables documented
- [ ] `.env` present in `.gitignore`
- [ ] App starts in `development` mode without `ALLOWED_HOSTS` set
- [ ] `pytest -v` passes
- [ ] `ruff check .` passes

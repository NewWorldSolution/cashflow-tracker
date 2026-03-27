# Review — I9-T2: Production Config + Secrets
**Branch:** `feature/p1-i9/t2-prod-config`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompts/t2-prod-config.md`, `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `ENVIRONMENT` variable read in `app/main.py`, validated against `production | development | test`, defaulting to `development`
- `ALLOWED_HOSTS` parsed from env as a comma-separated list; `RuntimeError` raised at startup if `ENVIRONMENT == "production"` and `ALLOWED_HOSTS` is empty
- `TrustedHostMiddleware` added to the app when `ENVIRONMENT == "production"`
- `SessionMiddleware` configured with `https_only=(ENVIRONMENT == "production")`, `max_age=8*60*60`, `same_site="lax"`
- `DEFAULT_LOCALE` read from env (default `pl`), validated against `("en", "pl")`; `LocaleMiddleware` uses it as the session fallback instead of the hardcoded import
- `.env.example` created at repo root documenting all five variables: `SECRET_KEY`, `DATABASE_URL`, `ENVIRONMENT`, `DEFAULT_LOCALE`, `ALLOWED_HOSTS`
- `.env` present in `.gitignore`; `.env.example` NOT ignored
- No schema changes, no new routes, no health/logging/static/CI work

---

## Review Steps

1. **Diff scope** — confirm only these files appear:
   - `app/main.py`
   - `.env.example`
   - `.gitignore` (addition only — check `.env` is listed)
   - iteration planning files under `iterations/p1-i9/`
   Any route, template, schema, or service file changes are out of scope.

2. **`ENVIRONMENT` detection in `app/main.py`**
   - Read via `os.getenv("ENVIRONMENT", "development").lower()`
   - Validated via an explicit runtime check against `("production", "development", "test")`
   - Invalid value must raise an error — not silently accepted

3. **`ALLOWED_HOSTS` enforcement**
   - Parsed as `[h.strip() for h in raw.split(",") if h.strip()]`
   - `RuntimeError` raised in `create_app()` when `ENVIRONMENT == "production"` and list is empty
   - `TrustedHostMiddleware` added only when `ENVIRONMENT == "production"`
   - Dev and test modes must start cleanly without `ALLOWED_HOSTS` set

4. **Session middleware hardening**
   - `https_only` is `True` in production, `False` otherwise — never hardcoded to one value
   - `max_age` set to `8 * 60 * 60` (8 hours)
   - `same_site="lax"` present

5. **`DEFAULT_LOCALE` from environment**
   - `os.getenv("DEFAULT_LOCALE", "pl")` with lowercase normalisation
   - Invalid values fall back to `"pl"` silently (not an error — defensive default is correct here)
   - `LocaleMiddleware.dispatch` uses the env-derived value, not a hardcoded import

6. **`.env.example`**
   - All five variables documented: `SECRET_KEY`, `DATABASE_URL`, `ENVIRONMENT`, `DEFAULT_LOCALE`, `ALLOWED_HOSTS`
   - No real secret values — placeholders only
   - Guidance comment explaining how to generate `SECRET_KEY`

7. **`.gitignore`**
   - `.env` is listed (not `.env.example`)

8. **No premature scope creep**
   - `/health` endpoint not added here (T4 scope)
   - Logging middleware not added here (T4 scope)
   - WhiteNoise not added here (T4 scope)
   - `db/init_db.py` not touched

9. **Run tests and lint:**

```bash
pytest -v
ruff check .
```

Expected: all tests pass without `ENVIRONMENT` set (defaults to `development`), ruff clean.

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

Files modified outside `app/main.py`, `.env.example`, `.gitignore`, and iteration planning files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] `ENVIRONMENT` read from env, defaults to `development`, validated against allowed values
- [PASS|FAIL] `ALLOWED_HOSTS` enforced in production — `RuntimeError` if empty
- [PASS|FAIL] `TrustedHostMiddleware` added only when `ENVIRONMENT == "production"`
- [PASS|FAIL] session cookie `https_only=True` in production, `False` in dev/test
- [PASS|FAIL] session `max_age` set to 8 hours (28800 seconds)
- [PASS|FAIL] `DEFAULT_LOCALE` read from env, defaults to `"pl"`
- [PASS|FAIL] `LocaleMiddleware` uses env-derived locale, not hardcoded import
- [PASS|FAIL] `.env.example` created with all five variables and no real secrets
- [PASS|FAIL] `.env` listed in `.gitignore`; `.env.example` not ignored
- [PASS|FAIL] app starts without error when `ENVIRONMENT` is unset (development mode)
- [PASS|FAIL] no health/logging/static/CI work mixed in
- [PASS|FAIL] no schema or route changes
- [PASS|FAIL] `pytest -v` passes
- [PASS|FAIL] `ruff check .` passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

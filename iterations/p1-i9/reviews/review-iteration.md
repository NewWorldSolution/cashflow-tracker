# QA Review — P1-I9: Azure / Server / Deployment
**Reviewer:** QA agent
**Branch:** `feature/phase-1/iteration-9`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i9/tasks.md`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/p1-i9/prompts/t1-azure-setup.md`, `iterations/p1-i9/prompts/t2-prod-config.md`, `iterations/p1-i9/prompts/t3-pg-migration.md`, `iterations/p1-i9/prompts/t4-ops.md`, `iterations/p1-i9/prompts/t5-deploy-pipeline.md`, `CLAUDE.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 9. Individual task reviews verified each task in isolation — this review verifies the whole iteration integrates correctly before merge to `main`. Focus on cross-task integration: do the pieces fit together, are there contradictions between tasks, and does the final result match the go-live requirements?

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What this iteration was supposed to deliver

1. **T1 — Connection layer skeleton** in `app/main.py`: `_is_postgres()`, refactored `_connect()` returning raw psycopg2 for PostgreSQL, updated `get_db()` and `AuthGate`, `psycopg2-binary` in requirements, `docs/deployment.md` stub. Full PostgreSQL execution deferred to T3.
2. **T2 — Production config hardening**: `ENVIRONMENT` detection and validation (if/raise, not assert), `ALLOWED_HOSTS` enforcement with `TrustedHostMiddleware` in production, session cookie `https_only`, `DEFAULT_LOCALE` from env, `.env.example`, `.env` in `.gitignore`
3. **T3 — PostgreSQL migration**: single `db/schema.sql` (no `schema_pg.sql`); `_prepare_schema_for_pg()` AUTOINCREMENT→SERIAL; `_apply_pg_post_schema()` for idempotent CHECK constraint; seed files rewritten to `ON CONFLICT DO NOTHING`; `_PgConnectionWrapper` translating `?`→`%s` added to `app/main.py`; dual-engine `db/init_db.py`; PostgreSQL test fixtures; both engines passing
4. **T4 — Ops**: `GET /health` (200/503, unauthenticated), `_configure_logging()` (JSON in prod, plain in dev), `RequestLoggingMiddleware`, WhiteNoise module-level wrapper in production (no `app.middleware_stack = None`), SANDBOX banner conditional on `ENVIRONMENT`, `app.state.environment` set
5. **T5 — Delivery**: `docs/deployment.md` complete runbook, smoke test checklist, `.github/workflows/ci.yml`

---

## Review Steps

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout feature/phase-1/iteration-9
git pull origin feature/phase-1/iteration-9
```

### Step 2 — Full suite and lint

```bash
pytest -v
ruff check .
```

Expected: all tests pass, ruff clean.

If `DATABASE_URL` is available for PostgreSQL:

```bash
DATABASE_URL=postgresql://... pytest -v
```

Expected: all tests pass including the `pg_*` fixtures.

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected modified/created files:

```text
app/main.py
app/templates/base.html
db/schema_pg.sql
db/init_db.py
requirements.txt
.env.example
.gitignore
docs/deployment.md
.github/workflows/ci.yml
tests/conftest.py and/or tests/test_init_db.py
iterations/p1-i9/tasks.md
iterations/p1-i9/prompts/*.md
iterations/p1-i9/reviews/*.md
```

Files that must NOT be modified (no feature regression):

```text
app/services/validation.py
app/services/calculations.py
app/services/transaction_service.py
app/services/auth_service.py
app/routes/transactions.py
app/routes/dashboard.py
app/routes/auth.py
app/routes/settings.py
app/i18n/
db/schema.sql            ← SQLite schema structurally unchanged (AUTOINCREMENT stays)
```

File that must NOT exist:
```text
db/schema_pg.sql         ← second schema file not allowed; single-schema design
```

### Step 4 — Cross-task integration checks

Verify the tasks connect cleanly end to end:

- [ ] `DATABASE_URL` from T2 (`.env.example`) matches the format consumed by T1 (`_is_postgres()`) and T3 (`init_db.py` engine detection)
- [ ] `ENVIRONMENT` from T2 gates T4's WhiteNoise wrapping and SANDBOX banner correctly (`app.state.environment` set in `create_app()`)
- [ ] `_PgConnectionWrapper` (added in T3) is returned by `_connect()` for PostgreSQL — T1's raw psycopg2 return is now wrapped
- [ ] `_is_postgres()` in both `main.py` and `init_db.py` recognises `_PgConnectionWrapper` instances
- [ ] `get_db()` from T1 uses the wrapper path for PostgreSQL so service layer `?` placeholders work end to end
- [ ] `AuthGate` from T1 also uses the wrapper so auth queries run on PostgreSQL
- [ ] `/health` from T4 is in `EXEMPT_PATHS` from T1 — unauthenticated access must work

### Step 5 — Architecture checks

Verify by code inspection that no pre-existing invariants were broken:

- [ ] No hard deletes introduced anywhere
- [ ] No derived values (vat_amount, net_amount, vat_reclaimable, effective_cost) newly stored in the database
- [ ] Validation still centralized in `app/services/validation.py`
- [ ] `category_id` still an integer FK — no free-text category anywhere
- [ ] `logged_by` and `voided_by` still integer FKs
- [ ] PostgreSQL-specific code does not fork business logic (engine differences are in connection/init layer only)
- [ ] All queries still filter `WHERE is_active = TRUE` (soft-delete audit trail intact)

### Step 6 — Production config checks

- [ ] `ENVIRONMENT` validated — invalid values raise an error at startup
- [ ] `ALLOWED_HOSTS` enforced in production (RuntimeError if empty)
- [ ] `SECRET_KEY` still required — existing RuntimeError preserved
- [ ] Session cookie uses `https_only=True` in production
- [ ] No secrets committed in `.env.example`, `docs/deployment.md`, or CI workflow files

### Step 7 — Database/bootstrap checks

- [ ] `db/schema_pg.sql` does NOT exist — single schema maintained
- [ ] `db/schema.sql` structurally unchanged (AUTOINCREMENT stays; `_prepare_schema_for_pg()` adapts it at runtime)
- [ ] `chk_expense_vat_deductible` CHECK applied via `_apply_pg_post_schema()` (PostgreSQL only, idempotent)
- [ ] `init_db.py` runs idempotently on both engines (rerunnable without errors or duplicate rows)
- [ ] Seed files use `ON CONFLICT DO NOTHING` — no `INSERT OR IGNORE` remains

### Step 8 — Ops/runtime checks

- [ ] `GET /health` accessible without authentication
- [ ] `/health` runs a real DB query — not a hardcoded response
- [ ] `/health` returns 503 on DB failure
- [ ] JSON logging active when `ENVIRONMENT=production`
- [ ] Request logging covers method, path, status, response time
- [ ] SANDBOX banner hidden in production, visible in development
- [ ] WhiteNoise wraps app only when `ENVIRONMENT=production`

### Step 9 — Delivery checks

- [ ] `docs/deployment.md` contains complete runbook with `az` commands, App Settings, init verification (row counts), startup command, health check config, update cycle, troubleshooting
- [ ] Smoke test checklist covers: health, auth, cash_in create, cash_out create, void, correct, company filter, SANDBOX absent, data persistence
- [ ] `.github/workflows/ci.yml` runs `pytest` and `ruff check .` (or deferral documented)
- [ ] CI workflow uses `ENVIRONMENT=test` and `SECRET_KEY` from env — no hardcoded secrets

### Step 10 — PostgreSQL verification

If a PostgreSQL connection is available:

- [ ] App boots against PostgreSQL (`DATABASE_URL=postgresql://...`)
- [ ] `pytest -v` passes against PostgreSQL (including `pg_*` fixtures)
- [ ] `/health` reports `{"database": "connected"}` against PostgreSQL
- [ ] `vat_deductible_pct` NULL on cash_out is rejected by the CHECK constraint

If PostgreSQL is not available: state this explicitly and confirm that the implementation is structurally correct from code inspection.

---

## Required output format

### 1. Verdict

```text
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

Full list with file references.

### 3. Problems Found

```text
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Architecture Violations

If none: `None.`

### 5. Acceptance Criteria Check

- [PASS|FAIL] `pytest -v` passes (SQLite)
- [PASS|FAIL] `ruff check .` passes
- [PASS|FAIL] T1–T5 cross-task integration is consistent (DATABASE_URL, ENVIRONMENT, _PgConnectionWrapper, EXEMPT_PATHS)
- [PASS|FAIL] `psycopg2-binary` in requirements; SQLite remains for dev/test
- [PASS|FAIL] `ENVIRONMENT` detection and `ALLOWED_HOSTS` enforcement correct
- [PASS|FAIL] session cookie `https_only` in production
- [PASS|FAIL] `.env.example` complete; no secrets committed
- [PASS|FAIL] `db/schema_pg.sql` does NOT exist; single `db/schema.sql` maintained
- [PASS|FAIL] `_prepare_schema_for_pg()` and `_apply_pg_post_schema()` handle PostgreSQL differences at init time
- [PASS|FAIL] `init_db.py` dual-engine with idempotent bootstrap; seed files use `ON CONFLICT DO NOTHING`
- [PASS|FAIL] `_PgConnectionWrapper` translates `?`→`%s`; service layer unchanged
- [PASS|FAIL] PostgreSQL test fixtures skip gracefully; pg tests cover tables/seeds/CHECK
- [PASS|FAIL] `GET /health` unauthenticated, real DB check, 200/503
- [PASS|FAIL] JSON logging in production, plain in development
- [PASS|FAIL] request logging covers method/path/status/latency
- [PASS|FAIL] WhiteNoise in production; StaticFiles mount in dev
- [PASS|FAIL] SANDBOX banner conditional on `ENVIRONMENT`
- [PASS|FAIL] `docs/deployment.md` complete runbook
- [PASS|FAIL] smoke test checklist covers all critical flows
- [PASS|FAIL] CI/CD pipeline (or documented deferral)
- [PASS|FAIL] no architecture principles violated (no hard deletes, no derived storage, no free-text categories, no LLM in logic)
- [PASS|FAIL] PostgreSQL readiness demonstrated or limitation clearly stated

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

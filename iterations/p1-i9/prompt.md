# cashflow-tracker Task Prompt — P1-I9: Azure / Server / Deployment

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/ → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point for transaction field rules |

---

## Planning Baseline

- **Iteration branch:** `feature/phase-1/iteration-9`
- **Base branch when I9 starts:** `main` after P1-I8 is merged
- **Current test baseline:** verify on `main` when I9 begins
- **Ruff:** clean
- **Prerequisite iteration:** P1-I8 — sub-categories must be complete before I9 starts
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I9 |
| Title | Azure / Server / Deployment |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 9 (final Phase 1 iteration) |
| Feature branch | `feature/phase-1/iteration-9` |
| Depends on | P1-I8 (sub-categories — all merged to main) |
| Blocks | Phase 2 (Basic Reporting) |
| PR scope | Task branches PR into `feature/phase-1/iteration-9`. The iteration branch PRs into `main` after QA. |

---

## Task Goal

Prepare the app for real deployment and operational use in Azure. After I9, the app runs in production with PostgreSQL, proper configuration, environment handling, and a repeatable deployment workflow. **This is the go-live iteration** — the SANDBOX banner is removed and production data starts.

**Critical:** No new features in this iteration. This is purely infrastructure, deployment, and the database switch from SQLite to PostgreSQL.

**Execution model:** 5 task branches, each with its own prompt file in `iterations/p1-i9/prompts/`. This file is the full reference; task prompt files are the execution guides.

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md          (I9 section)
```

### Task-specific

| Task | Also read |
|------|-----------|
| I9-T1 | `db/schema.sql`, `db/init_db.py`, `requirements.txt`, `app/main.py` |
| I9-T2 | `app/main.py`, `.env` (if exists) |
| I9-T3 | `db/schema.sql`, `db/init_db.py`, `seed/*.sql` |
| I9-T4 | `app/main.py`, `app/routes/*.py` |
| I9-T5 | `tests/test_transactions.py`, all test files |

---

## Database Transition

### Current state (SQLite sandbox)

- SQLite database at local path
- Schema in `db/schema.sql` — designed to be engine-agnostic
- `db/init_db.py` handles schema creation + seed data
- All data is non-production — can be discarded at go-live

### Target state (Azure PostgreSQL)

- Azure Database for PostgreSQL — Flexible Server
- Same schema — designed to work identically on both engines (per CLAUDE.md)
- Connection via connection string (environment variable)
- **PostgreSQL-specific addition:** Conditional CHECK constraint for `vat_deductible_pct NOT NULL on expenses` (per CLAUDE.md — deferred until go-live)

### Migration approach

1. Schema is identical between SQLite and PostgreSQL — only the connection method changes
2. Sandbox data **may be discarded** — users have been warned since day 1 via SANDBOX banner
3. Seed data (users, categories, companies) must be re-seeded in PostgreSQL
4. `init_db.py` must work with both SQLite (dev/test) and PostgreSQL (production)
5. Application code uses standard SQL — no SQLite-specific syntax

### Connection abstraction

```python
# Environment-driven database selection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cashflow.db")
# SQLite for local dev/test, PostgreSQL for production
```

The app must detect which engine is in use and handle connection differences:
- SQLite: file-based, `aiosqlite` or synchronous `sqlite3`
- PostgreSQL: `psycopg2` or `asyncpg`, connection pooling

---

## Azure Infrastructure

### Hosting options (decision in T1)

| Option | Pros | Cons |
|--------|------|------|
| **Azure App Service** | Simplest deployment, built-in SSL, easy scaling | Less control, potential cold start |
| **Azure Container Apps** | Docker-based, good for FastAPI, auto-scaling | Requires Dockerfile, more setup |
| **Azure VM** | Full control, familiar from WBSB | Manual maintenance, no auto-scaling |

**Recommendation:** Azure App Service (Linux) — simplest path for a 3-user internal tool. Owner has Azure deployment experience from WBSB.

### Required Azure resources

- Azure App Service (or chosen hosting) — Python 3.11+ runtime
- Azure Database for PostgreSQL — Flexible Server
- Azure Key Vault (or App Service Configuration) — secrets management
- Custom domain + SSL (optional for initial deployment)

### Environment variables

| Variable | Purpose | Where stored |
|----------|---------|--------------|
| `DATABASE_URL` | PostgreSQL connection string | App Settings / Key Vault |
| `SECRET_KEY` | Session encryption key | App Settings / Key Vault |
| `ENVIRONMENT` | `production` / `development` / `test` | App Settings |
| `DEFAULT_LOCALE` | `pl` (production default) | App Settings |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | App Settings |

---

## PostgreSQL-Specific Changes

### Conditional CHECK constraint (per CLAUDE.md)

Add at go-live only — not in SQLite sandbox:

```sql
-- PostgreSQL only — added at go-live
ALTER TABLE transactions
ADD CONSTRAINT chk_expense_vat_deductible
CHECK (
    direction != 'expense'
    OR vat_deductible_pct IS NOT NULL
);
```

### SQL compatibility notes

- `AUTOINCREMENT` (SQLite) → `SERIAL` or `GENERATED ALWAYS AS IDENTITY` (PostgreSQL)
- `INSERT OR IGNORE` (SQLite) → `INSERT ... ON CONFLICT DO NOTHING` (PostgreSQL)
- `BOOLEAN` works on both — SQLite stores as 0/1, PostgreSQL as true/false
- `TEXT` works on both
- `datetime('now')` (SQLite) → `NOW()` (PostgreSQL)
- Parameter placeholders: `?` (SQLite) → `%s` (psycopg2) or `$1` (asyncpg)

### init_db.py changes

- Detect database engine from `DATABASE_URL`
- Use engine-appropriate SQL syntax for schema creation
- Use engine-appropriate SQL syntax for seed data
- Ensure idempotent operation on both engines

---

## Health Check & Operational Endpoints

### Health check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

- Checks database connectivity
- Returns 200 if healthy, 503 if unhealthy
- Used by Azure for health monitoring and auto-restart

### Logging

- Structured logging (JSON format for production)
- Log levels: INFO for normal operations, WARNING for recoverable issues, ERROR for failures
- Request logging: method, path, status code, response time
- No sensitive data in logs (no passwords, session tokens, or personal data)

---

## SANDBOX Banner Removal

The SANDBOX banner in `base.html` has been visible since I1. At go-live:

1. Remove the SANDBOX banner from `base.html`
2. Optionally replace with a minimal "Production" indicator during initial rollout
3. The banner removal signals to users that data is now permanent

---

## Allowed Files

```
app/main.py                                    ← modify (database abstraction, health check, production config)
db/schema.sql                                  ← modify (PostgreSQL compatibility, conditional CHECK)
db/init_db.py                                  ← modify (dual-engine support, PostgreSQL connection)
requirements.txt                               ← modify (add psycopg2 / asyncpg)
app/templates/base.html                        ← modify (remove SANDBOX banner)
app/routes/*.py                                ← modify (if database connection changes affect routes)
Dockerfile                                     ← create (if containerized deployment)
.env.example                                   ← create (production env var template)
docs/deployment.md                             ← create (deployment runbook)
tests/conftest.py                              ← modify (dual-engine test support if needed)
tests/test_transactions.py                     ← modify (if PostgreSQL-specific tests needed)
iterations/p1-i9/tasks.md                      ← status updates only
```

---

## Deliverables by Task

### T1 — Azure Hosting + Database Setup

**Goal:** Azure hosting model decided, PostgreSQL provisioned, app can connect to both SQLite (dev) and PostgreSQL (production).

- Choose and document hosting model (App Service recommended)
- Provision Azure Database for PostgreSQL — Flexible Server
- Update `requirements.txt` with PostgreSQL driver
- Implement database connection abstraction in `app/main.py` (environment-driven)
- Verify app starts and connects to PostgreSQL
- Document Azure resource setup steps

### T2 — Production Config + Secrets

**Goal:** Production environment properly configured with secrets management.

- Define environment variable strategy
- Configure Azure App Settings or Key Vault for secrets
- Update `app/main.py` for production configuration (CORS, allowed hosts, session security)
- Create `.env.example` with all required variables documented
- Ensure `SECRET_KEY` is properly managed (not hardcoded)
- `ENVIRONMENT` variable controls debug mode, logging level, SANDBOX banner

### T3 — Schema Migration (SQLite → PostgreSQL)

**Goal:** Schema and seed data work on PostgreSQL. Existing tests pass against both engines.

- Update `db/init_db.py` for dual-engine support
- Handle SQL syntax differences (AUTOINCREMENT → SERIAL, INSERT OR IGNORE → ON CONFLICT, etc.)
- Add PostgreSQL conditional CHECK for `vat_deductible_pct` on expenses
- Re-seed users, categories, companies in PostgreSQL
- Verify all migrations (company_id backfill, parent_id, etc.) work on PostgreSQL
- Run full test suite against PostgreSQL

### T4 — Health Check + Logging + Static Files

**Goal:** Operational endpoints and production-ready observability.

- Implement `GET /health` endpoint with database connectivity check
- Add structured logging for production (JSON format)
- Configure request logging (method, path, status, response time)
- Set up static file serving for production (WhiteNoise or Azure CDN)
- Remove SANDBOX banner from `base.html`

### T5 — CI/CD + Deployment Docs + Smoke Test

**Goal:** Repeatable deployment process with documentation.

- Create deployment documentation (`docs/deployment.md`)
- Document: Azure setup, environment variables, database provisioning, first deployment, updates
- Create smoke-test checklist (login, create transaction, list, void, correct, company filter)
- Optionally set up CI/CD pipeline (GitHub Actions → Azure)
- Verify end-to-end: deploy → health check → smoke test passes

---

## What Must NOT Change

- Auth model — same 3-user session-based auth
- VAT calculation formulas — no modifications
- Soft-delete behavior — no changes
- Transaction data model — no schema changes beyond PostgreSQL compatibility
- All business logic — no changes to validation.py or calculations.py
- Route paths — no breaking changes to any URL
- i18n system — no changes
- Company/sub-category features from I7/I8 — no regression
- All existing tests must continue to pass (against both SQLite and PostgreSQL)

---

## Acceptance Checklist

```bash
# Against SQLite (dev)
pytest -v
# Expected: all tests pass

# Against PostgreSQL (production)
DATABASE_URL=postgresql://... pytest -v
# Expected: all tests pass

ruff check .
# Expected: clean
```

- [ ] Azure hosting provisioned and app deployed
- [ ] Azure PostgreSQL provisioned and connected
- [ ] App starts and serves pages from Azure
- [ ] Database connection works (PostgreSQL in production, SQLite in dev/test)
- [ ] `init_db.py` works on both SQLite and PostgreSQL
- [ ] PostgreSQL conditional CHECK for `vat_deductible_pct` on expenses is active
- [ ] Health check endpoint responds with 200
- [ ] All existing tests pass against PostgreSQL
- [ ] SANDBOX banner removed
- [ ] Environment variables properly configured (no hardcoded secrets)
- [ ] Deployment documentation complete
- [ ] Smoke test passes end-to-end in production
- [ ] ruff clean
- [ ] No new features — infrastructure only

---

## Agent Rules

1. Read this file first.
2. Read your task prompt file: `iterations/p1-i9/prompts/t[N]-[name].md`
3. Update status to IN PROGRESS before writing any code.
4. Check dependencies — never start if dep is not DONE.
5. Verify acceptance checklist before requesting review.
6. After PR is merged: update `tasks.md` status → DONE with one-line note.
7. No LLM calls in any logic layer.
8. Default locale is `pl` (Polish) — English is the fallback, not the default.
9. **No new features** — this iteration is purely infrastructure and deployment.
10. **Do not discard test compatibility** — tests must pass against both SQLite and PostgreSQL.
11. **Owner has Azure experience** from WBSB project — leverage existing knowledge, don't over-explain Azure basics.
12. **Sandbox data may be discarded** — do not build a data migration path for sandbox transactions.

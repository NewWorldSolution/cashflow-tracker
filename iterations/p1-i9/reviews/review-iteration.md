# QA Review — P1-I9: Azure / Server / Deployment
**Reviewer:** QA agent
**Branch:** `feature/phase-1/iteration-9`
**PR target:** `main`
**Trigger:** Run only after ALL tasks (T1–T5) show ✅ DONE in `iterations/p1-i9/tasks.md`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/phase-1-plan.md`, `CLAUDE.md`

---

## QA Agent Role

You are the QA agent for Phase 1 Iteration 9. Individual task reviews verify each task in isolation; this review verifies the whole iteration before merge to `main`.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

Use the reference docs above as the detailed source of truth. The task prompt files for I9 are still placeholders, so this QA review must anchor itself to the iteration brief and task board.

---

## What this iteration was supposed to deliver

1. Azure hosting model selected and implemented
2. Production configuration and secrets strategy moved to deployment settings
3. App can run against PostgreSQL in production while retaining SQLite for local dev/test
4. `db/init_db.py` and seed/bootstrap flow work for PostgreSQL
5. PostgreSQL-specific CHECK for non-null `vat_deductible_pct` on expenses is handled correctly
6. `GET /health` exists and reflects database connectivity
7. Logging and static-file serving are production-ready
8. Deployment is documented and repeatable
9. CI/CD pipeline validates the app and supports deployment flow
10. Smoke-test checklist exists for go-live verification
11. No secrets are committed
12. SANDBOX banner is removed for go-live

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

Expected:

- All tests pass
- Ruff is clean

### Step 3 — Scope verification

```bash
git diff --name-only main
```

Expected implementation files may include:

```text
app/main.py
app/routes/*.py
app/services/*.py
app/templates/base.html
db/schema.sql
db/init_db.py
seed/*.sql
requirements.txt
Dockerfile
.dockerignore
.github/workflows/*.yml
docs/deployment.md
docs/runbook.md
docs/smoke-test.md
```

Iteration planning files may also appear in the diff; this is expected:

```text
iterations/p1-i9/tasks.md
iterations/p1-i9/prompt.md
iterations/p1-i9/prompts/*.md
iterations/p1-i9/reviews/*.md
```

Unexpected broad feature work outside deployment/go-live scope is a failure.

### Step 4 — Architecture checks

Verify by code inspection:

- [ ] No hard deletes introduced
- [ ] No derived VAT/net/effective-cost values started being stored directly
- [ ] Validation remains centralized in the service layer
- [ ] `category_id` remains an integer FK, never free text
- [ ] `logged_by` and `voided_by` remain integer FKs
- [ ] PostgreSQL migration work does not fork business logic between engines

### Step 5 — Deployment/config checks

Verify by code inspection:

- [ ] Azure hosting path is clear and internally consistent
- [ ] Required env vars are defined and consumed consistently
- [ ] no production secrets are committed
- [ ] SQLite remains available for local dev/test
- [ ] PostgreSQL is the production path
- [ ] SANDBOX banner has been removed for go-live

### Step 6 — Database/bootstrap checks

Verify by code inspection and, if possible, execution:

- [ ] `db/init_db.py` supports both SQLite and PostgreSQL
- [ ] bootstrap/seed flow is idempotent
- [ ] PostgreSQL-specific CHECK for expense deductible pct is handled correctly
- [ ] no SQLite-only SQL remains in the PostgreSQL path
- [ ] schema remains logically consistent with pre-I9 business rules

### Step 7 — Ops/runtime checks

Verify by code inspection and manual run if needed:

- [ ] `GET /health` exists
- [ ] health endpoint checks DB connectivity
- [ ] unhealthy DB returns 503
- [ ] request logging captures method/path/status/latency
- [ ] static assets are served in deployed runtime

### Step 8 — Delivery checks

Verify by reading workflow/docs:

- [ ] CI runs tests and ruff
- [ ] deployment path is documented end to end
- [ ] rollback/recovery guidance exists
- [ ] smoke-test checklist covers key flows after deployment

### Step 9 — PostgreSQL verification

If PostgreSQL access is available for QA, verify:

- [ ] app boots against PostgreSQL
- [ ] existing tests pass against PostgreSQL
- [ ] health endpoint reports healthy against PostgreSQL

If PostgreSQL access is not available, state that explicitly and judge the code/docs readiness from the committed implementation.

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

- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean
- [PASS|FAIL] Azure hosting path is implemented clearly
- [PASS|FAIL] production config/secrets strategy is environment-driven
- [PASS|FAIL] SQLite remains usable for local dev/test
- [PASS|FAIL] PostgreSQL bootstrap path is implemented correctly
- [PASS|FAIL] PostgreSQL-specific expense deductible CHECK is handled correctly
- [PASS|FAIL] `GET /health` exists and reflects DB state
- [PASS|FAIL] logging and static-file serving are production-ready
- [PASS|FAIL] deployment docs are complete and repeatable
- [PASS|FAIL] CI/CD validates the app and supports deployment flow
- [PASS|FAIL] smoke-test checklist covers critical go-live checks
- [PASS|FAIL] no secrets are committed
- [PASS|FAIL] SANDBOX banner removed
- [PASS|FAIL] no architecture principles were violated
- [PASS|FAIL] PostgreSQL readiness is demonstrated or any environment limitation is clearly stated

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

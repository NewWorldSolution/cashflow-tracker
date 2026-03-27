# Review — I9-T5: CI/CD + Deployment Docs + Smoke Test
**Branch:** `feature/p1-i9/t5-deploy-pipeline`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompts/t5-deploy-pipeline.md`, `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- `docs/deployment.md` expanded from the T1 stub into a complete runbook: Azure resource provisioning (`az` commands), App Settings configuration, database initialisation verification, startup command, health check configuration, SSL/custom domain, update cycle, troubleshooting, and a smoke test checklist
- Smoke test checklist covers: health endpoint, login, opening balance, create cash_in, create cash_out, void, correct, company filter, SANDBOX banner absent, data persistence
- `.github/workflows/ci.yml` created — runs `pytest` and `ruff check .` on push/PR; optionally includes a PostgreSQL service job
- No real passwords or connection strings in any committed file
- No application code changes (no `app/`, `db/`, `seed/` modifications)

---

## Review Steps

1. **Diff scope** — confirm only these files appear:
   - `docs/deployment.md`
   - `.github/workflows/ci.yml` (or a note if explicitly deferred)
   - iteration planning files under `iterations/p1-i9/`
   Any `app/`, `db/`, `seed/`, or `tests/` changes are out of scope.

2. **`docs/deployment.md` — completeness**

   Verify each section is present and actionable:
   - Architecture paragraph (App Service + PostgreSQL Flexible Server, no Docker)
   - Prerequisites list
   - Section 1: resource group + PostgreSQL Flexible Server `az` commands
   - Section 2: App Service plan + web app `az` commands
   - Section 3: App Settings (`az webapp config appsettings set`) with all five required variables
   - Section 4: Database initialisation verification (psql commands + expected row counts: 81 categories, 4 companies, 3 users)
   - Section 5: Deployment command (`git push azure main` or equivalent)
   - Section 6: Startup command (`az webapp config set --startup-file`)
   - Section 7: Health check Azure configuration (`/health` path)
   - Section 8: Update cycle
   - Section 9: Troubleshooting (`az webapp log tail`, restart, log download)
   - Section 10 (or appendix): Smoke test checklist

3. **`docs/deployment.md` — correctness**
   - All `az` CLI commands use the resource names defined in T1 (`cashflow-rg`, `cashflow-pg`, `cashflow-app`)
   - PostgreSQL connection string example uses `?sslmode=require`
   - `SECRET_KEY` generation command shown (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
   - No real passwords or connection strings — placeholders only

4. **Smoke test checklist**
   - Covers all items from the task prompt:
     - `GET /health` returns 200
     - Login works
     - Opening balance setup (first deploy)
     - Create cash_in transaction (two-level category picker, all fields)
     - Create cash_out transaction (VAT derived correctly in detail view)
     - Void a transaction (reason required, excluded from totals)
     - Correct a transaction (original voided, new created, totals updated)
     - Company filter works on dashboard and list
     - SANDBOX banner is absent in production
     - Data persists across page refresh and logout/login

5. **`.github/workflows/ci.yml`**
   - Triggers on push to `main` and `feature/**`, and on pull_request to `main`
   - Steps: checkout → Python 3.11 setup → `pip install -r requirements.txt` → `pytest -v` → `ruff check .`
   - `SECRET_KEY` set as an env var for the test step
   - `ENVIRONMENT=test` set for the test step
   - No production secrets are hardcoded in the workflow
   - A test-only placeholder such as `SECRET_KEY: ci-test-secret-key` is acceptable
   - If PostgreSQL job is included: uses a `services: postgres:` block, not a real Azure connection

   If CI is explicitly deferred: check that the reason is documented clearly in the deployment runbook.

6. **No app code changes**
   - No modifications to `app/`, `db/`, `seed/`, `tests/`, or `requirements.txt`

7. **Run:**

```bash
pytest -v
ruff check .
```

Expected: no regressions (this task adds no app code).

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

Files modified outside `docs/deployment.md`, `.github/workflows/ci.yml`, and iteration planning files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] `docs/deployment.md` contains full Azure provisioning steps with `az` commands
- [PASS|FAIL] all five required App Settings documented with examples
- [PASS|FAIL] database initialisation verification steps present (expected row counts)
- [PASS|FAIL] startup command documented (`uvicorn app.main:app --host 0.0.0.0 --port 8000`)
- [PASS|FAIL] health check Azure configuration documented (`/health` path)
- [PASS|FAIL] update cycle documented
- [PASS|FAIL] troubleshooting commands present (`az webapp log tail`, restart)
- [PASS|FAIL] no real passwords or connection strings committed
- [PASS|FAIL] smoke test checklist covers health, auth, cash_in create, cash_out create, void, correct, company filter, SANDBOX absent, persistence
- [PASS|FAIL] `.github/workflows/ci.yml` created with pytest + ruff (or deferral explicitly documented)
- [PASS|FAIL] CI workflow uses `ENVIRONMENT=test` and a test-safe `SECRET_KEY` env var; no production secrets are hardcoded
- [PASS|FAIL] no app / db / seed / test / requirements changes
- [PASS|FAIL] `pytest -v` passes
- [PASS|FAIL] `ruff check .` passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

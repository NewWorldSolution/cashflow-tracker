# I9-T5 — CI/CD + Deployment Docs + Smoke Test

**Branch:** `feature/p1-i9/t5-deploy-pipeline`
**Base:** `feature/phase-1/iteration-9` (after T4 merged)
**Depends on:** I9-T4

---

## Goal

Produce a complete deployment runbook in `docs/deployment.md`, an optional GitHub Actions CI pipeline, and a smoke-test checklist. After this task, any operator (including the owner returning after a break) can provision a fresh Azure environment, deploy the app, and verify it works — by following the runbook alone.

This is a **documentation and pipeline task**. No application code changes.

---

## Read Before Starting

```text
CLAUDE.md
project.md
iterations/p1-i9/prompt.md
docs/deployment.md      ← stub created in T1 — expand it here
app/main.py             ← understand all env vars in use
.env.example            ← all variables documented in T2
requirements.txt        ← current dependencies
db/schema_pg.sql        ← PostgreSQL schema from T3
```

---

## Deliverables

### 1. Complete `docs/deployment.md`

Write the full deployment runbook. Target audience: the owner, who has Azure experience from WBSB. Do not over-explain Azure basics — focus on the steps and values specific to this app.

Structure:

---

```markdown
# cashflow-tracker — Deployment Runbook

## Architecture

[One paragraph: Azure App Service (Linux) + Azure Database for PostgreSQL Flexible Server.
No Docker, no containers — Python 3.11 runtime directly on App Service.]

## Prerequisites

- Azure subscription with contributor access
- Azure CLI installed and logged in (`az login`)
- Python 3.11+ locally
- Git access to this repository
- PostgreSQL client (`psql`) for initial seed verification

## 1. Azure Resource Provisioning

### 1.1 Resource Group
az group create --name cashflow-rg --location polandcentral

### 1.2 Azure Database for PostgreSQL — Flexible Server
az postgres flexible-server create \
  --resource-group cashflow-rg \
  --name cashflow-pg \
  --location polandcentral \
  --admin-user cfadmin \
  --admin-password <STRONG_PASSWORD> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 16

# Create the application database
az postgres flexible-server db create \
  --resource-group cashflow-rg \
  --server-name cashflow-pg \
  --database-name cashflow

# Allow App Service outbound IPs (add after App Service is created)
# az postgres flexible-server firewall-rule create ...

### 1.3 Azure App Service
az appservice plan create \
  --name cashflow-plan \
  --resource-group cashflow-rg \
  --sku B1 \
  --is-linux

az webapp create \
  --name cashflow-app \
  --resource-group cashflow-rg \
  --plan cashflow-plan \
  --runtime "PYTHON:3.11"

## 2. Application Settings (Secrets)

Set all required environment variables as App Service Application Settings.
Never commit these to the repository.

### Required settings

az webapp config appsettings set \
  --name cashflow-app \
  --resource-group cashflow-rg \
  --settings \
    SECRET_KEY="<generate: python -c \"import secrets; print(secrets.token_hex(32))\">" \
    DATABASE_URL="postgresql://cfadmin:<PASSWORD>@cashflow-pg.postgres.database.azure.com:5432/cashflow?sslmode=require" \
    ENVIRONMENT="production" \
    DEFAULT_LOCALE="pl" \
    ALLOWED_HOSTS="cashflow-app.azurewebsites.net" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true"

## 3. Database Initialisation

On first deployment, the app runs `initialise_db()` on startup via the lifespan hook.
This creates all tables and seeds users, categories, and companies.

To verify manually after first deploy:
psql "postgresql://cfadmin:<PASSWORD>@cashflow-pg.postgres.database.azure.com:5432/cashflow?sslmode=require" \
  -c "SELECT count(*) FROM categories;"
# Expected: 81 (19 parents + 62 subcategories)

psql ... -c "SELECT count(*) FROM users;"
# Expected: 3

psql ... -c "SELECT count(*) FROM companies;"
# Expected: 4

## 4. Deployment

### First deployment
git push azure main

# Or using Azure CLI:
az webapp deployment source config \
  --name cashflow-app \
  --resource-group cashflow-rg \
  --repo-url https://github.com/<owner>/cashflow-tracker \
  --branch main \
  --manual-integration

### Subsequent deployments
git push azure main
# App Service builds and restarts automatically (SCM_DO_BUILD_DURING_DEPLOYMENT=true)

## 5. Startup Command

Set the startup command in App Service:

az webapp config set \
  --name cashflow-app \
  --resource-group cashflow-rg \
  --startup-file "uvicorn app.main:app --host 0.0.0.0 --port 8000"

## 6. Health Check Configuration

Configure Azure App Service health check:
- Path: /health
- Expected status: 200

az webapp config set \
  --name cashflow-app \
  --resource-group cashflow-rg \
  --generic-configurations '{"healthCheckPath": "/health"}'

## 7. SSL / Custom Domain (optional)

Azure App Service provides HTTPS at *.azurewebsites.net out of the box.
For a custom domain, use the Azure portal or:

az webapp config hostname add \
  --webapp-name cashflow-app \
  --resource-group cashflow-rg \
  --hostname yourdomain.com

## 8. Updates and Redeployment

Standard update cycle:
1. Merge PR to main
2. git push azure main
3. Monitor: az webapp log tail --name cashflow-app --resource-group cashflow-rg
4. Verify: curl https://cashflow-app.azurewebsites.net/health

## 9. Troubleshooting

View live logs:
az webapp log tail --name cashflow-app --resource-group cashflow-rg

Download logs:
az webapp log download --name cashflow-app --resource-group cashflow-rg

Restart app:
az webapp restart --name cashflow-app --resource-group cashflow-rg

Check startup errors:
az webapp log show --name cashflow-app --resource-group cashflow-rg --log-type application
```

---

### 2. Smoke test checklist

Add a `## Smoke Test` section to `docs/deployment.md` at the end. This checklist must be run after every deployment (first deploy and updates).

```markdown
## Smoke Test Checklist

Run after every deployment. All items must pass before declaring the deployment successful.

### Pre-check
- [ ] `GET /health` returns 200 with `{"status": "healthy", "database": "connected"}`
- [ ] App loads at the Azure URL without errors

### Authentication
- [ ] Login page loads at `/auth/login`
- [ ] Login with `owner` / `owner123` succeeds and redirects to dashboard
- [ ] Dashboard displays opening balance (or redirects to opening balance setup on first deploy)
- [ ] Language switcher works (PL ↔ EN)
- [ ] Logout works

### Opening balance (first deploy only)
- [ ] Set opening balance via `/settings/opening-balance`
- [ ] Dashboard displays the opening balance after setting

### Transaction: create cash_in
- [ ] Navigate to `/transactions/new`
- [ ] Select direction: Wpływ (cash_in)
- [ ] Select parent category → subcategory (two-level picker works)
- [ ] Fill all required fields and submit
- [ ] Transaction appears in list at `/transactions/`

### Transaction: create cash_out
- [ ] Create a cash_out transaction with VAT rate
- [ ] Derived VAT amount and effective cost display correctly in detail view

### Transaction: void
- [ ] Open a transaction, click Anuluj (void)
- [ ] Provide void reason and confirm
- [ ] Transaction shows as voided in list (greyed out or marked)
- [ ] Voided transaction is excluded from dashboard totals

### Transaction: correct
- [ ] Open a transaction, click Koryguj (correct)
- [ ] Modify amount and submit
- [ ] Original transaction voided, new correction transaction created
- [ ] Dashboard totals reflect the correction

### Company filter
- [ ] Dashboard company filter (JDG / Sp. z o.o. / etc.) filters transactions correctly
- [ ] List view company filter works

### SANDBOX banner
- [ ] SANDBOX banner is NOT visible (production environment)

### Data persistence
- [ ] Refresh page — transactions created above are still present
- [ ] Log out and back in — data still present
```

### 3. GitHub Actions CI pipeline (optional but recommended)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, "feature/**"]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests (SQLite)
        env:
          SECRET_KEY: ci-test-secret-key
          ENVIRONMENT: test
        run: pytest -v

      - name: Ruff lint check
        run: ruff check .
```

PostgreSQL CI tests (optional — requires a PostgreSQL service in the CI job):

```yaml
  test-postgres:
    runs-on: ubuntu-latest
    needs: test

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: cftest
          POSTGRES_PASSWORD: cftest
          POSTGRES_DB: cashflow_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests (PostgreSQL)
        env:
          SECRET_KEY: ci-test-secret-key
          ENVIRONMENT: test
          DATABASE_URL: postgresql://cftest:cftest@localhost:5432/cashflow_test
        run: pytest -v
```

---

## Important Rules

- **No application code changes** — this task is docs and pipeline only
- **Do not commit real passwords or connection strings** — all examples use placeholders
- **The runbook must be self-sufficient** — the owner should be able to follow it cold without asking questions
- **Smoke test covers the full happy path** — not just the health endpoint
- **GitHub Actions is optional** — document it but do not block the iteration if CI setup is deferred

---

## Allowed Files

```text
docs/deployment.md               ← expand from stub
.github/workflows/ci.yml         ← create (optional)
iterations/p1-i9/tasks.md
```

---

## Acceptance Criteria

- [ ] `docs/deployment.md` contains full runbook (Azure provisioning through updates)
- [ ] All required `az` CLI commands present with correct resource names
- [ ] Startup command documented
- [ ] Health check Azure configuration documented
- [ ] Smoke test checklist covers: health, auth, create cash_in, create cash_out, void, correct, company filter, SANDBOX banner absent, data persistence
- [ ] No real passwords or secrets in documentation — placeholders only
- [ ] `.github/workflows/ci.yml` created (or explicitly noted as deferred with reason)
- [ ] `ruff check .` passes
- [ ] `pytest -v` passes (no application code changed — this is a sanity check)

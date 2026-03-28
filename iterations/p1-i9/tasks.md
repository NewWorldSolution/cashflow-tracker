# P1-I9 — Azure / Server / Deployment
## Task Board

**Status:** READY TO START
**Last updated:** 2026-03-27
**Iteration branch:** `feature/phase-1/iteration-9` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-9` → `main` ← QA agent approves before merge

---

## Goal

Prepare the app for real deployment and operational use in Azure. After I9, the app runs in production with proper configuration, environment handling, and a repeatable deployment workflow. This is the transition from SQLite sandbox to production.

---

## Planned Work

| # | Area | Description |
|---|------|-------------|
| 1 | Hosting | Decide Azure hosting model (App Service, Container Apps, VM, etc.) |
| 2 | Config | Set up deployment configuration for the chosen hosting option |
| 3 | Env vars | Define production environment variable strategy |
| 4 | Secrets | Move secrets/config to proper deployment settings (Key Vault or App Settings) |
| 5 | Database | Decide production database approach (Azure PostgreSQL) |
| 6 | Migration | Startup/init strategy for schema migration (SQLite → PostgreSQL) |
| 7 | Health | Add health-check / operational endpoint(s) |
| 8 | Static | Define static file serving setup for production |
| 9 | Logging | Add logging/error-handling setup for deployed environment |
| 10 | Docs | Deployment documentation / runbook |
| 11 | CI/CD | Optionally add CI/CD deployment pipeline |
| 12 | Smoke test | Smoke-test checklist for deployed app |

---

## Tasks

| ID    | Title                              | Owner | Status     | Depends on | Branch |
|-------|------------------------------------|-------|------------|------------|--------|
| I9-T1 | Azure hosting + database setup     | Codex | ✅ DONE | —          | `feature/p1-i9/t1-azure-setup` |
| I9-T2 | Production config + secrets        | Codex | ✅ DONE | I9-T1      | `feature/p1-i9/t2-prod-config` |
| I9-T3 | Schema migration (SQLite → PG)     | —     | ⏳ WAITING | I9-T1      | `feature/p1-i9/t3-pg-migration` |
| I9-T4 | Health check + logging + static    | Codex | ✅ DONE | I9-T2      | `feature/p1-i9/t4-ops` |
| I9-T5 | CI/CD + deployment docs + smoke    | —     | ⏳ WAITING | I9-T4      | `feature/p1-i9/t5-deploy-pipeline` |

---

## Important Notes

- **This is the go-live iteration** — after I9, SANDBOX banner is removed and production data starts
- **Database switch:** SQLite → Azure PostgreSQL. Schema is designed to be identical between both engines (per CLAUDE.md). Only the connection string changes.
- **PostgreSQL conditional CHECK** for `vat_deductible_pct NOT NULL on expenses` is added at go-live (per CLAUDE.md)
- **All existing sandbox data may be discarded** at this point — users have been warned since day 1 via the SANDBOX banner
- **Owner has Azure deployment experience** from WBSB project (I13)
- **No new features** — this iteration is purely infrastructure and deployment
- **Tests must pass against PostgreSQL** — verify that all existing tests work with the production database engine

---

## Prompts & Reviews

| Task  | Implementation prompt | Review prompt | Reviewer |
|-------|-----------------------|---------------|----------|
| I9-T1 | `iterations/p1-i9/prompts/t1-azure-setup.md` | `iterations/p1-i9/reviews/review-t1.md` | — |
| I9-T2 | `iterations/p1-i9/prompts/t2-prod-config.md` | `iterations/p1-i9/reviews/review-t2.md` | — |
| I9-T3 | `iterations/p1-i9/prompts/t3-pg-migration.md` | `iterations/p1-i9/reviews/review-t3.md` | — |
| I9-T4 | `iterations/p1-i9/prompts/t4-ops.md` | `iterations/p1-i9/reviews/review-t4.md` | — |
| I9-T5 | `iterations/p1-i9/prompts/t5-deploy-pipeline.md` | `iterations/p1-i9/reviews/review-t5.md` | — |
| —     | — | `iterations/p1-i9/reviews/review-iteration.md` | — (QA) |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-9` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

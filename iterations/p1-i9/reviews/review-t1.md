# Review — I9-T1: Azure Hosting + Database Setup
**Branch:** `feature/p1-i9/t1-azure-setup`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/phase-1-plan.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

This task prompt file is still a placeholder, so use the reference docs above as the source of truth for scope and intent.

---

## What was supposed to be built

- Azure hosting approach chosen and committed in code/config, with one clear deployment path only
- PostgreSQL production runtime dependency added
- Production startup/bootstrap path prepared for Azure hosting
- App entrypoint updated only as needed for deployment bootstrap
- No secrets committed to the repository
- No schema-migration implementation beyond setup/bootstrap decisions yet

---

## Review Steps

1. Confirm diff scope is limited to hosting/bootstrap files only. Expected files may include:
   - `requirements.txt`
   - `app/main.py`
   - `Dockerfile`
   - `.dockerignore`
   - Azure/startup bootstrap files such as `startup.sh`, `azure.yaml`, or similar deployment config
   - iteration planning files under `iterations/p1-i9/`
2. Verify exactly one hosting path is implemented clearly:
   - App Service startup configuration, or
   - Containerized deployment via `Dockerfile`
   Mixed or contradictory deployment strategies are a failure unless explicitly justified.
3. Verify PostgreSQL support is added through an appropriate runtime dependency (`psycopg2`, `psycopg`, or `asyncpg`) and that SQLite is not removed for local dev/test.
4. Verify the startup path is production-safe:
   - binds to Azure-provided host/port environment variables
   - does not require `--reload`
   - does not hardcode localhost-only assumptions
5. Verify no secrets, connection strings, or private keys are committed in tracked files.
6. Verify no application feature work is mixed into this task:
   - no transaction validation changes
   - no template/UI work
   - no CI/CD pipeline work
   - no health endpoint/logging/static implementation yet
7. Verify any new deployment file actually matches the chosen hosting strategy.
8. Run:

```bash
pytest -v
ruff check .
```

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

Files modified outside hosting/bootstrap/config scope for this task.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to hosting/bootstrap files
- [PASS|FAIL] one clear Azure hosting strategy is chosen
- [PASS|FAIL] deployment artifacts match the chosen strategy
- [PASS|FAIL] PostgreSQL runtime dependency added correctly
- [PASS|FAIL] SQLite remains available for local dev/test
- [PASS|FAIL] production startup path does not depend on dev-only reload/local assumptions
- [PASS|FAIL] no secrets committed
- [PASS|FAIL] no schema-migration implementation mixed into this task
- [PASS|FAIL] no health/logging/static work mixed into this task
- [PASS|FAIL] no CI/CD or runbook work mixed into this task
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

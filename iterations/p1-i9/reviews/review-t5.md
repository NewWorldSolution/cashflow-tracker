# Review — I9-T5: CI/CD + Deployment Docs + Smoke Test
**Branch:** `feature/p1-i9/t5-deploy-pipeline`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/phase-1-plan.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

This task prompt file is still a placeholder, so use the reference docs above as the source of truth for scope and intent.

---

## What was supposed to be built

- CI/CD workflow for repeatable validation/deployment
- deployment runbook documenting Azure deployment and rollback
- smoke-test checklist for deployed app
- test/lint execution integrated into the pipeline
- deployment flow avoids committed secrets and documents required environment settings

---

## Review Steps

1. Confirm diff scope is limited to delivery/docs/pipeline files only. Expected files may include:
   - `.github/workflows/*.yml`
   - `docs/deployment.md`
   - `docs/runbook.md`
   - `docs/smoke-test.md`
   - supporting scripts used only by deployment/pipeline
   - iteration planning files under `iterations/p1-i9/`
2. Verify the CI workflow runs the project quality gates at minimum:
   - dependency install
   - `pytest`
   - `ruff check .`
3. Verify deployment, if included, is gated on successful validation and does not bypass failing tests/lint.
4. Verify secrets are referenced through CI/Azure secret stores and are not committed in workflow files or docs.
5. Verify the deployment docs explain:
   - required environment variables
   - database/bootstrap steps
   - deployment command/path
   - rollback or recovery path
6. Verify the smoke-test checklist covers at minimum:
   - app reachable
   - login works
   - create transaction
   - correction/edit flow
   - void/soft-delete flow
   - health endpoint
   - static assets load
7. Verify this task does not make unrelated changes to app logic, schema, or runtime behavior unless strictly required for the pipeline.
8. Run:

```bash
pytest -v
ruff check .
```

If the workflow can be validated locally, report the key job steps and whether they match the docs.

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

Files modified outside pipeline/docs/smoke-test scope for this task.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to pipeline/docs/smoke-test files
- [PASS|FAIL] CI runs pytest
- [PASS|FAIL] CI runs ruff
- [PASS|FAIL] deployment is gated on successful validation
- [PASS|FAIL] no secrets committed in workflow or docs
- [PASS|FAIL] deployment docs cover env vars and bootstrap steps
- [PASS|FAIL] deployment docs cover rollback/recovery
- [PASS|FAIL] smoke-test checklist covers critical user and ops flows
- [PASS|FAIL] no unrelated app/schema/runtime work mixed into this task
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

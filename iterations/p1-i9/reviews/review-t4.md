# Review — I9-T4: Health Check + Logging + Static Files
**Branch:** `feature/p1-i9/t4-ops`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/phase-1-plan.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

This task prompt file is still a placeholder, so use the reference docs above as the source of truth for scope and intent.

---

## What was supposed to be built

- `GET /health` endpoint for operational monitoring
- health response reports app/database status
- unhealthy database state returns 503
- production-appropriate logging added
- request logging covers method, path, status, and response time
- static file serving is prepared for deployed use

---

## Review Steps

1. Confirm diff scope is limited to ops/runtime files only. Expected files may include:
   - `app/main.py`
   - `app/routes/*.py`
   - new logging/helpers under `app/`
   - tests for health/runtime behavior
   - iteration planning files under `iterations/p1-i9/`
2. Verify `GET /health` exists and is unauthenticated unless the branch explicitly justifies a different operational model.
3. Verify the endpoint checks database connectivity rather than returning a hardcoded healthy response.
4. Verify response behavior:
   - HTTP 200 when healthy
   - HTTP 503 when unhealthy
   - structured payload including at least app status and database status
5. Verify logging is production-oriented:
   - INFO/WARNING/ERROR levels used appropriately
   - request logging includes method, path, status code, and latency
   - no secret values or credentials are logged
6. Verify static files are served in a way compatible with deployed runtime and do not depend on debug/dev-only behavior.
7. Verify this task does not mix in:
   - schema migration work
   - production secret/config work
   - CI/CD pipeline changes
   - unrelated transaction feature work
8. Run:

```bash
pytest -v
ruff check .
```

If practical in the branch, hit `/health` in both a healthy and simulated-unhealthy state and report the observed status codes.

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

Files modified outside ops/runtime scope for this task.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to ops/runtime files
- [PASS|FAIL] `GET /health` exists
- [PASS|FAIL] health endpoint checks database connectivity
- [PASS|FAIL] health endpoint returns 200 when healthy
- [PASS|FAIL] health endpoint returns 503 when unhealthy
- [PASS|FAIL] health response includes app/database status
- [PASS|FAIL] request logging includes method, path, status, and latency
- [PASS|FAIL] logging avoids secrets/credentials
- [PASS|FAIL] static file serving is production-compatible
- [PASS|FAIL] no migration/config/pipeline/feature work mixed into this task
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

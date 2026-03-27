# Review — I9-T2: Production Config + Secrets
**Branch:** `feature/p1-i9/t2-prod-config`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/phase-1-plan.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

This task prompt file is still a placeholder, so use the reference docs above as the source of truth for scope and intent.

---

## What was supposed to be built

- Production configuration driven by environment variables
- Secret handling moved out of code and into deployment settings
- Local development defaults preserved where explicitly allowed
- Required production config keys defined and consumed consistently:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `ENVIRONMENT`
  - `DEFAULT_LOCALE`
  - `ALLOWED_HOSTS`
- No secrets committed into tracked files

---

## Review Steps

1. Confirm diff scope is limited to configuration files only. Expected files may include:
   - `app/main.py`
   - a new config/settings module under `app/`
   - `.env.example`, `.env.production.example`, or similar sample env file
   - iteration planning files under `iterations/p1-i9/`
2. Verify production configuration is environment-driven and does not hardcode secrets, hostnames, or connection strings.
3. Verify `DATABASE_URL` is the source of truth for database selection and that local SQLite fallback remains available for non-production use.
4. Verify `SECRET_KEY` is required in production and not silently defaulted to an unsafe constant.
5. Verify `ENVIRONMENT` drives production/development/test behavior explicitly rather than relying on ad hoc flags.
6. Verify `DEFAULT_LOCALE` is configurable and production default remains aligned with the brief (`pl`).
7. Verify `ALLOWED_HOSTS` is parsed from configuration and used consistently for host validation if implemented in this task.
8. Verify missing required production settings fail fast with an explicit error rather than silently degrading to insecure defaults.
9. Verify no secrets are checked into:
   - `.env`
   - sample files with real values
   - code constants
   - deployment docs committed in this branch
10. Verify this task does not contain:
   - database schema migration logic
   - health/logging/static implementation
   - CI/CD pipeline work
   - unrelated route/template changes
11. Run:

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

Files modified outside configuration/secret-handling scope for this task.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to config/secret-handling files
- [PASS|FAIL] configuration is environment-driven
- [PASS|FAIL] `DATABASE_URL` is the database source of truth
- [PASS|FAIL] SQLite fallback remains for local dev/test
- [PASS|FAIL] `SECRET_KEY` is required in production
- [PASS|FAIL] `ENVIRONMENT` is handled explicitly
- [PASS|FAIL] `DEFAULT_LOCALE` is configurable and production-safe
- [PASS|FAIL] `ALLOWED_HOSTS` is configurable and parsed correctly
- [PASS|FAIL] missing production settings fail fast
- [PASS|FAIL] no secrets committed
- [PASS|FAIL] no migration/ops/pipeline work mixed into this task
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

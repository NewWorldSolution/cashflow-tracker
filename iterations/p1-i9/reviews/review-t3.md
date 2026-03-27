# Review — I9-T3: Schema Migration (SQLite → PostgreSQL)
**Branch:** `feature/p1-i9/t3-pg-migration`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `iterations/phase-1-plan.md`, `CLAUDE.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

This task prompt file is still a placeholder, so use the reference docs above as the source of truth for scope and intent.

---

## What was supposed to be built

- `db/init_db.py` works with both SQLite and PostgreSQL
- Seed data can be recreated cleanly in PostgreSQL
- Schema remains logically identical across both engines
- PostgreSQL-specific handling is added only where required
- Sandbox data migration is optional; schema/bootstrap migration is mandatory
- PostgreSQL-only CHECK for `vat_deductible_pct NOT NULL on expenses` is applied at go-live without breaking SQLite

---

## Review Steps

1. Confirm diff scope is limited to database/bootstrap files only. Expected files may include:
   - `db/schema.sql`
   - `db/init_db.py`
   - `seed/users.sql`
   - `seed/categories.sql`
   - `seed/companies.sql`
   - database-focused tests such as `tests/test_init_db.py`
   - iteration planning files under `iterations/p1-i9/`
2. Verify `db/init_db.py` detects engine/driver from `DATABASE_URL` and chooses SQLite vs PostgreSQL behavior explicitly.
3. Verify SQLite support still works for local dev/test and has not been broken by PostgreSQL changes.
4. Verify PostgreSQL bootstrap is idempotent:
   - schema creation can be rerun safely
   - seed inserts are rerunnable without duplicate rows
5. Verify SQLite-only SQL syntax is not used in the PostgreSQL path:
   - `INSERT OR IGNORE`
   - SQLite placeholder style only
   - `datetime('now')` assumptions
6. Verify PostgreSQL-only behavior is isolated cleanly and does not leak into the SQLite path.
7. Verify the additional PostgreSQL CHECK for non-null `vat_deductible_pct` on expenses exists only for PostgreSQL/go-live handling and does not break SQLite bootstrap.
8. Verify no derived values begin to be stored in schema as part of the migration.
9. Verify no free-text category storage, hard deletes, or validation logic migration into routes/templates is introduced.
10. Verify this task does not mix in:
   - Azure hosting bootstrap work
   - production secret/config handling
   - health/logging/static work
   - CI/CD pipeline or deployment docs
11. Run:

```bash
pytest -v
ruff check .
```

If available in the branch, also run the database bootstrap against both engines and report whether each succeeds.

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

Files modified outside database/bootstrap scope for this task.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to database/bootstrap files
- [PASS|FAIL] `init_db.py` supports both SQLite and PostgreSQL
- [PASS|FAIL] database engine selection is driven by `DATABASE_URL`
- [PASS|FAIL] SQLite local-dev path still works
- [PASS|FAIL] PostgreSQL bootstrap is idempotent
- [PASS|FAIL] seed data can be recreated cleanly in PostgreSQL
- [PASS|FAIL] SQLite-specific SQL is not used in the PostgreSQL path
- [PASS|FAIL] PostgreSQL-only CHECK for expense deductible pct is handled correctly
- [PASS|FAIL] schema remains logically equivalent across both engines
- [PASS|FAIL] no derived values are newly stored
- [PASS|FAIL] no hosting/config/ops/pipeline work mixed into this task
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# Review — I7-T1: Companies Schema + Seed + Migration
**Branch:** `feature/p1-i7/t1-companies-schema`
**PR target:** `feature/phase-1/iteration-7`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: `db/schema.sql` — add `companies` table plus `transactions.company_id` and `transactions.for_accountant`
- Modified: `db/init_db.py` — idempotent migration, seed companies, backfill existing transactions
- New file: `seed/companies.sql` — initial 4 companies with language-neutral keys

---

## Review steps

1. Confirm diff scope is limited to `db/schema.sql`, `db/init_db.py`, and `seed/companies.sql`.
2. Verify `db/schema.sql` defines `companies` with:
   - `id INTEGER PRIMARY KEY AUTOINCREMENT`
   - `name TEXT NOT NULL UNIQUE`
   - `slug TEXT NOT NULL UNIQUE`
   - `is_active BOOLEAN NOT NULL DEFAULT TRUE`
3. Verify `seed/companies.sql` inserts exactly these companies:
   - `sp`
   - `ltd`
   - `ff`
   - `private`
4. Verify `transactions` in `db/schema.sql` includes:
   - `company_id INTEGER NOT NULL REFERENCES companies(id)`
   - `for_accountant BOOLEAN NOT NULL DEFAULT FALSE`
5. Verify `db/init_db.py` seeds companies idempotently for existing databases.
6. Verify `db/init_db.py` adds `company_id` and `for_accountant` for existing databases in an idempotent way.
7. Verify existing transactions are backfilled to the default company `id = 1` (`sp`).
8. Verify migration logic does not delete or rewrite transaction history beyond the required backfill/defaulting.
9. Verify no business logic, routes, templates, i18n, or tests were modified in this task branch.
10. Run:

```bash
pytest -v
ruff check .
```

---

## Required output format

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

Files modified outside `db/schema.sql`, `db/init_db.py`, and `seed/companies.sql`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `companies` table exists with required columns and constraints
- [PASS|FAIL] `seed/companies.sql` contains `sp`, `ltd`, `ff`, `private`
- [PASS|FAIL] `transactions.company_id` exists as NOT NULL FK
- [PASS|FAIL] `transactions.for_accountant` exists as NOT NULL boolean default FALSE
- [PASS|FAIL] migration is idempotent for existing databases
- [PASS|FAIL] companies are seeded during init/migration
- [PASS|FAIL] existing transactions are backfilled to company `id = 1` (`sp`)
- [PASS|FAIL] no transaction history is deleted or hard-reset
- [PASS|FAIL] no routes/templates/i18n/services/tests changed outside task scope
- [PASS|FAIL] pytest passes
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

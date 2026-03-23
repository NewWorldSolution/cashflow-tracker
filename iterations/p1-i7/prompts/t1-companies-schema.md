# I7-T1 — Companies Schema + Seed + Migration

**Branch:** `feature/p1-i7/t1-companies-schema` (from `feature/phase-1/iteration-7`)
**Worktree:** `../cashflow-tracker-t1`
**PR target:** `feature/phase-1/iteration-7`
**Depends on:** —

---

## Goal

Create the `companies` table, seed 4 language-neutral companies, add `company_id` and `for_accountant` to transactions, and backfill existing transactions to the default company (`sp`, id `1`).

After T1:

- schema supports multi-company
- `for_accountant` exists in the schema
- existing data is migrated safely
- no UI changes exist yet

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i7/tasks.md
iterations/p1-i7/prompt.md
db/schema.sql
db/init_db.py
seed/categories.sql
seed/users.sql
```

---

## Allowed Files

```text
db/schema.sql
db/init_db.py
seed/companies.sql
```

Do NOT modify routes, templates, i18n, JS, CSS, tests, or services in this task.

---

## What to Implement

### 1. `db/schema.sql`

Add:

- `companies` table with `id`, `name`, `slug`, `is_active`
- `company_id INTEGER NOT NULL REFERENCES companies(id)` on `transactions`
- `for_accountant BOOLEAN NOT NULL DEFAULT FALSE` on `transactions`

The schema should reflect the final desired shape, not the migration compromise.

### 2. `seed/companies.sql`

Seed exactly 4 companies:

```sql
INSERT OR IGNORE INTO companies (id, name, slug)
VALUES
    (1, 'sp', 'sp'),
    (2, 'ltd', 'ltd'),
    (3, 'ff', 'ff'),
    (4, 'private', 'private');
```

These are language-neutral keys. They are not user-facing labels.

### 3. `db/init_db.py`

Add idempotent migration logic that:

- creates/seeds companies for existing DBs
- adds `company_id` for legacy DBs if missing
- adds `for_accountant` for legacy DBs if missing
- backfills existing transactions to `company_id = 1`

Requirements:

- seed companies before backfill
- migration must be safe to run multiple times
- do not delete or rewrite transaction history beyond backfill/defaults

---

## Acceptance Check

```bash
ruff check .
pytest -v
```

- [ ] `companies` table exists in `schema.sql`
- [ ] `transactions.company_id` exists in `schema.sql`
- [ ] `transactions.for_accountant` exists in `schema.sql`
- [ ] `seed/companies.sql` contains `sp`, `ltd`, `ff`, `private`
- [ ] `init_db.py` seeds companies idempotently
- [ ] `init_db.py` migrates `company_id` idempotently
- [ ] `init_db.py` migrates `for_accountant` idempotently
- [ ] existing transactions are backfilled to `company_id = 1`
- [ ] no routes/templates/i18n/services/tests changed
- [ ] pytest passes
- [ ] ruff clean

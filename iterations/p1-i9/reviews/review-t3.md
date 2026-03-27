# Review — I9-T3: Schema Migration (SQLite → PostgreSQL)
**Branch:** `feature/p1-i9/t3-pg-migration`
**PR target:** `feature/phase-1/iteration-9`
**Reference docs:** `iterations/p1-i9/prompts/t3-pg-migration.md`, `iterations/p1-i9/prompt.md`, `iterations/p1-i9/tasks.md`, `CLAUDE.md`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- **Single schema file** — no `db/schema_pg.sql`. `db/schema.sql` is the sole source. `_prepare_schema_for_pg()` substitutes `AUTOINCREMENT` → `SERIAL` at apply time for PostgreSQL. The go-live `chk_expense_vat_deductible` CHECK constraint is applied separately via `_apply_pg_post_schema()` (idempotent — handles `DuplicateObject` error).
- **`db/init_db.py` refactored** for dual-engine: `_is_postgres(conn)` recognising both raw psycopg2 and `_PgConnectionWrapper`; engine-aware `_table_exists()` (`information_schema` vs `sqlite_master`); engine-aware `_column_exists()` (`information_schema` vs `PRAGMA`); `_apply_schema()` calling `_split_schema_statements()` (splits on `;\n`, not bare `;`) for PostgreSQL.
- **Seed files rewritten** — `seed/categories.sql` and `seed/companies.sql` now use `INSERT INTO ... ON CONFLICT DO NOTHING` (no `INSERT OR IGNORE`). No runtime string rewriting needed.
- **`_PgConnectionWrapper`** added in `app/main.py` — wraps psycopg2, translates `?` → `%s` in `execute()`, uses `RealDictCursor` for dict-like row access; `_connect()` returns the wrapper for PostgreSQL URLs; `_is_postgres()` updated to recognise the wrapper.
- Service layer SQL (`?` placeholders) is NOT modified — the wrapper handles compatibility transparently.
- `pg_db` test fixture skips gracefully when no PostgreSQL URL is set; PostgreSQL-specific tests cover tables, seed counts, and the CHECK constraint.
- `pytest -v` passes against SQLite; `DATABASE_URL=postgresql://... pytest -v` passes against PostgreSQL.

---

## Review Steps

1. **Diff scope** — confirm only these files appear:
   - `db/schema.sql` (no structural changes — `AUTOINCREMENT` stays; only adaptation in code)
   - `db/init_db.py`
   - `seed/categories.sql`
   - `seed/companies.sql`
   - `app/main.py`
   - `tests/conftest.py` and/or `tests/test_init_db.py`
   - iteration planning files under `iterations/p1-i9/`
   **`db/schema_pg.sql` must NOT exist** — flag as scope violation if present.

2. **`db/schema.sql`**
   - `AUTOINCREMENT` still present (SQLite syntax) — adaptation happens in code, not the file
   - No `SERIAL`, no `ALTER TABLE ADD CONSTRAINT CHECK` added to this file

3. **`db/init_db.py` — `_prepare_schema_for_pg()`**
   - Replaces `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY` only
   - Does NOT do general string replacement that could corrupt other parts of the schema

4. **`db/init_db.py` — `_apply_pg_post_schema()`**
   - Adds `chk_expense_vat_deductible` CHECK constraint
   - Idempotent: catches `psycopg2.errors.DuplicateObject` and rolls back instead of crashing

5. **`db/init_db.py` — `_split_schema_statements()`**
   - Splits on `;\n` (semicolon + newline), NOT on bare `;`
   - The bare `;` split is unsafe — `;\n` is safe for our DDL-only schema

6. **`db/init_db.py` — engine detection**
   - `_is_postgres(conn)` handles both raw psycopg2 connections and `_PgConnectionWrapper` instances
   - `_table_exists()` uses `information_schema.tables` for PostgreSQL, `sqlite_master` for SQLite
   - `_column_exists()` uses `information_schema.columns` for PostgreSQL, `PRAGMA table_info()` for SQLite

7. **Seed files**
   - `seed/categories.sql`: no `INSERT OR IGNORE` — uses `INSERT INTO ... ON CONFLICT DO NOTHING`
   - `seed/companies.sql`: same
   - The inline user INSERT in `init_db.py`: uses `ON CONFLICT DO NOTHING` with `?` placeholders

8. **`_PgConnectionWrapper` in `app/main.py`**
   - `execute(sql, params)` replaces `?` with `%s` before calling psycopg2
   - Uses `RealDictCursor` so `.fetchone()` / `.fetchall()` return dict-like results
   - `commit()` and `close()` proxy to the underlying connection
   - `_connect()` returns `_PgConnectionWrapper(conn)` for PostgreSQL URLs
   - `_is_postgres()` in `main.py` recognises `_PgConnectionWrapper` instances

9. **Service layer unchanged**
   - No `app/services/*.py` file uses `%s` placeholders — all still use `?`
   - No `app/services/*.py` imports psycopg2

10. **PostgreSQL fixtures and tests**
    - `pg_db` fixture calls `pytest.skip()` when `DATABASE_URL` is not a PostgreSQL URL
    - Tests cover: all 6 tables exist, 19 parent + 62 subcategory categories seeded, 4 companies, 3 users, and `vat_deductible_pct = NULL` on cash_out row rejected by CHECK constraint

11. **Run:**

```bash
# SQLite (must always pass)
pytest -v

# PostgreSQL (pass if DATABASE_URL is set, skip gracefully if not)
DATABASE_URL=postgresql://... pytest -v
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

Files modified outside `db/schema.sql`, `db/init_db.py`, seed files, `app/main.py`, test files, and iteration planning files. Flag `db/schema_pg.sql` if it exists.

### 5. Acceptance Criteria Check

- [PASS|FAIL] no `db/schema_pg.sql` — single schema file maintained
- [PASS|FAIL] `_prepare_schema_for_pg()` substitutes only `AUTOINCREMENT` → `SERIAL` (bounded, safe)
- [PASS|FAIL] `chk_expense_vat_deductible` CHECK applied via `_apply_pg_post_schema()`, idempotent
- [PASS|FAIL] `_split_schema_statements()` splits on `;\n` not bare `;`
- [PASS|FAIL] `_is_postgres(conn)` recognises both raw psycopg2 and `_PgConnectionWrapper`
- [PASS|FAIL] `_table_exists()` and `_column_exists()` use engine-appropriate introspection
- [PASS|FAIL] seed files use `ON CONFLICT DO NOTHING` — no `INSERT OR IGNORE` remains
- [PASS|FAIL] inline user INSERT in `init_db.py` uses `ON CONFLICT DO NOTHING` with `?`
- [PASS|FAIL] `_PgConnectionWrapper` translates `?` → `%s` and uses `RealDictCursor`
- [PASS|FAIL] `_connect()` returns wrapper for PostgreSQL URLs
- [PASS|FAIL] service layer SQL unchanged (still uses `?`, no psycopg2 imports)
- [PASS|FAIL] `pg_db` fixture skips gracefully when PostgreSQL URL not available
- [PASS|FAIL] PostgreSQL tests cover tables, seed counts (19+62, 4, 3), and CHECK constraint
- [PASS|FAIL] no derived values newly stored
- [PASS|FAIL] no hosting/config/ops/CI work mixed in
- [PASS|FAIL] `pytest -v` passes (SQLite)
- [PASS|FAIL] `ruff check .` passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

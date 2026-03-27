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

- `db/schema_pg.sql` created — PostgreSQL version of the schema with `SERIAL PRIMARY KEY` (not `AUTOINCREMENT`) and the go-live conditional CHECK constraint on `vat_deductible_pct`
- `db/init_db.py` refactored for dual-engine: `_is_postgres(conn)` helper, engine-aware `_table_exists()`, engine-aware `_column_exists()`, engine-aware `_apply_schema()`, `_split_sql()` for psycopg2 (no `executescript`), `_adapt_seed()` converting `INSERT OR IGNORE` → `INSERT ... ON CONFLICT DO NOTHING` at runtime
- `_PgConnectionWrapper` class added in `app/main.py` — wraps a psycopg2 connection and translates `?` → `%s` in `execute()`, allowing service layer to remain unchanged
- `_connect()` in `app/main.py` returns `_PgConnectionWrapper` for PostgreSQL connections; `_is_postgres()` updated to recognise the wrapper
- `tests/conftest.py` (or `tests/test_init_db.py`) gains a `pg_db` fixture that skips if no PostgreSQL `DATABASE_URL`
- PostgreSQL-specific tests added: tables created, 19+62 categories seeded, 4 companies, 3 users, `vat_deductible_pct` CHECK constraint active
- `pytest -v` passes against SQLite; `DATABASE_URL=postgresql://... pytest -v` passes against PostgreSQL
- Service layer SQL (`?` placeholders, `INSERT OR IGNORE`, etc.) is NOT modified — the wrapper handles it

---

## Review Steps

1. **Diff scope** — confirm only these files appear:
   - `db/schema_pg.sql` (new)
   - `db/init_db.py`
   - `app/main.py`
   - `tests/conftest.py` and/or `tests/test_init_db.py`
   - iteration planning files under `iterations/p1-i9/`
   Modifications to `app/services/*.py`, `app/routes/*.py`, or seed files (beyond runtime adaptation) need justification.

2. **`db/schema_pg.sql`**
   - Uses `SERIAL PRIMARY KEY` (not `AUTOINCREMENT`)
   - Contains `ALTER TABLE transactions ADD CONSTRAINT chk_expense_vat_deductible CHECK (direction != 'cash_out' OR vat_deductible_pct IS NOT NULL)`
   - Does NOT contain `INSERT OR IGNORE` or SQLite-specific syntax
   - Does NOT store derived values (vat_amount, net_amount, etc.)

3. **`db/schema.sql` (SQLite)**
   - Must remain unchanged — no `SERIAL`, no `ALTER TABLE ADD CONSTRAINT CHECK` (SQLite rejects this syntax)

4. **`db/init_db.py` engine detection**
   - `_is_postgres(conn)` checks `type(conn).__module__.startswith("psycopg2")` or equivalent
   - `_table_exists()` uses `information_schema.tables` for PostgreSQL, `sqlite_master` for SQLite
   - `_column_exists()` uses `information_schema.columns` for PostgreSQL, `PRAGMA table_info()` for SQLite

5. **`db/init_db.py` schema application**
   - PostgreSQL: reads `db/schema_pg.sql`, splits on `;`, executes statements one by one (psycopg2 has no `executescript`)
   - SQLite: reads `db/schema.sql`, uses `conn.executescript()` unchanged

6. **`db/init_db.py` seed adaptation**
   - `_adapt_seed()` replaces `INSERT OR IGNORE INTO` with `INSERT INTO` and appends `ON CONFLICT DO NOTHING` for PostgreSQL
   - Applied to categories, companies, and user inserts
   - Seed `.sql` files themselves are NOT modified — adaptation happens at runtime only

7. **`_PgConnectionWrapper` in `app/main.py`**
   - `execute(sql, params)` replaces `?` with `%s` before calling psycopg2
   - Uses `RealDictCursor` so `.fetchone()` / `.fetchall()` return dict-like results
   - `commit()` and `close()` proxy to the underlying connection
   - `executescript()` fallback splits on `;` and runs each statement (for init_db compatibility)
   - `_connect()` returns `_PgConnectionWrapper(conn)` for PostgreSQL URLs

8. **Service layer unchanged**
   - No `app/services/*.py` file uses `%s` placeholders — all still use `?`
   - No `app/services/*.py` file imports psycopg2

9. **PostgreSQL fixtures and tests**
   - `pg_db` fixture calls `pytest.skip()` when `DATABASE_URL` is not a PostgreSQL URL
   - Tests cover: tables created, category count (19 parents + 62 subcategories), company count (4), user count (3), and `vat_deductible_pct` CHECK constraint rejected on cash_out with NULL

10. **Run:**

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

Files modified outside `db/schema_pg.sql`, `db/init_db.py`, `app/main.py`, test files, and iteration planning files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] `db/schema_pg.sql` created with `SERIAL PRIMARY KEY`
- [PASS|FAIL] `chk_expense_vat_deductible` CHECK constraint present in `schema_pg.sql`
- [PASS|FAIL] `db/schema.sql` (SQLite) is unchanged
- [PASS|FAIL] `init_db.py` `_table_exists()` uses engine-appropriate introspection
- [PASS|FAIL] `init_db.py` `_column_exists()` uses engine-appropriate introspection
- [PASS|FAIL] `init_db.py` applies `schema_pg.sql` for PostgreSQL, `schema.sql` for SQLite
- [PASS|FAIL] `INSERT OR IGNORE` adapted to `ON CONFLICT DO NOTHING` at runtime for PostgreSQL
- [PASS|FAIL] seed files themselves not modified
- [PASS|FAIL] `_PgConnectionWrapper` translates `?` → `%s` transparently
- [PASS|FAIL] service layer SQL unchanged (still uses `?`)
- [PASS|FAIL] `pg_db` fixture skips gracefully when PostgreSQL URL not available
- [PASS|FAIL] PostgreSQL tests cover tables, seed counts, and CHECK constraint
- [PASS|FAIL] no derived values newly stored
- [PASS|FAIL] no hosting/config/ops/CI work mixed in
- [PASS|FAIL] `pytest -v` passes (SQLite)
- [PASS|FAIL] `ruff check .` passes

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

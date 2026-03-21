# Review — I1-T1: Schema + Seed Data
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i1/t1-schema`
**PR target:** `feature/phase-1/iteration-1`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Your job is to verify it exactly matches the spec. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
db/__init__.py           ← empty
db/schema.sql            ← 5 tables with CREATE TABLE IF NOT EXISTS
db/init_db.py            ← idempotent runner: schema + categories + bcrypt users
seed/__init__.py         ← empty
seed/categories.sql      ← 22 categories with INSERT OR IGNORE
seed/users.sql           ← comment/template only — no hardcoded hashes
requirements.txt         ← all deps pinned
.env.example             ← SECRET_KEY and DATABASE_URL placeholders
.gitignore               ← .env, *.db, *.sqlite3, __pycache__
```

### Schema rules

- `CREATE TABLE IF NOT EXISTS` on all 5 tables
- No `CHECK` constraint on `vat_rate` — validation is application-layer only
- `category_id` integers are fixed (1–4 income, 5–22 expense) — must be stable FKs
- `vat_deductible_pct` is `REAL` (nullable in schema) — NOT NULL enforced in app layer only
- `logged_by` and `voided_by` are integer FKs to `users.id`

### Seed rules

- `INSERT OR IGNORE` throughout — idempotent
- 22 categories: 4 income (ids 1–4), 18 expense (ids 5–22)
- 3 users: owner, assistant, wife — `password_hash` bcrypt only, plaintext never stored
- `category_id` values must match exact integers from spec (not auto-assigned)

---

## Architecture principles to check

| # | Principle | Check |
|---|-----------|-------|
| 1 | No `vat_rate` CHECK constraint in db/schema.sql | grep |
| 3 | No SQL DELETE anywhere | grep |
| 7 | No derived value columns (vat_amount, net_amount, etc.) | grep |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i1/t1-schema
```

### Step 2 — Verify files exist

```bash
ls db/schema.sql db/init_db.py db/__init__.py
ls seed/categories.sql seed/users.sql seed/__init__.py
ls requirements.txt .env.example .gitignore
```

Every file must exist. Missing file = `CHANGES REQUIRED`.

### Step 3 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-1
```

Only the 9 files above must appear. Any unexpected file = scope violation.

### Step 4 — Schema verification

```bash
# Must have 5 tables
grep -c "CREATE TABLE IF NOT EXISTS" db/schema.sql
# Expected: 5

# Must NOT have CHECK on vat_rate
grep "CHECK.*vat_rate" db/schema.sql
# Expected: no output

# Must NOT have derived value columns
grep -i "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" db/schema.sql
# Expected: no output

# Must NOT have hard deletes
grep -i "DROP TABLE\|DELETE FROM" db/schema.sql db/init_db.py
# Expected: no output
```

### Step 5 — Category count

```bash
python db/init_db.py
python -c "
import sqlite3
conn = sqlite3.connect('cashflow.db')
print('total:', conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0])
print('income:', conn.execute(\"SELECT COUNT(*) FROM categories WHERE direction='income'\").fetchone()[0])
print('expense:', conn.execute(\"SELECT COUNT(*) FROM categories WHERE direction='expense'\").fetchone()[0])
"
# Expected: total: 22, income: 4, expense: 18
```

### Step 6 — Idempotency

```bash
python db/init_db.py   # second run
python -c "
import sqlite3
conn = sqlite3.connect('cashflow.db')
print(conn.execute('SELECT COUNT(*) FROM categories').fetchone())  # (22,)
print(conn.execute('SELECT COUNT(*) FROM users').fetchone())       # (3,)
"
```

### Step 7 — Password hashing

```bash
python -c "
import sqlite3
conn = sqlite3.connect('cashflow.db')
for row in conn.execute('SELECT username, password_hash FROM users'):
    h = row[1]
    assert h.startswith('\$2b\$'), f'Plaintext password detected for {row[0]}: {h!r}'
    print(f'{row[0]}: OK')
"
```

### Step 8 — Category ID stability

Read `seed/categories.sql`. Verify:
- `internal_transfer` has `category_id = 3`
- `cleaning` has `category_id = 11`
- `transport_vehicle` has `category_id = 18`
- `other_expense` has `category_id = 22`

If IDs are auto-assigned (no explicit `category_id` in INSERT) = `CHANGES REQUIRED`. Future tasks depend on these being stable.

### Step 9 — .env in .gitignore

```bash
grep "^\.env$" .gitignore
# Expected: .env
git status --short .env 2>/dev/null
# Expected: no output — .env must not be tracked
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every item implemented correctly with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside the allowed list.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] python db/init_db.py runs twice without error or duplicates
- [PASS|FAIL] All 5 tables exist
- [PASS|FAIL] Exactly 22 categories (4 income, 18 expense)
- [PASS|FAIL] Exactly 3 users with bcrypt-hashed passwords
- [PASS|FAIL] No CHECK constraint on vat_rate in schema
- [PASS|FAIL] category_id integers are explicit and stable (1–22)
- [PASS|FAIL] .env is gitignored
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

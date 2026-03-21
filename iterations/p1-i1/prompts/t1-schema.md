# I1-T1 — Schema + Seed Data
**Agent:** Codex
**Branch:** `feature/p1-i1/t1-schema`
**PR target:** `feature/phase-1/iteration-1`

---

## Context

cashflow-tracker is a private cash flow notebook for a 3-person Polish service business. It tracks gross income/expense transactions with full Polish VAT. This task creates the database foundation — every other task depends on it.

**Rules that apply to every file you produce:**
- `CREATE TABLE IF NOT EXISTS` — idempotent, safe to run twice
- `INSERT OR IGNORE` — seed is idempotent, no duplicates on re-run
- No CHECK constraint on `vat_rate` in the database — validation is application-layer only
- `amount` always stores gross (VAT-inclusive) — never net
- `logged_by` and `voided_by` are integer FKs to `users.id` — never name strings
- Derived values (`vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost`) are never stored

---

## Schema — implement exactly as specified

### db/schema.sql

```sql
CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    telegram_user_id TEXT UNIQUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id                INTEGER PRIMARY KEY,
    name                       TEXT NOT NULL UNIQUE,
    label                      TEXT NOT NULL,
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    default_vat_rate           REAL NOT NULL,
    default_vat_deductible_pct REAL
);

CREATE TABLE IF NOT EXISTS transactions (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    date                       DATE NOT NULL,
    amount                     DECIMAL(10,2) NOT NULL,
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    category_id                INTEGER NOT NULL REFERENCES categories(category_id),
    payment_method             TEXT NOT NULL CHECK(payment_method IN ('cash','card','transfer')),
    vat_rate                   REAL NOT NULL,
    income_type                TEXT CHECK(income_type IN ('internal','external')),
    vat_deductible_pct         REAL,
    manual_vat_amount          DECIMAL(10,2),
    description                TEXT,
    logged_by                  INTEGER NOT NULL REFERENCES users(id),
    is_active                  BOOLEAN NOT NULL DEFAULT TRUE,
    void_reason                TEXT,
    voided_by                  INTEGER REFERENCES users(id),
    replacement_transaction_id INTEGER REFERENCES transactions(id),
    created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings_audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    key        TEXT NOT NULL,
    old_value  TEXT,
    new_value  TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Important: `vat_rate` has no CHECK constraint — do not add one.

---

## Seed data — implement exactly as specified

### seed/categories.sql

```sql
-- Income categories
INSERT OR IGNORE INTO categories (category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)
VALUES
    (1,  'services',          'Services',            'income',  23, NULL),
    (2,  'products',          'Products sold',        'income',  23, NULL),
    (3,  'internal_transfer', 'Internal transfer',    'income',   0, NULL),
    (4,  'other_income',      'Other income',         'income',  23, NULL);

-- Expense categories
INSERT OR IGNORE INTO categories (category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)
VALUES
    (5,  'marketing',            'Marketing & advertising',    'expense', 23, 100),
    (6,  'marketing_commission', 'Sales commissions',          'expense', 23, 100),
    (7,  'rent',                 'Rent & premises',            'expense', 23, 100),
    (8,  'utilities',            'Utilities',                  'expense', 23, 100),
    (9,  'renovation',           'Renovation & repairs',       'expense', 23, 100),
    (10, 'office_supplies',      'Office supplies',            'expense', 23, 100),
    (11, 'cleaning',             'Cleaning services',          'expense',  0,   0),
    (12, 'consumables',          'Operational consumables',    'expense', 23, 100),
    (13, 'equipment',            'Equipment & tools',          'expense', 23, 100),
    (14, 'contractor_fees',      'Contractor & educator fees', 'expense', 23, 100),
    (15, 'taxes',                'Taxes & ZUS',                'expense',  0,   0),
    (16, 'it_software',          'IT & software',              'expense', 23, 100),
    (17, 'salaries',             'Salaries & employee costs',  'expense',  0,   0),
    (18, 'transport_vehicle',    'Vehicle & petrol',           'expense', 23,  50),
    (19, 'transport_travel',     'Travel & transport',         'expense',  0, 100),
    (20, 'training',             'Training & education',       'expense', 23, 100),
    (21, 'inventory',            'Inventory purchases',        'expense', 23, 100),
    (22, 'other_expense',        'Other expense',              'expense', 23, 100);
```

### seed/users.sql

This file is a template only — do not hardcode password hashes here. Hashing is done at runtime in `db/init_db.py`.

```sql
-- Passwords are bcrypt-hashed at runtime in db/init_db.py
-- This file documents the user structure only
-- INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)
-- Users: owner / assistant / wife
```

---

## db/init_db.py — implement this logic

```python
"""
Idempotent database initialiser.
Run with: python db/init_db.py
Safe to run multiple times — no duplicate rows, no errors.
"""
import sqlite3
import pathlib
import bcrypt

DB_PATH = pathlib.Path("cashflow.db")
SCHEMA_PATH = pathlib.Path("db/schema.sql")
CATEGORIES_SQL = pathlib.Path("seed/categories.sql")

USERS = [
    ("owner",     "owner123"),
    ("assistant", "assistant123"),
    ("wife",      "wife123"),
]


def initialise_db(conn: sqlite3.Connection | None = None) -> None:
    """Create schema and seed data. Accepts an optional connection for testing."""
    if conn is None:
        conn = sqlite3.connect(DB_PATH)

    # Apply schema
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)

    # Seed categories
    categories_sql = CATEGORIES_SQL.read_text()
    conn.executescript(categories_sql)

    # Seed users — hash passwords at runtime
    for username, plaintext_password in USERS:
        password_hash = bcrypt.hashpw(
            plaintext_password.encode(), bcrypt.gensalt()
        ).decode()
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )

    conn.commit()


if __name__ == "__main__":
    initialise_db()
    print("Database initialised.")
```

---

## requirements.txt

```
fastapi>=0.115.0
uvicorn[standard]>=0.29.0
jinja2>=3.1.0
python-multipart>=0.0.9
starlette>=0.37.0
itsdangerous>=2.1.0
bcrypt>=4.1.0
pytest>=8.0.0
httpx>=0.27.0
ruff>=0.4.0
python-dotenv>=1.0.0
```

---

## .env.example

```
SECRET_KEY=change-me-before-use
DATABASE_URL=sqlite:///./cashflow.db
```

---

## .gitignore additions

Add to `.gitignore` (create if it does not exist):

```
.env
*.db
*.sqlite3
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
```

---

## Empty __init__.py files

Create these as empty files:
- `db/__init__.py`
- `seed/__init__.py`

---

## Worktree setup

```bash
# From the repo root, on the iteration branch
git fetch origin
git checkout feature/phase-1/iteration-1

# Create a worktree for this task
git worktree add -b feature/p1-i1/t1-schema ../cashflow-tracker-t1 feature/phase-1/iteration-1
cd ../cashflow-tracker-t1
```

## PR

```bash
git add db/ seed/ requirements.txt .env.example .gitignore
git commit -m "feat: schema, idempotent seed, and bcrypt user init (I1-T1)"
git push -u origin feature/p1-i1/t1-schema
gh pr create --base feature/phase-1/iteration-1 --head feature/p1-i1/t1-schema \
  --title "I1-T1: Schema + seed data" \
  --body "Creates 5-table schema, 22 categories, 3 bcrypt-hashed users. Idempotent."
```

---

## Acceptance checklist

- [ ] `python db/init_db.py` runs twice — no error, no duplicate rows
- [ ] `SELECT COUNT(*) FROM categories` → 22
- [ ] `SELECT COUNT(*) FROM users` → 3
- [ ] All `password_hash` values start with `$2b$`
- [ ] All 5 tables exist: users, categories, transactions, settings, settings_audit
- [ ] No `vat_rate` CHECK constraint in schema
- [ ] `.env` is in `.gitignore`

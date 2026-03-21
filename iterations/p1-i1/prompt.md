# cashflow-tracker Task Prompt — P1-I1: Foundation — Schema, Seed Data & Opening Balance

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/validation.py → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores the actual gross cash; VAT is extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or any reporting layer |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly; block the save, never default silently |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost` are computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point; route handlers and templates call it, never re-implement it |

---

## Repository State

- **Feature branch for this task:** `phase-1/iteration-1`
- **Tests passing:** 0
- **Ruff:** clean
- **Last completed task:** none — this is the first task
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I1 |
| Title | Foundation — Schema, Seed Data & Opening Balance |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 1 — Foundation |
| Feature branch | `phase-1/iteration-1` |
| Depends on | none |
| Blocks | P1-I2 (Authentication) |
| PR scope | One PR per iteration into `main`. Do not combine iterations. Do not push partial work. |

---

## Task Goal

This task creates the foundation the entire project builds on: the database schema, idempotent seed data, the FastAPI application skeleton, and the opening balance setup screen. Without it, no subsequent iteration can start.

The opening balance is a hard prerequisite for the transaction form — users must not be able to reach `/transactions/new` without setting it first. This task puts that gate in place and ensures every future page shows the SANDBOX banner that tells users this data is non-production.

---

## Files to Read Before Starting

### Mandatory — read these for every task, in this order

```
CLAUDE.md                                              ← constitution — read first, always
project.md                                             ← current state and what this iteration delivers
skills/cash-flow/schema/SKILL.md                       ← full table structure and SQLite/PG boundary rules
skills/cash-flow/transaction_validator/SKILL.md        ← all 10 domain rules — the single source of truth
skills/cash-flow/error_handling/SKILL.md               ← no silent failures, inline errors, block on any failure
```

### Task-specific

```
skills/cash-flow/auth_logic/SKILL.md                   ← session identity rules (users.id FK, never name string)
docs/concept.md                                        ← full category reference table with all 22 categories and their defaults
```

---

## Existing Code This Task Builds On

### Already exists and must NOT be reimplemented:

This is Iteration 1. The repo contains only documentation and skill files — no application code exists yet. Do not read the docs directory expecting application source code.

### Contracts this task establishes for P1-I2:

```
db/schema.sql           ← frozen after this task; P1-I2 must not alter the schema
db/init_db.py           ← must remain idempotent; P1-I2 only adds routes, not schema
seed/users.sql          ← 3 users exist with known test credentials; P1-I2 builds login against these
seed/categories.sql     ← 22 categories exist; all subsequent tasks rely on these FKs
settings table          ← opening_balance and as_of_date keys are the contract; P1-I2 reads them for the redirect gate
```

---

## What to Build

### New files

```
app/main.py                                   ← FastAPI app factory, router registration, session middleware, lifespan
app/routes/__init__.py                        ← empty init
app/routes/settings.py                        ← GET and POST /settings/opening-balance
app/templates/base.html                       ← base layout with SANDBOX banner (visible on every page)
app/templates/settings/opening_balance.html   ← opening balance form
db/schema.sql                                 ← all 6 tables: users, categories, transactions, settings, settings_audit, + alembic not needed
db/init_db.py                                 ← schema creation + seed runner (idempotent — safe to run twice)
seed/categories.sql                           ← all 22 categories with INSERT OR IGNORE
seed/users.sql                                ← 3 users with bcrypt-hashed passwords, INSERT OR IGNORE
.env.example                                  ← SECRET_KEY and DATABASE_URL — .env added to .gitignore
requirements.txt                              ← all dependencies pinned
tests/__init__.py                             ← empty init so pytest discovers the tests/ directory
tests/test_init_db.py                         ← idempotency and seed verification tests
```

### Modified files

```
.gitignore              ← add .env, __pycache__, *.db, *.sqlite3
```

### Database schema — exact table definitions

Implement these tables exactly in `db/schema.sql`. Use `CREATE TABLE IF NOT EXISTS` throughout.

```sql
-- Table 1
CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    telegram_user_id TEXT UNIQUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2
CREATE TABLE IF NOT EXISTS categories (
    category_id                INTEGER PRIMARY KEY,
    name                       TEXT NOT NULL UNIQUE,
    label                      TEXT NOT NULL,
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    default_vat_rate           REAL NOT NULL,
    default_vat_deductible_pct REAL
);

-- Table 3
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

-- Table 4
CREATE TABLE IF NOT EXISTS settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 5
CREATE TABLE IF NOT EXISTS settings_audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    key        TEXT NOT NULL,
    old_value  TEXT,
    new_value  TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Note: `vat_rate` has **no CHECK constraint** in the database. Validation lives in the application layer only. Do not add one.

### Seed data — exact category rows

`seed/categories.sql` must insert exactly these 22 rows using `INSERT OR IGNORE`. Use explicit `category_id` integers so FKs are stable across re-runs.

```sql
-- Income categories (1–4)
INSERT OR IGNORE INTO categories (category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)
VALUES
    (1,  'services',          'Services',            'income',  23, NULL),
    (2,  'products',          'Products sold',        'income',  23, NULL),
    (3,  'internal_transfer', 'Internal transfer',    'income',   0, NULL),
    (4,  'other_income',      'Other income',         'income',  23, NULL);

-- Expense categories (5–22)
INSERT OR IGNORE INTO categories (category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct)
VALUES
    (5,  'marketing',             'Marketing & advertising',    'expense', 23,   100),
    (6,  'marketing_commission',  'Sales commissions',          'expense', 23,   100),
    (7,  'rent',                  'Rent & premises',            'expense', 23,   100),
    (8,  'utilities',             'Utilities',                  'expense', 23,   100),
    (9,  'renovation',            'Renovation & repairs',       'expense', 23,   100),
    (10, 'office_supplies',       'Office supplies',            'expense', 23,   100),
    (11, 'cleaning',              'Cleaning services',          'expense',  0,     0),
    (12, 'consumables',           'Operational consumables',    'expense', 23,   100),
    (13, 'equipment',             'Equipment & tools',          'expense', 23,   100),
    (14, 'contractor_fees',       'Contractor & educator fees', 'expense', 23,   100),
    (15, 'taxes',                 'Taxes & ZUS',                'expense',  0,     0),
    (16, 'it_software',           'IT & software',              'expense', 23,   100),
    (17, 'salaries',              'Salaries & employee costs',  'expense',  0,     0),
    (18, 'transport_vehicle',     'Vehicle & petrol',           'expense', 23,    50),
    (19, 'transport_travel',      'Travel & transport',         'expense',  0,   100),
    (20, 'training',              'Training & education',       'expense', 23,   100),
    (21, 'inventory',             'Inventory purchases',        'expense', 23,   100),
    (22, 'other_expense',         'Other expense',              'expense', 23,   100);
```

### Seed data — users

`seed/users.sql` must insert exactly 3 users using `INSERT OR IGNORE`. Passwords must be bcrypt-hashed at seed time — **never store plaintext**.

```
username: owner       password: owner123
username: assistant   password: assistant123
username: wife        password: wife123
```

Because `INSERT OR IGNORE` requires pre-hashed values in SQL, generate the bcrypt hashes in `db/init_db.py` at runtime and insert via Python — do not hardcode hash strings in the SQL file. Use `INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)`.

### Public API

```python
# app/routes/settings.py

@router.get("/settings/opening-balance")
async def get_opening_balance(request: Request) -> HTMLResponse:
    """Render the opening balance setup form.
    Shows current value if already set, empty form if not."""

@router.post("/settings/opening-balance")
async def post_opening_balance(
    request: Request,
    opening_balance: float = Form(...),
    as_of_date: str = Form(...),
) -> RedirectResponse:
    """Save opening balance and as_of_date to settings table.
    Writes an audit row to settings_audit for every change (including the first).
    Redirects to / on success.
    Raises HTTPException(400) if opening_balance <= 0 or as_of_date is invalid."""

# app/main.py

def get_db() -> sqlite3.Connection:
    """Return a database connection. Use as a FastAPI dependency."""

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
```

### Behaviour rules

- **Rule 1:** The SANDBOX banner must appear on every page via `base.html` — it is not optional decoration. It must read: "SANDBOX — this is a test environment. Data may be discarded."
- **Rule 2:** Navigating to any route other than `/settings/opening-balance` when `opening_balance` is not set in the settings table must redirect to `/settings/opening-balance`. Implement this as a dependency or middleware in `app/main.py`. A warning is not sufficient — it must be a hard redirect.
- **Rule 3:** `db/init_db.py` must be idempotent. Running it twice must produce no duplicate rows and no errors. Use `CREATE TABLE IF NOT EXISTS` for schema and `INSERT OR IGNORE` for seed data.
- **Rule 4:** `settings_audit` receives a row for every write to `settings` — including the initial set. It records `key`, `old_value` (NULL on first write), `new_value`, and `changed_at`.
- **Rule 5:** The `.env` file must never be committed. `.env.example` is committed with placeholder values only (`SECRET_KEY=change-me`, `DATABASE_URL=sqlite:///./cashflow.db`).
- **Rule 6:** Session middleware requires `SECRET_KEY` from `.env`. If the key is missing, the app must fail to start with a descriptive error — not silently use a default.

### Input/output examples

```
# Example: opening balance already set — GET /settings/opening-balance
→ 200 OK, form pre-populated with current opening_balance and as_of_date

# Example: opening balance not set — GET /transactions/new (future route, but the gate applies)
→ 302 Redirect to /settings/opening-balance

# Example: POST /settings/opening-balance — valid
POST /settings/opening-balance
opening_balance=50000.00, as_of_date=2026-01-01
→ Inserts/updates settings table (keys: opening_balance, as_of_date)
→ Writes audit row to settings_audit
→ 302 Redirect to /

# Example: POST /settings/opening-balance — invalid
POST /settings/opening-balance
opening_balance=-100, as_of_date=2026-01-01
→ 400 Bad Request, error shown inline on form
```

---

## Architecture Constraints

These apply to every task without exception. No PR is approved if any of these are violated.

1. **Gross amounts always** — store the actual gross cash amount. Never net. VAT is derived at query time.
2. **Deterministic logic** — no LLM calls in validation, calculation, or reporting. All financial logic is deterministic Python.
3. **Soft-delete only** — never use SQL DELETE on transactions. Deactivation = `is_active = FALSE` + mandatory `void_reason` + `voided_by` (users.id).
4. **category_id is always FK** — never accept free-text category names. Always validate against the categories table.
5. **No silent failures** — never catch an error and return a default. Raise HTTPException with a descriptive message.
6. **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs from `users.id`. Never name strings.
7. **Derived values never stored** — do not add columns for `vat_amount`, `net_amount`, `vat_reclaimable`, or `effective_cost`.
8. **Validation in service layer** — `services/validation.py` is the single enforcement point. Route handlers call it; they do not reimplement rules.

---

## Allowed Files

Only these files may be created or modified. If the implementation requires touching a file not on this list, **stop and ask**.

```
app/__init__.py                                ← new: empty package init
app/main.py                                    ← new: FastAPI app, middleware, db dependency, opening balance gate
app/routes/__init__.py                         ← new: empty package init
app/routes/settings.py                         ← new: opening balance GET/POST
app/templates/base.html                        ← new: base layout with SANDBOX banner
app/templates/settings/opening_balance.html    ← new: opening balance form
db/schema.sql                                  ← new: 5-table schema (CREATE TABLE IF NOT EXISTS)
db/init_db.py                                  ← new: schema + seed runner (idempotent)
db/__init__.py                                 ← new: empty package init
seed/categories.sql                            ← new: 22 categories with INSERT OR IGNORE
seed/users.sql                                 ← new: user insert template (hashing done in init_db.py)
seed/__init__.py                               ← new: empty package init
tests/__init__.py                              ← new: empty package init
tests/test_init_db.py                          ← new: idempotency and seed verification tests
.env.example                                   ← new: SECRET_KEY and DATABASE_URL placeholders
.gitignore                                     ← modify: add .env, *.db, *.sqlite3, __pycache__
requirements.txt                               ← new: all dependencies pinned
```

---

## Files NOT to Touch

The following do not exist yet but describe where P1-I2 will work — do not create them:

```
app/routes/auth.py                 ← owned by P1-I2 (Authentication)
app/templates/auth/                ← owned by P1-I2
app/services/validation.py        ← owned by P1-I3 (Transaction Capture)
app/services/calculations.py      ← owned by P1-I3
app/routes/transactions.py        ← owned by P1-I3
```

If the opening balance gate implementation makes you want to create auth routes, **stop and raise it** — this task implements only the redirect to `/settings/opening-balance`, not the full auth system.

---

## Acceptance Criteria

- [ ] `python db/init_db.py` runs twice without error and without creating duplicate rows — verified by running it twice and querying row counts
- [ ] All 5 tables exist after init: `users`, `categories`, `transactions`, `settings`, `settings_audit`
- [ ] All 22 categories present with correct `name`, `direction`, `default_vat_rate`, and `default_vat_deductible_pct` — verified by SELECT COUNT
- [ ] 3 users present: `owner`, `assistant`, `wife` — with `password_hash` populated (not null, not plaintext)
- [ ] Opening balance form saves `opening_balance` and `as_of_date` to the `settings` table
- [ ] Every save to `settings` (including the first) writes a row to `settings_audit`
- [ ] Any route other than `/settings/opening-balance` redirects to it when opening balance is not set
- [ ] SANDBOX banner visible on the opening balance page (via `base.html`)
- [ ] `SECRET_KEY` missing from `.env` causes app to fail with a descriptive error at startup
- [ ] `.env` is in `.gitignore` — must not appear in `git status` as tracked
- [ ] All 0 prior tests still pass — `pytest` exit code 0
- [ ] Ruff clean — `ruff check .` exit code 0

---

## Tests Required

**Test file:** `tests/test_init_db.py`

| Test function | What it verifies |
|---------------|-----------------|
| `test_init_db_creates_all_tables` | After running init_db, all 5 tables exist in the SQLite database |
| `test_init_db_is_idempotent` | Running init_db twice produces no duplicate rows in users or categories |
| `test_categories_count_is_22` | Exactly 22 rows in categories after seeding |
| `test_categories_income_count_is_4` | Exactly 4 rows with `direction = 'income'` |
| `test_categories_expense_count_is_18` | Exactly 18 rows with `direction = 'expense'` |
| `test_users_count_is_3` | Exactly 3 rows in users after seeding |
| `test_users_passwords_are_hashed` | `password_hash` for all 3 users starts with `$2b$` (bcrypt prefix); plaintext never stored |
| `test_opening_balance_saves_to_settings` | POST /settings/opening-balance saves `opening_balance` and `as_of_date` to settings table |
| `test_opening_balance_writes_audit_row` | POST /settings/opening-balance writes a row to settings_audit with correct key and new_value |
| `test_opening_balance_rejects_negative` | POST with `opening_balance = -100` returns 400 |
| `test_missing_opening_balance_redirects` | GET /any-protected-route redirects to /settings/opening-balance when balance not set |

```python
# Pattern: database test using a fresh in-memory SQLite db per test
import sqlite3
import pytest
from db.init_db import initialise_db

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    initialise_db(conn)
    yield conn
    conn.close()

def test_categories_count_is_22(db):
    count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    assert count == 22

def test_users_passwords_are_hashed(db):
    hashes = db.execute("SELECT password_hash FROM users").fetchall()
    assert len(hashes) == 3
    for (h,) in hashes:
        assert h.startswith("$2b$"), f"Expected bcrypt hash, got: {h!r}"
```

```python
# Pattern: route test with TestClient
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(database_url=str(db_path))
    with TestClient(app) as c:
        yield c

def test_opening_balance_rejects_negative(client):
    response = client.post(
        "/settings/opening-balance",
        data={"opening_balance": "-100", "as_of_date": "2026-01-01"},
    )
    assert response.status_code == 400
```

---

## Edge Cases to Handle Explicitly

| Edge case | Expected behaviour |
|-----------|-------------------|
| `db/init_db.py` run twice | No duplicate rows; no errors; idempotent by design |
| `opening_balance = 0` | Reject with 400 — zero opening balance is not valid for a running business |
| `opening_balance < 0` | Reject with 400 with descriptive error message |
| `as_of_date` in wrong format (e.g. `21-03-2026`) | Reject with 400; store only ISO 8601 format (`YYYY-MM-DD`) |
| `SECRET_KEY` not in environment | App fails at startup with explicit error; never silently falls back to a weak default |
| Route accessed before opening balance is set | Hard redirect to `/settings/opening-balance`; not a flash message, not a warning |
| `settings_audit` on first write | `old_value` is NULL (not empty string); `new_value` is the submitted value |
| Category `category_id` values | Must match the exact integers in the seed table (1–22); these are FK references used by all future tasks |

---

## What NOT to Do

- Do not create `app/routes/auth.py` — authentication belongs to P1-I2
- Do not create `app/services/validation.py` — validation belongs to P1-I3
- Do not add a CHECK constraint on `vat_rate` in `schema.sql` — validation is application-layer only
- Do not hardcode a `SECRET_KEY` default in the application — fail loudly if it is missing
- Do not use `INSERT INTO` without `OR IGNORE` in seed files — the seed must be idempotent
- Do not store `password_hash` as plaintext — bcrypt only
- Do not add a `password` column — only `password_hash` exists in the schema
- Do not commit `.env` — it must be in `.gitignore` before the first commit
- Do not use `except: pass` or any silent exception swallowing
- Do not modify files outside the allowed list

---

## Handoff: What P1-I2 Needs From This Task

After this task merges, the following will be available for P1-I2 (Authentication):

```python
# Database
# Tables: users, categories, transactions, settings, settings_audit — all created, no schema changes needed

# Users available for login testing:
# username=owner,     password=owner123
# username=assistant, password=assistant123
# username=wife,      password=wife123

# Dependency available in app/main.py:
def get_db() -> sqlite3.Connection: ...   # returns a live db connection

# Contract P1-I2 must respect:
# - session['user_id'] must store users.id (integer) — never username string
# - The opening balance gate stays in place — authenticated routes still redirect if balance unset
# - db/schema.sql is frozen — P1-I2 adds routes only, not schema changes
```

---

## Execution Workflow

Follow this sequence exactly. Do not skip or reorder steps.

### Step 0 — Branch setup and draft PR (before anything else)

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Confirm the working tree is clean
git status
# Expected: "nothing to commit, working tree clean"

# 3. Create and switch to the feature branch
git checkout -b phase-1/iteration-1

# 4. Confirm you are on the right branch
git branch --show-current
# Expected: phase-1/iteration-1

# 5. Push the branch immediately
git push -u origin phase-1/iteration-1

# 6. Open a DRAFT PR before writing any code
gh pr create \
  --base main \
  --head phase-1/iteration-1 \
  --title "P1-I1: Foundation — Schema, Seed Data & Opening Balance" \
  --body "Work in progress. See iterations/prompt-p1-i1.md for full task spec." \
  --draft
```

### Step 1 — Verify the baseline

```bash
pytest
# Expected: 0 tests, exit code 0 (no failures)

ruff check .
# Expected: no issues, exit code 0
```

If ruff fails: fix before writing any implementation code.

### Step 2 — Read before writing

Read all files listed in "Files to Read Before Starting" in order. Do not write a line of implementation until you understand the schema and domain rules.

### Step 3 — Plan before multi-file changes

This task touches more than 2 files. Present the full implementation plan (which files, what changes, in what order) before writing any code. Wait for confirmation.

### Step 4 — Confirm allowed files

Before editing any file, cross-check against the "Allowed Files" list. If a file you need is not on the list, **stop and ask**.

### Step 5 — Implement

Build in this order:
1. `requirements.txt` and `.env.example` — establish dependencies first
2. `db/schema.sql` — schema is the foundation; everything else depends on it
3. `db/init_db.py` — make the schema + seed runner work before building routes
4. `seed/categories.sql` and `seed/users.sql` — complete seed data
5. `app/main.py` — FastAPI app with db dependency and opening balance gate middleware
6. `app/routes/settings.py` — opening balance GET/POST
7. `app/templates/base.html` and `app/templates/settings/opening_balance.html` — UI last
8. `tests/test_init_db.py` — tests after implementation is complete

### Step 6 — Test and lint

```bash
pytest
# Must pass: all new tests. Zero failures.

ruff check .
# Must be clean. Fix all issues before committing.
```

Do not submit if either command fails.

### Step 7 — Verify scope

```bash
git diff --name-only main
```

Every file in the output must appear in the "Allowed Files" list. Revert any unexpected file before committing.

### Step 8 — Commit and mark PR ready

```bash
git add <specific files — do not use git add -A>
git commit -m "feat: foundation schema, seed data, and opening balance (P1-I1)

Creates db/schema.sql (5 tables with CREATE TABLE IF NOT EXISTS), idempotent
seed via INSERT OR IGNORE (22 categories, 3 bcrypt-hashed users), FastAPI app
skeleton with SQLite dependency, and opening balance setup screen. Opening
balance gate redirects all unprotected routes until balance is set. SANDBOX
banner added to base template. settings_audit records every balance change.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

gh pr ready phase-1/iteration-1
```

Add a comment to the PR: what was built, what tests cover, any decisions made during implementation.

---

## Definition of Done

This task is complete when ALL of the following are true:

- [ ] `python db/init_db.py` runs twice without error or duplicate rows
- [ ] All 5 tables exist: `users`, `categories`, `transactions`, `settings`, `settings_audit`
- [ ] All 22 categories present with correct defaults — verified by `SELECT COUNT(*) FROM categories`
- [ ] 3 users present with bcrypt-hashed passwords — plaintext never stored
- [ ] Opening balance saves to settings table; every change creates a row in settings_audit
- [ ] Any route other than `/settings/opening-balance` redirects when balance is not set
- [ ] SANDBOX banner visible on every page
- [ ] All new tests listed in "Tests Required" pass
- [ ] Ruff clean (`ruff check .` exit code 0)
- [ ] Only files in "Allowed Files" were modified (`git diff --name-only main`)
- [ ] Feature branch pushed, draft PR opened, marked ready for review
- [ ] `.env` is gitignored; `.env.example` is committed with placeholder values
- [ ] No `except: pass`, no hard deletes, no free-text categories, no stored derived values

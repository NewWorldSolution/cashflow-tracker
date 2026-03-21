# P1-I1 — Foundation: Schema, Seed Data & Opening Balance
## Task Board

**Status:** READY
**Last updated:** 2026-03-21 — initial board created
**Iteration branch:** `feature/p1-i1`
**Targets:** `main`

---

## Dependency Map

```
I1-T1 (schema + seed)
  ├── I1-T2 (FastAPI skeleton) ──┐
  └── I1-T3 (opening balance)  ──┴──► I1-T4 (templates + UI) ──► I1-T5 (tests + close)
```

T2 and T3 may run in parallel once T1 is DONE.
T4 must wait for both T2 and T3 to be DONE.
T5 runs last — it closes the iteration.

---

## Tasks

| ID    | Title                      | Owner       | Status        | Depends on   | Branch                      |
|-------|----------------------------|-------------|---------------|--------------|-----------------------------|
| I1-T1 | Schema + seed data         | Claude Code | ⏳ WAITING    | —            | `feature/p1-i1-t1-schema`   |
| I1-T2 | FastAPI skeleton           | Claude Code | ⏳ WAITING    | I1-T1        | `feature/p1-i1-t2-fastapi`  |
| I1-T3 | Opening balance route      | Claude Code | ⏳ WAITING    | I1-T1        | `feature/p1-i1-t3-balance`  |
| I1-T4 | Base template + UI         | Claude Code | ⏳ WAITING    | I1-T2, I1-T3 | `feature/p1-i1-t4-ui`       |
| I1-T5 | Tests + ruff + PR ready    | Claude Code | ⏳ WAITING    | I1-T4        | `feature/p1-i1-t5-tests`    |

---

## Task Details

### I1-T1 — Schema + seed data

**Goal:** Create the database foundation. Everything else depends on this.

**Allowed files:**
```
db/__init__.py             ← new: empty package init
db/schema.sql              ← new: 5 tables with CREATE TABLE IF NOT EXISTS
db/init_db.py              ← new: schema + seed runner (idempotent)
seed/__init__.py           ← new: empty package init
seed/categories.sql        ← new: 22 categories with INSERT OR IGNORE
seed/users.sql             ← new: user insert template (hashing done in init_db.py)
requirements.txt           ← new: all dependencies pinned
.env.example               ← new: SECRET_KEY and DATABASE_URL placeholders
.gitignore                 ← modify: add .env, *.db, *.sqlite3, __pycache__
```

**Key rules:**
- `CREATE TABLE IF NOT EXISTS` on all 5 tables: users, categories, transactions, settings, settings_audit
- `INSERT OR IGNORE` throughout seed — idempotent, safe to run twice
- No CHECK constraint on `vat_rate` in schema — application layer only
- Users: bcrypt hashing done in Python at runtime, not hardcoded hash strings in SQL
- Category `category_id` integers must be stable (1–4 income, 5–22 expense)
- `.env` must be in `.gitignore` before first commit; `.env.example` committed with placeholder values

**Acceptance check:**
- `python db/init_db.py` runs twice without error or duplicates
- `SELECT COUNT(*) FROM categories` returns 22
- `SELECT COUNT(*) FROM users` returns 3
- All `password_hash` values start with `$2b$` (bcrypt)

**Notes for next tasks:** After T1 merges into `feature/p1-i1`, both T2 and T3 agents can branch from it. The `get_db()` dependency will be added by T2 in `app/main.py` — T3 should import it from there, not reimplement it.

---

### I1-T2 — FastAPI skeleton

**Goal:** Create the application entry point with session middleware, db dependency, and the opening balance gate.

**Allowed files:**
```
app/__init__.py            ← new: empty package init
app/main.py                ← new: FastAPI app factory, middleware, db dependency, opening balance gate
app/routes/__init__.py     ← new: empty package init
```

**Key rules:**
- `SECRET_KEY` loaded from environment — fail at startup with descriptive error if missing, never use a default
- Opening balance gate: any route except `/settings/opening-balance` redirects there if `opening_balance` key is not in settings table — implement as middleware or dependency
- Session middleware requires `SECRET_KEY` from env
- `get_db()` returns a `sqlite3.Connection` — used as a FastAPI dependency by all routes

**Acceptance check:**
- App starts with valid `SECRET_KEY` in env
- App fails with a clear error if `SECRET_KEY` is missing
- Visiting any route with no opening balance set redirects to `/settings/opening-balance`

**Notes for next tasks:** T3 imports `get_db` from `app.main`. T4 reads `base.html` path conventions from this task.

---

### I1-T3 — Opening balance route

**Goal:** Implement GET/POST `/settings/opening-balance` — reads and writes the settings table with audit trail.

**Depends on:** I1-T1 (settings table must exist), I1-T2 (imports `get_db` from `app.main`)

**Allowed files:**
```
app/routes/settings.py     ← new: GET and POST /settings/opening-balance
```

**Key rules:**
- GET: render form, pre-populate if value already exists
- POST: validate (`opening_balance > 0`, `as_of_date` must be valid ISO 8601), save to settings table, write audit row to settings_audit (`old_value = NULL` on first write), redirect to `/` on success
- Reject `opening_balance = 0` (not valid) and `opening_balance < 0`
- Reject malformed date (e.g. `21-03-2026`) — store only `YYYY-MM-DD`
- All errors shown inline — do not reset the form
- No validation logic in the route handler itself — raise `HTTPException(400)` with descriptive message

**Acceptance check:**
- POST with valid data saves to settings and writes to settings_audit
- POST with negative balance returns 400 with error message
- POST with malformed date returns 400 with error message
- `settings_audit.old_value` is NULL on first write, not empty string

---

### I1-T4 — Base template + UI

**Goal:** Create the Jinja2 base layout and the opening balance form template.

**Depends on:** I1-T2 (app structure), I1-T3 (route defined — template must match form action)

**Allowed files:**
```
app/templates/base.html                         ← new: base layout with SANDBOX banner
app/templates/settings/opening_balance.html     ← new: opening balance form
```

**Key rules:**
- SANDBOX banner must appear on every page — wording: "SANDBOX — this is a test environment. Data may be discarded."
- Banner is part of `base.html`, not per-page — it cannot be hidden or skipped
- Opening balance form: fields `opening_balance` (number input) and `as_of_date` (date input)
- Form errors shown inline — user input preserved on validation failure
- No JavaScript required for this task — plain HTML form only
- No inline styles — keep markup clean for future CSS

**Acceptance check:**
- SANDBOX banner visible when rendering the opening balance page
- Form submits to POST `/settings/opening-balance`
- Error message visible inline when server returns 400

---

### I1-T5 — Tests + ruff + PR ready

**Goal:** Write the test suite, verify ruff is clean, and close the iteration.

**Depends on:** I1-T4 (full implementation must be in place before testing)

**Allowed files:**
```
tests/__init__.py          ← new: empty package init so pytest discovers tests/
tests/test_init_db.py      ← new: 11 tests covering schema, seed, opening balance route
```

**Required tests (all must pass):**

| Test function | Verifies |
|---|---|
| `test_init_db_creates_all_tables` | All 5 tables exist after init |
| `test_init_db_is_idempotent` | Running init_db twice produces no duplicate rows |
| `test_categories_count_is_22` | Exactly 22 rows in categories |
| `test_categories_income_count_is_4` | 4 rows with `direction = 'income'` |
| `test_categories_expense_count_is_18` | 18 rows with `direction = 'expense'` |
| `test_users_count_is_3` | Exactly 3 rows in users |
| `test_users_passwords_are_hashed` | All `password_hash` start with `$2b$`; plaintext never stored |
| `test_opening_balance_saves_to_settings` | POST saves to settings table |
| `test_opening_balance_writes_audit_row` | POST writes row to settings_audit |
| `test_opening_balance_rejects_negative` | POST with negative balance returns 400 |
| `test_missing_opening_balance_redirects` | GET any protected route redirects when balance not set |

**Closure steps:**
1. `pytest` — all 11 tests pass, exit code 0
2. `ruff check .` — clean, exit code 0
3. `git diff --name-only feature/p1-i1` — only allowed files appear
4. Mark draft PR ready: `gh pr ready feature/p1-i1`
5. Update this file: set iteration Status to COMPLETE, update Last updated

---

## Agent Rules

1. **Read this file first.** Find your assigned task. Confirm status is WAITING or READY before starting.
2. **Update status to IN PROGRESS** before writing a single line of code. Edit the task table above.
3. **Check dependencies.** Never start a task whose dependency is not DONE. If a dep is still IN PROGRESS, wait.
4. **Branch from `feature/p1-i1`**, not from `main`. PRs target `feature/p1-i1`, not `main`.
5. **Read `iterations/p1-i1/prompt.md`** for full context, architecture rules, and public API signatures.
6. **After completing:** update status to DONE. Add one line under the task: what you produced and any decisions made.
7. **Never modify a task assigned to another agent.** If you need to communicate something, add a note under your own task.
8. **If blocked:** update status to BLOCKED with the reason. Stop and wait — do not work around it silently.
9. **Scope is the allowed files list for your task.** Any file not on your list requires a stop-and-ask.
10. **No `except: pass`, no hard deletes, no free-text categories, no stored derived values** — see `CLAUDE.md`.

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — dependency not yet DONE |
| 🔄 IN PROGRESS | Agent is actively working on this task |
| ✅ DONE | Task complete, branch merged into `feature/p1-i1` |
| 🚫 BLOCKED | Agent stopped — see note below task for reason |
| ✔ COMPLETE | All tasks DONE, iteration branch merged to `main` |

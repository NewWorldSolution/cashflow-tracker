# P1-I1 — Foundation: Schema, Seed Data & Opening Balance
## Task Board

**Status:** IN PROGRESS
**Last updated:** 2026-03-21 — I1-T1 DONE (merged), I1-T2 DONE (PR #2 open), T3 unblocked
**Iteration branch:** `feature/phase-1/iteration-1`  ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-1` → `main`  ← QA agent approves before merge

---

## Dependency Map

```
I1-T1 (schema + seed)
  ├── I1-T2 (FastAPI skeleton) ──┐
  └── I1-T3 (opening balance)  ──┴──► I1-T4 (templates + UI) ──► I1-T5 (tests + close)
```

T2 and T3 run in parallel (two different agents) once T1 is DONE.
T4 must wait for both T2 and T3 to be DONE.
T5 closes the iteration — runs last.

---

## Tasks

| ID    | Title                   | Owner       | Status     | Depends on   | Branch                        |
|-------|-------------------------|-------------|------------|--------------|-------------------------------|
| I1-T1 | Schema + seed data      | Codex       | ✅ DONE    | —            | `feature/p1-i1/t1-schema`    |
| I1-T2 | FastAPI skeleton        | Claude Code | ✅ DONE    | I1-T1        | `feature/p1-i1/t2-fastapi`   |
| I1-T3 | Opening balance route   | Codex       | ✅ DONE    | I1-T1        | `feature/p1-i1/t3-balance`   |
| I1-T4 | Base template + UI      | Claude Code | ✅ DONE    | I1-T2, I1-T3 | `feature/p1-i1/t4-ui`        |
| I1-T5 | Tests + ruff + PR ready | Claude Code | ⏳ WAITING | I1-T4        | `feature/p1-i1/t5-tests`     |

---

## Prompts & Reviews

| Task  | Implementation prompt                     | Review prompt                          | Reviewer    |
|-------|-------------------------------------------|----------------------------------------|-------------|
| I1-T1 | `iterations/p1-i1/prompts/t1-schema.md`   | `iterations/p1-i1/reviews/review-t1.md` | Claude Code |
| I1-T2 | `iterations/p1-i1/prompts/t2-fastapi.md`  | `iterations/p1-i1/reviews/review-t2.md` | Codex       |
| I1-T3 | `iterations/p1-i1/prompts/t3-balance.md`  | `iterations/p1-i1/reviews/review-t3.md` | Claude Code |
| I1-T4 | `iterations/p1-i1/prompts/t4-ui.md`       | `iterations/p1-i1/reviews/review-t4.md` | Codex       |
| I1-T5 | `iterations/p1-i1/prompts/t5-tests.md`    | `iterations/p1-i1/reviews/review-t5.md` | Codex       |
| —     | —                                         | `iterations/p1-i1/reviews/review-iteration.md` | Claude Code (QA) |

---

## Task Details

### I1-T1 — Schema + seed data (Codex)

**Goal:** Create the database foundation. Everything else depends on this.

**Allowed files:**
```
db/__init__.py
db/schema.sql
db/init_db.py
seed/__init__.py
seed/categories.sql
seed/users.sql
requirements.txt
.env.example
.gitignore
```

**Acceptance check (run after merge):**
```bash
python db/init_db.py && python db/init_db.py   # must run twice, no error, no duplicates
python -c "import sqlite3; c=sqlite3.connect('cashflow.db'); print(c.execute('SELECT COUNT(*) FROM categories').fetchone())"  # → (22,)
python -c "import sqlite3; c=sqlite3.connect('cashflow.db'); print(c.execute('SELECT COUNT(*) FROM users').fetchone())"  # → (3,)
```

---

### I1-T2 — FastAPI skeleton (Claude Code)

**Goal:** App entry point with session middleware, db dependency, and opening balance gate.

**Allowed files:**
```
app/__init__.py
app/main.py
app/routes/__init__.py
```

**Acceptance check:**
- App starts with valid `SECRET_KEY` in env
- App fails with descriptive error if `SECRET_KEY` is missing
- Any route other than `/settings/opening-balance` redirects there when balance is not set

---

### I1-T3 — Opening balance route (Codex)

**Goal:** GET/POST `/settings/opening-balance` with audit trail.

**Depends on:** I1-T1 (tables), I1-T2 (get_db dependency — interface defined in prompt)

**Allowed files:**
```
app/routes/settings.py
```

**Acceptance check:**
- POST saves to settings table, writes audit row to settings_audit
- POST with negative balance → 400
- POST with malformed date → 400
- `old_value` is NULL on first write

---

### I1-T4 — Base template + UI (Claude Code)

**Goal:** Jinja2 base layout with SANDBOX banner and opening balance form.

**Allowed files:**
```
app/templates/base.html
app/templates/settings/opening_balance.html
```

**Acceptance check:**
- SANDBOX banner on every page
- Form submits to POST `/settings/opening-balance`
- Errors shown inline, input preserved

---

### I1-T5 — Tests + ruff + PR ready (Claude Code)

**Goal:** Full test suite, ruff clean, iteration closed.

**Allowed files:**
```
tests/__init__.py
tests/test_init_db.py
```

**Closure steps:**
1. `pytest` — 11 tests pass, exit code 0
2. `ruff check .` — clean, exit code 0
3. `git diff --name-only feature/phase-1/iteration-1` — only allowed files
4. `gh pr ready feature/phase-1/iteration-1`
5. Update this file: Status → COMPLETE

---

## Agent Rules

1. **Read this file first.** Find your task. Confirm status is WAITING before starting.
2. **Update status to IN PROGRESS** before writing a line of code.
3. **Check dependencies.** Never start if any dep is not DONE.
4. **Worktree:** check out the iteration branch first, then create your task branch from it.
5. **PR targets the iteration branch**, not `main`. One task per PR.
6. **After completing:** set status to DONE. Add one-line note: what you produced.
7. **Never touch another agent's task.** Add notes under your own task only.
8. **If blocked:** set status to BLOCKED with reason. Stop.
9. **No `except: pass`, no hard deletes, no free-text categories, no stored derived values.**
10. Read your task prompt: `iterations/p1-i1/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency or not yet assigned |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-1` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

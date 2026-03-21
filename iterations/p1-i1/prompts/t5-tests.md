# I1-T5 — Tests + Ruff + PR Ready
**Agent:** Claude Code
**Branch:** `feature/p1-i1/t5-tests`
**PR target:** `feature/phase-1/iteration-1`

---

## Before starting — read these files in order

```
CLAUDE.md                                    ← architecture rules
iterations/p1-i1/tasks.md                   ← confirm I1-T4 (and all prior tasks) are DONE
skills/generic/qa_runner/SKILL.md            ← test against acceptance criteria, not code assumptions
skills/cash-flow/schema/SKILL.md             ← table structure to verify against
```

All prior tasks (T1–T4) must show ✅ DONE in `tasks.md`. If any is not DONE, stop and wait.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-1

# Confirm full stack is present
python -c "from app.main import app; print('app OK')"
python -c "from app.routes.settings import router; print('settings OK')"
ls app/templates/base.html app/templates/settings/opening_balance.html

git worktree add -b feature/p1-i1/t5-tests ../cashflow-tracker-t5 feature/phase-1/iteration-1
cd ../cashflow-tracker-t5
```

---

## What to build

### Allowed files (this task only)

```
tests/__init__.py          ← new: empty — allows pytest discovery
tests/test_init_db.py      ← new: 11 tests
```

No other files. Do not modify any existing files.

---

## tests/test_init_db.py — implement all 11 tests

```python
"""
Tests for I1-T1 (schema + seed) and I1-T3 (opening balance route).
All tests use isolated in-memory databases or TestClient with tmp_path.
"""
import sqlite3
import pytest
from fastapi.testclient import TestClient

from db.init_db import initialise_db


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Fresh in-memory SQLite database, fully initialised."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialise_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def client(tmp_path):
    """TestClient with a temporary database — isolated per test."""
    import os
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = f"sqlite:///./{db_path}"

    from app.main import create_app
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c


# ── schema + seed tests (I1-T1) ───────────────────────────────────────────────

def test_init_db_creates_all_tables(db):
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"users", "categories", "transactions", "settings", "settings_audit"}.issubset(tables)


def test_init_db_is_idempotent(db):
    """Running initialise_db twice must not create duplicate rows."""
    initialise_db(db)  # second run
    category_count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert category_count == 22
    assert user_count == 3


def test_categories_count_is_22(db):
    count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    assert count == 22


def test_categories_income_count_is_4(db):
    count = db.execute(
        "SELECT COUNT(*) FROM categories WHERE direction = 'income'"
    ).fetchone()[0]
    assert count == 4


def test_categories_expense_count_is_18(db):
    count = db.execute(
        "SELECT COUNT(*) FROM categories WHERE direction = 'expense'"
    ).fetchone()[0]
    assert count == 18


def test_users_count_is_3(db):
    count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 3


def test_users_passwords_are_hashed(db):
    """Passwords must be bcrypt hashes — never plaintext."""
    hashes = db.execute("SELECT password_hash FROM users").fetchall()
    assert len(hashes) == 3
    for row in hashes:
        h = row[0]
        assert h.startswith("$2b$"), (
            f"Expected bcrypt hash starting with '$2b$', got: {h!r}. "
            "Plaintext passwords must never be stored."
        )


# ── opening balance route tests (I1-T3) ───────────────────────────────────────

def test_opening_balance_saves_to_settings(client):
    response = client.post(
        "/settings/opening-balance",
        data={"opening_balance": "50000.00", "as_of_date": "2026-01-01"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    # Verify DB directly — status code alone is insufficient
    import sqlite3, os
    db_path = os.environ.get("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT value FROM settings WHERE key = 'opening_balance'").fetchone()
    conn.close()
    assert row is not None
    assert float(row[0]) == 50000.00


def test_opening_balance_writes_audit_row(client):
    client.post(
        "/settings/opening-balance",
        data={"opening_balance": "50000.00", "as_of_date": "2026-01-01"},
        follow_redirects=False,
    )
    import sqlite3, os
    db_path = os.environ.get("DATABASE_URL", "cashflow.db").removeprefix("sqlite:///./")
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT key, old_value, new_value FROM settings_audit ORDER BY id"
    ).fetchall()
    conn.close()
    keys = [r[0] for r in rows]
    assert "opening_balance" in keys
    # First write: old_value must be NULL
    balance_row = next(r for r in rows if r[0] == "opening_balance")
    assert balance_row[1] is None, (
        f"old_value must be NULL on first write, got: {balance_row[1]!r}"
    )


def test_opening_balance_rejects_negative(client):
    response = client.post(
        "/settings/opening-balance",
        data={"opening_balance": "-100", "as_of_date": "2026-01-01"},
    )
    assert response.status_code == 400


def test_missing_opening_balance_redirects(client):
    """Any protected route must redirect to opening balance when balance is not set."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/settings/opening-balance" in response.headers["location"]
```

---

## Closure sequence — run in this exact order

### 1. Run all tests

```bash
pytest -v
# Expected: 11 passed, 0 failed, exit code 0
# If any test fails: fix the test OR open a blocking issue in tasks.md — do not skip
```

### 2. Ruff

```bash
ruff check .
# Expected: no issues, exit code 0
# Fix all issues before continuing
```

### 3. Scope verification

```bash
git diff --name-only feature/phase-1/iteration-1
# Every file listed must be in the allowed files list from each task
# Unexpected files = scope violation = stop and investigate before committing
```

### 4. Commit and push

```bash
git add tests/__init__.py tests/test_init_db.py
git commit -m "test: 11 tests for schema, seed idempotency, and opening balance route (I1-T5)"
git push -u origin feature/p1-i1/t5-tests
```

### 5. Open PR

```bash
gh pr create \
  --base feature/phase-1/iteration-1 \
  --head feature/p1-i1/t5-tests \
  --title "I1-T5: Tests + iteration close" \
  --body "11 tests: schema creation, idempotency, category/user counts, bcrypt verification, opening balance save and audit trail, redirect gate. All pass. Ruff clean."
```

### 6. Update tasks.md

Set I1-T5 to ✅ DONE and iteration Status to COMPLETE in `iterations/p1-i1/tasks.md`.

---

## Acceptance checklist

- [ ] 11 tests exist and all pass (`pytest -v` exit code 0)
- [ ] `test_init_db_is_idempotent` calls `initialise_db` twice and verifies row counts
- [ ] `test_users_passwords_are_hashed` checks `$2b$` prefix — not just that password_hash is not null
- [ ] `test_opening_balance_saves_to_settings` queries the DB directly — not just checks status code
- [ ] `test_opening_balance_writes_audit_row` asserts `old_value IS NULL` on first write
- [ ] Ruff clean
- [ ] Scope: only `tests/__init__.py` and `tests/test_init_db.py` modified
- [ ] tasks.md updated to COMPLETE

---

## Self-review

When the acceptance checklist above is complete, read and execute the review at:

```
iterations/p1-i1/reviews/review-t5.md
```

Work through every step in the review file exactly as written. Produce the full required output (Verdict, What's Correct, Problems Found, Scope Violations, Acceptance Criteria Check, Exact Fixes Required).

If the verdict is `CHANGES REQUIRED` or `BLOCKED`: fix every listed issue, re-run tests and ruff, commit the fix, then re-execute the review from Step 1. Do not stop until the verdict is `PASS`.

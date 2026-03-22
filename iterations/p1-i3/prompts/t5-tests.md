# I3-T5 — Tests + Ruff + PR Ready

**Owner:** Codex
**Branch:** `feature/p1-i3/t5-tests` (from `feature/phase-1/iteration-3`)
**PR target:** `feature/phase-1/iteration-3`
**Depends on:** I3-T4 ✅ DONE (all implementation complete and merged)

---

## Goal

Write the full test suite, verify ruff is clean, and close the iteration.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i3/prompt.md          ← "Tests Required" section — full test list; read before writing any test
iterations/p1-i3/tasks.md           ← fixture spec in I3-T5 section
tests/test_auth.py                  ← reference for client fixture pattern (db_path attribute)
```

---

## Allowed Files

```
tests/test_validation.py        ← create new
tests/test_transactions.py      ← create new
iterations/p1-i3/tasks.md       ← status update only (step 5 of closure)
```

Do NOT modify any other file.

---

## Fixtures

**Two fixtures only — not three:**

```python
import os
import sqlite3
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    """Opening balance pre-set. Authenticated as 'owner'. db_path accessible as client.db_path."""
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    from app.main import create_app
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        c.db_path = db_path  # store for tests that need direct db access
        c.post(
            "/settings/opening-balance",
            data={"opening_balance": "50000", "as_of_date": "2026-01-01"},
            follow_redirects=True,
        )
        c.post("/auth/login", data={"username": "owner", "password": "owner123"})
        yield c


@pytest.fixture
def logged_out_client(tmp_path):
    """Opening balance pre-set. NOT authenticated (no login step).

    Note: This is different from P1-I2's fresh_client, which had NO opening balance.
    This fixture has an opening balance so AuthGate proceeds to the auth check,
    allowing us to test that the auth redirect fires (not the balance redirect).
    """
    db_path = str(tmp_path / "test.db")
    os.environ["SECRET_KEY"] = "test-secret-key"
    from app.main import create_app
    test_app = create_app(database_url=db_path)
    with TestClient(test_app, raise_server_exceptions=True, follow_redirects=False) as c:
        c.post(
            "/settings/opening-balance",
            data={"opening_balance": "50000", "as_of_date": "2026-01-01"},
            follow_redirects=True,
        )
        # no login — used only for unauthenticated redirect test
        yield c
```

---

## tests/test_validation.py — 22 tests

Each test calls `validate_transaction(data, db)` directly with a seeded in-memory db.

**Helpers you will need:**

```python
import sqlite3
from decimal import Decimal
from app.services.validation import validate_transaction

def make_db():
    """In-memory db seeded with categories and one test user."""
    from db.init_db import init_db
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    init_db(db)
    return db

def valid_income():
    return {
        "date": "2026-01-15",
        "direction": "income",
        "amount": Decimal("1000.00"),
        "category_id": <income category id from seeded db>,
        "payment_method": "transfer",
        "vat_rate": 23.0,
        "income_type": "external",
        "vat_deductible_pct": None,
        "description": None,
        "logged_by": 1,
        "is_active": True,
    }

def valid_expense():
    return {
        "date": "2026-01-15",
        "direction": "expense",
        "amount": Decimal("500.00"),
        "category_id": <expense category id>,
        "payment_method": "card",
        "vat_rate": 23.0,
        "income_type": None,
        "vat_deductible_pct": 100.0,
        "description": None,
        "logged_by": 1,
        "is_active": True,
    }
```

**Tests to implement (in order):**

```python
def test_valid_income_transaction_accepted(db)
def test_valid_expense_transaction_accepted(db)
def test_internal_income_vat_zero_accepted(db)
    # income_type='internal', vat_rate=0 → errors == []
def test_internal_income_nonzero_vat_rejected(db)
    # income_type='internal', vat_rate=23 → errors non-empty
def test_expense_vat_rate_override_accepted(db)
    # expense category with default_vat_rate=23, submitted vat_rate=5 → errors == []
    # (VAT override of category default is allowed — only internal income is restricted)
def test_expense_without_vat_deductible_pct_rejected(db)
def test_income_with_vat_deductible_pct_rejected(db)
def test_income_without_income_type_rejected(db)
    # direction='income', income_type=None → error
def test_expense_with_income_type_rejected(db)
    # direction='expense', income_type='external' → error
def test_other_expense_without_description_rejected(db)
def test_other_income_without_description_rejected(db)
def test_other_expense_with_description_accepted(db)
def test_invalid_category_id_rejected(db)
    # category_id=9999 (not in db) → error
def test_direction_category_mismatch_rejected(db)
    # income transaction using an expense category_id → error
def test_direction_category_match_accepted(db)
    # income transaction using an income category_id → errors == []
def test_invalid_vat_rate_rejected(db)
    # vat_rate=7 → error
def test_invalid_payment_method_rejected(db)
    # payment_method='cheque' → error
def test_invalid_vat_deductible_pct_rejected(db)
    # vat_deductible_pct=75 → error
def test_zero_amount_rejected(db)
def test_negative_amount_rejected(db)
def test_invalid_date_format_rejected(db)
    # date='not-a-date' → error
def test_multiple_errors_returned_together(db)
    # Two invalid fields → both errors present in returned list; len(errors) >= 2
```

---

## tests/test_transactions.py — 14 tests

All use the `client` fixture (or `logged_out_client` for the unauthenticated test).

```python
def test_create_form_loads(client):
    r = client.get("/transactions/new")
    assert r.status_code == 200

def test_create_transaction_success_redirects(client):
    r = client.post("/transactions/new", data={<valid income data>})
    assert r.status_code == 302
    assert r.headers["location"] == "/transactions/"

def test_create_transaction_saves_to_db(client):
    client.post("/transactions/new", data={<valid expense data>})
    conn = sqlite3.connect(client.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM transactions").fetchone()
    conn.close()
    assert row is not None
    assert row["direction"] == "expense"

def test_logged_by_set_from_session_not_form(client):
    # Post with an injected logged_by=999 in form data
    # Saved row must have logged_by = owner's actual id (from session), not 999
    client.post("/transactions/new", data={..., "logged_by": "999"})
    conn = sqlite3.connect(client.db_path)
    row = conn.execute("SELECT logged_by FROM transactions").fetchone()
    conn.close()
    assert row["logged_by"] != 999  # must be owner's id from session

def test_create_transaction_shows_all_errors(client):
    # Post with two invalid fields (e.g. missing category_id and invalid payment_method)
    r = client.post("/transactions/new", data={<data with 2 errors>})
    assert r.status_code == 422
    # Both error strings must appear in the response body
    assert <error_1_text> in r.text
    assert <error_2_text> in r.text

def test_form_input_preserved_on_error(client):
    r = client.post("/transactions/new", data={..., "description": "test note", <invalid field>})
    assert r.status_code == 422
    assert "test note" in r.text

def test_internal_income_vat_rate_enforced(client):
    r = client.post("/transactions/new", data={..., "income_type": "internal", "vat_rate": "23"})
    assert r.status_code == 422

def test_other_expense_description_required(client):
    # Use other_expense category, no description → 422
    r = client.post("/transactions/new", data={<other_expense data without description>})
    assert r.status_code == 422

def test_transaction_list_loads(client):
    r = client.get("/transactions/")
    assert r.status_code == 200

def test_transaction_list_shows_recent(client):
    client.post("/transactions/new", data={<valid data>})
    r = client.get("/transactions/")
    assert r.status_code == 200
    assert <some identifying field value> in r.text

def test_transaction_list_excludes_inactive(client):
    # Insert an inactive transaction directly in db
    conn = sqlite3.connect(client.db_path)
    conn.execute(
        "INSERT INTO transactions (date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, logged_by, is_active, void_reason) "
        "VALUES ('2026-01-01', 100, 'income', <income_cat_id>, 'cash', 23, 'external', 1, 0, 'test void')"
    )
    conn.commit(); conn.close()
    r = client.get("/transactions/")
    # Voided transaction must not appear in the list
    # (verify by checking for a unique value in that row, e.g. a distinct amount not used elsewhere)

def test_transaction_list_ordered_by_created_at(client):
    # Insert two transactions with a time gap or just check the list order matches DESC
    client.post("/transactions/new", data={<first valid transaction>})
    client.post("/transactions/new", data={<second valid transaction with distinguishable field>})
    r = client.get("/transactions/")
    # Second transaction (most recent) should appear before the first in the response text
    pos_first = r.text.find(<first_identifier>)
    pos_second = r.text.find(<second_identifier>)
    assert pos_second < pos_first  # second was created last, so appears first in DESC order

def test_categories_endpoint_returns_json(client):
    r = client.get("/categories")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "category_id" in item
        assert "name" in item
        assert "label" in item
        assert "direction" in item
        assert "default_vat_rate" in item

def test_unauthenticated_create_redirects(logged_out_client):
    r = logged_out_client.get("/transactions/new")
    assert r.status_code == 302
    assert "/auth/login" in r.headers["location"]
```

---

## Closure Steps

1. `pytest` — all tests pass (25 P1-I2 + 36 new P1-I3 tests), exit code 0
2. `ruff check .` — clean, exit code 0
3. `git diff --name-only feature/phase-1/iteration-3` — only `tests/test_validation.py`, `tests/test_transactions.py`, and `iterations/p1-i3/tasks.md`
4. `gh pr ready feature/phase-1/iteration-3`
5. Update `iterations/p1-i3/tasks.md`: Status → ✔ COMPLETE, Last updated → today, I3-T5 → ✅ DONE

---

## Done

- All tests pass
- Ruff clean
- PR marked ready
- tasks.md updated to ✔ COMPLETE

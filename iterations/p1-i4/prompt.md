# cashflow-tracker Task Prompt — P1-I4: Corrections, Hardening & Acceptance

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/ → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point for transaction field rules |

---

## Repository State

- **Iteration branch:** `feature/phase-1/iteration-4`
- **Base branch:** `main` (P1-I3 merged 2026-03-22)
- **Tests passing:** 61 (11 P1-I1 + 14 P1-I2 + 36 P1-I3)
- **Ruff:** clean
- **Last completed iteration:** P1-I3 — Transaction Capture (create form, validation, calculations, recent list)
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I4 |
| Title | Corrections, Hardening & Acceptance |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 4 |
| Feature branch | `feature/phase-1/iteration-4` |
| Depends on | P1-I3 (create/list routes, `validate_transaction`, `calculations.py`) |
| Blocks | P1-I5 (UI polish) |
| PR scope | Task branches PR into `feature/phase-1/iteration-4`. The iteration branch PRs into `main` after QA. Do not combine iterations. Do not push partial work. |

---

## Task Goal

This iteration adds the void/correct workflow with a complete audit trail, direct unit tests for the calculation service, and extended route tests. After P1-I4, authenticated users can view a transaction's full detail, void a mistaken entry with a required reason, and submit a correction that automatically links to the original. The data is trustworthy: every deactivated row carries who voided it, why, and what replaced it.

**Execution model:** 4 task branches, each with its own prompt file in `iterations/p1-i4/prompts/`. This file is the full reference; task prompt files are the execution guides.

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md
skills/cash-flow/schema/SKILL.md
skills/cash-flow/transaction_validator/SKILL.md
skills/cash-flow/deterministic_logic/SKILL.md
skills/cash-flow/error_handling/SKILL.md
```

### Task-specific

| Task | Also read |
|------|-----------|
| I4-T1 | `app/services/validation.py`, `app/services/calculations.py`, `app/routes/transactions.py` |
| I4-T2 | `iterations/p1-i4/prompts/t2-routes.md` |
| I4-T3 | `app/templates/transactions/create.html`, `app/templates/transactions/list.html`, `iterations/p1-i4/prompts/t3-templates.md` |
| I4-T4 | `iterations/p1-i4/prompts/t4-tests.md`, `tests/test_transactions.py`, `app/services/calculations.py` |

---

## Allowed Files

```
app/services/transaction_service.py       ← create new (T1)
app/routes/transactions.py                ← extend: 5 new route handlers (T2)
app/templates/transactions/detail.html    ← create new (T3)
app/templates/transactions/void.html      ← create new (T3)
app/templates/transactions/create.html    ← modify: form_action variable (T3)
app/templates/transactions/list.html      ← modify: date cell links to detail (T3)
tests/test_calculations.py                ← create new (T4)
tests/test_transactions.py                ← extend: +10 void/correct tests (T4)
iterations/p1-i4/tasks.md                 ← status updates only
```

Do NOT modify any other file.

---

## New Service — `app/services/transaction_service.py`

```python
import sqlite3


def get_transaction(transaction_id: int, db: sqlite3.Connection) -> dict | None:
    """
    Fetch a single transaction by id — active or voided.
    JOINs: categories (label), users (logged_by_username), users (voided_by_username via LEFT JOIN).
    Returns a plain dict or None if not found.
    db.row_factory = sqlite3.Row is assumed (set in app.main).
    """


def void_transaction(
    transaction_id: int,
    void_reason: str,
    voided_by: int,
    db: sqlite3.Connection,
) -> None:
    """
    Soft-delete a transaction.

    Preconditions — raise ValueError with a descriptive message if violated:
      1. Transaction must exist (get_transaction returns non-None).
      2. Transaction must be active (is_active = TRUE).
         Cannot void a transaction that is already voided.
      3. void_reason must be a non-empty string after strip().

    On success:
      UPDATE transactions SET is_active=0, void_reason=?, voided_by=? WHERE id=?

    Does NOT call db.commit() — the caller is responsible.
    """
```

---

## New Routes — extend `app/routes/transactions.py`

### GET /transactions/{id}

- Requires auth: `require_auth(request)`
- Call `get_transaction(id, db)` → 404 if None
- Render `transactions/detail.html` with context: `{"t": transaction_dict}`

### GET /transactions/{id}/void

- Requires auth
- Call `get_transaction(id, db)` → 404 if None or `not t["is_active"]`
- Render `transactions/void.html` with context: `{"t": t, "errors": [], "form_data": {}}`

### POST /transactions/{id}/void

- Requires auth
- Normalise: `void_reason = request form field "void_reason", stripped`
- Call `void_transaction(id, void_reason, user["id"], db)`
  - On `ValueError`: re-render `void.html` with `{"t": t, "errors": [str(e)], "form_data": {"void_reason": void_reason}}`, status_code=422
- `db.commit()`
- Redirect 302 → `/transactions/`

### GET /transactions/{id}/correct

- Requires auth
- Call `get_transaction(id, db)` → 404 if None or `not t["is_active"]`
- Build `form_data` dict from original transaction fields (all fields that the create form uses)
- Render `transactions/create.html` with context:
  ```python
  {
      "categories": <all categories from db>,
      "errors": [],
      "form_data": form_data,         # pre-filled from original
      "today": str(date.today()),
      "form_action": f"/transactions/{id}/correct",
  }
  ```

### POST /transactions/{id}/correct

- Requires auth
- Call `get_transaction(id, db)` → 404 if None or `not t["is_active"]`
- Normalise form data identically to `POST /transactions/new` (same `_s` / `_opt` helpers)
- Set `data["logged_by"] = user["id"]` (session, never form)
- Call `validate_transaction(data, db)` — same service as create
  - On errors: re-render `create.html` with errors + form_data + form_action, status_code=422
- On valid:
  1. INSERT new transaction with explicit column list (same as create — no derived values)
  2. `new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]`
  3. `db.execute("UPDATE transactions SET is_active=0, void_reason='Corrected', voided_by=?, replacement_transaction_id=? WHERE id=?", (user["id"], new_id, id))`
  4. `db.commit()`
  5. Redirect 302 → `/transactions/`

---

## Template Specs

### detail.html

```
{% extends "base.html" %}
{% block content %}
  <a href="/transactions/">← Back to list</a>
  <dl>
    <dt>Date</dt><dd>{{ t.date }}</dd>
    <dt>Direction</dt><dd>{{ t.direction }}</dd>
    <dt>Category</dt><dd>{{ t.category_label }}</dd>
    <dt>Amount (gross)</dt><dd>{{ t.amount }}</dd>
    <dt>VAT rate</dt><dd>{{ t.vat_rate }}%</dd>
    {% if t.direction == 'income' %}
    <dt>Income type</dt><dd>{{ t.income_type }}</dd>
    {% endif %}
    {% if t.direction == 'expense' %}
    <dt>VAT deductible</dt><dd>{{ t.vat_deductible_pct }}%</dd>
    {% endif %}
    <dt>Payment</dt><dd>{{ t.payment_method }}</dd>
    {% if t.description %}
    <dt>Description</dt><dd>{{ t.description }}</dd>
    {% endif %}
    <dt>Logged by</dt><dd>{{ t.logged_by_username }}</dd>
    <dt>Created at</dt><dd>{{ t.created_at }}</dd>
    <dt>Status</dt><dd>{{ 'Active' if t.is_active else 'Voided' }}</dd>
    {% if not t.is_active %}
    <dt>Void reason</dt><dd>{{ t.void_reason }}</dd>
    <dt>Voided by</dt><dd>{{ t.voided_by_username }}</dd>
    {% if t.replacement_transaction_id %}
    <dt>Replaced by</dt><dd><a href="/transactions/{{ t.replacement_transaction_id }}">#{{ t.replacement_transaction_id }}</a></dd>
    {% endif %}
    {% endif %}
  </dl>

  {% if t.is_active %}
  <a href="/transactions/{{ t.id }}/void">Void this transaction</a>
  <a href="/transactions/{{ t.id }}/correct">Correct this transaction</a>
  {% endif %}
{% endblock %}
```

### void.html

```
{% extends "base.html" %}
{% block content %}
  <a href="/transactions/{{ t.id }}">← Cancel</a>
  <h2>Void transaction</h2>
  <p>{{ t.date }} — {{ t.category_label }} — {{ t.amount }}</p>

  {% if errors %}
  <ul>{% for e in errors %}<li>{{ e }}</li>{% endfor %}</ul>
  {% endif %}

  <form method="post" action="/transactions/{{ t.id }}/void">
    <label>
      Reason for voiding (required)
      <input type="text" name="void_reason" value="{{ form_data.get('void_reason', '') }}">
    </label>
    <button type="submit">Void transaction</button>
  </form>
{% endblock %}
```

### create.html modification (single line)

Change the `<form>` opening tag from:
```html
<form method="post" action="/transactions/new">
```
to:
```html
<form method="post" action="{{ form_action | default('/transactions/new') }}">
```

### list.html modification (single line)

Change the date cell from:
```html
<td>{{ t.date }}</td>
```
to:
```html
<td><a href="/transactions/{{ t.id }}">{{ t.date }}</a></td>
```

---

## Tests Required

### `tests/test_calculations.py` — 10 new tests (direct unit tests, no DB)

```python
# Import: from app.services.calculations import vat_amount, net_amount, vat_reclaimable, effective_cost
# All assertions use Decimal; inputs via Decimal(str(...))

test_vat_amount_rate_0           # vat_amount(100, 0) == Decimal('0.00')
test_vat_amount_rate_5           # vat_amount(105, 5) == Decimal('5.00')
test_vat_amount_rate_8           # vat_amount(108, 8) == Decimal('8.00')
test_vat_amount_rate_23          # vat_amount(123, 23) == Decimal('23.00')
test_net_amount                  # net_amount(123, 23) == Decimal('100.00')
test_vat_reclaimable_100         # vat_reclaimable(123, 23, 100) == Decimal('23.00')
test_vat_reclaimable_50          # vat_reclaimable(123, 23, 50) == Decimal('11.50')
test_vat_reclaimable_0           # vat_reclaimable(123, 23, 0) == Decimal('0.00')
test_effective_cost_100pct       # effective_cost(123, 23, 100) == Decimal('100.00')
test_effective_cost_50pct        # effective_cost(123, 23, 50) == Decimal('111.50')
```

### `tests/test_transactions.py` — 10 new tests (extend existing suite)

```python
# Fixtures: client (authenticated, opening balance set, c.db_path accessible)
# Use the same fixture pattern as the existing file — no new fixtures

test_detail_view_returns_200         # Insert tx via db, GET /transactions/{id} → 200
test_detail_view_404_for_missing     # GET /transactions/99999 → 404
test_void_form_loads                 # GET /transactions/{id}/void → 200, contains void_reason input
test_void_requires_void_reason       # POST /transactions/{id}/void void_reason="" → 422
test_void_success                    # POST valid void_reason → 302; db: is_active=0, void_reason set, voided_by=1
test_voided_transaction_excluded_from_list  # Void tx; GET /transactions/ → amount not in response
test_void_already_voided_rejected    # Void tx; POST void again → 404
test_correct_form_prefills_original  # GET /transactions/{id}/correct → 200, original amount in response
test_correct_creates_new_voids_original  # POST valid correction → 302; db: original voided, new active, replacement_transaction_id set
test_correct_on_voided_rejected      # Void tx; GET /transactions/{id}/correct → 404
```

**Total after I4:** 61 + 10 + 10 = **81 passed**

---

## Void Validation Rules

| Rule | Behaviour |
|------|-----------|
| Transaction must exist | `get_transaction` returns None → 404 (route level) |
| Transaction must be active | `is_active = FALSE` → 404 (route level for GET; ValueError from service for POST) |
| `void_reason` non-empty | Empty or whitespace-only → ValueError from `void_transaction`; re-render void.html with error, status 422 |
| `voided_by` | Always `user["id"]` from session — never from form data |

---

## Acceptance Checklist

```bash
python -c "from app.services.transaction_service import get_transaction, void_transaction; print('ok')"
python -c "from app.routes.transactions import router; print('ok')"
pytest -v
# Expected: 81 passed, 0 failed
ruff check .
# Expected: clean
```

- Voided row: `is_active=0`, non-empty `void_reason`, `voided_by` = acting user's id
- Correction: new transaction exists and is active; original has `is_active=0`, `void_reason='Corrected'`, `replacement_transaction_id` = new id
- Voided transactions never appear in `GET /transactions/` (already filtered by `WHERE is_active = TRUE`)
- `void_reason` empty → 422, void.html re-rendered with error
- `voided_by` never read from form data
- No hard deletes anywhere

---

## Agent Rules

1. Read this file first.
2. Read your task prompt file: `iterations/p1-i4/prompts/t[N]-[name].md`
3. Update status to IN PROGRESS before writing any code.
4. Check dependencies — never start if dep is not ✅ DONE.
5. Verify acceptance checklist before requesting review.
6. After PR is merged: update `tasks.md` status → ✅ DONE with one-line note.
7. No `except: pass`, no stored derived values, no `voided_by` from form data.

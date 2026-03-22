# I5-T5 — Flash Messages + Tests

**Branch:** `feature/p1-i5/t5-flash-tests` (from `feature/phase-1/iteration-5`)
**PR target:** `feature/phase-1/iteration-5`
**Depends on:** I5-T4 ✅ DONE

---

## Goal

Add session-based flash messages for success feedback after every major action. Add tests to verify flash behavior. No extra dependencies — pure session + Jinja2.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i5/prompt.md
app/routes/transactions.py
app/main.py
app/templates/base.html          (flash rendering block from T1)
tests/test_transactions.py
```

---

## Allowed Files

```
app/routes/transactions.py     ← modify (add flash on success)
app/main.py                    ← modify (if flash middleware needed)
app/templates/base.html        ← modify (if flash rendering needs adjustment)
tests/test_transactions.py     ← extend (+4 tests)
iterations/p1-i5/tasks.md     ← status update
```

Do NOT modify validation.py, calculations.py, transaction_service.py, or any other service file.

---

## What to Implement

### 1. Flash message pattern

Store flash in session before redirect:
```python
request.session["flash"] = {"type": "success", "message": "Transaction saved successfully."}
```

The flash rendering in `base.html` (added by T1) renders from template context:
```html
{% if flash %}
<div class="flash flash-{{ flash.type }}">{{ flash.message }}</div>
{% endif %}
```

T1 implements a middleware or context processor that pops `request.session["flash"]` in Python and passes it to the template context. The key contract is: set before redirect, popped and rendered on next request. If T1's mechanism differs slightly, adjust to match — but the pop must happen in Python, not in Jinja2.

### 2. Add flash messages to routes

**`app/routes/transactions.py`:**

After successful create (POST /transactions/new):
```python
request.session["flash"] = {"type": "success", "message": "Transaction saved successfully."}
return RedirectResponse("/transactions/", status_code=302)
```

After successful void (POST /transactions/{id}/void):
```python
request.session["flash"] = {"type": "success", "message": "Transaction voided."}
return RedirectResponse("/transactions/", status_code=302)
```

After successful correct (POST /transactions/{id}/correct):
```python
request.session["flash"] = {"type": "success", "message": "Transaction corrected. Original has been voided."}
return RedirectResponse("/transactions/", status_code=302)
```

### 3. Add tests

Add to `tests/test_transactions.py`:

```python
def test_flash_after_create(client):
    """POST create → redirect → GET list → flash message in response."""
    r = client.post("/transactions/new", data=valid_income_form())
    assert r.status_code == 302

    list_r = client.get("/transactions/")
    assert "Transaction saved successfully." in list_r.text


def test_flash_after_void(client):
    """POST void → redirect → GET list → flash message in response."""
    transaction_id = insert_transaction(client)
    r = client.post(
        f"/transactions/{transaction_id}/void",
        data={"void_reason": "Test void"},
    )
    assert r.status_code == 302

    list_r = client.get("/transactions/")
    assert "Transaction voided." in list_r.text


def test_flash_after_correct(client):
    """POST correct → redirect → GET list → flash message in response."""
    transaction_id = insert_transaction(client)
    r = client.post(
        f"/transactions/{transaction_id}/correct",
        data=valid_expense_form(description="Corrected"),
    )
    assert r.status_code == 302

    list_r = client.get("/transactions/")
    assert "Transaction corrected." in list_r.text


def test_flash_clears_after_display(client):
    """Flash message appears once, then disappears on next load."""
    client.post("/transactions/new", data=valid_income_form())

    first_load = client.get("/transactions/")
    assert "Transaction saved successfully." in first_load.text

    second_load = client.get("/transactions/")
    assert "Transaction saved successfully." not in second_load.text
```

### 4. Closure steps

```bash
pytest -v
# Expected: 98 passed (94 existing + 4 new)
ruff check .
# Expected: clean
```

Update `iterations/p1-i5/tasks.md`: I5-T5 → ✅ DONE.

---

## Acceptance Check

- [ ] Flash message appears after create → redirects to list
- [ ] Flash message appears after void → redirects to list
- [ ] Flash message appears after correct → redirects to list
- [ ] Flash clears after being displayed once (does not persist)
- [ ] All 98 tests pass
- [ ] ruff clean

# I3-T2 — Transaction Routes

**Owner:** Claude Code
**Branch:** `feature/p1-i3/t2-routes` (from `feature/phase-1/iteration-3`)
**PR target:** `feature/phase-1/iteration-3`
**Depends on:** I3-T1 ✅ DONE (validation.py + calculations.py must be importable)

---

## Goal

Implement the four transaction route handlers. Wire them to `validate_transaction` and `calculations.py`. Register the router in `app/main.py`.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i3/prompt.md          ← full spec; read Route Logic, Data Normalisation, and What to Build sections
skills/cash-flow/transaction_validator/SKILL.md
skills/cash-flow/error_handling/SKILL.md
```

---

## Allowed Files

```
app/routes/transactions.py    ← create new
app/main.py                   ← add router registration only; no other changes
```

Do NOT modify any other file. Do NOT create templates.

---

## What to Implement

### Routes

```
GET  /transactions/new     → render create.html (categories loaded for dropdown)
POST /transactions/new     → normalise → validate → save or re-render with errors (422)
GET  /transactions/        → last 20 active transactions + derived fields
GET  /categories           → JSON list of all categories with defaults
```

### Data normalisation (before calling validate_transaction)

```python
# Applied to raw Form data before passing to validate_transaction:
# 1. Strip whitespace from all string fields
# 2. Empty string → None for: income_type, description
# 3. Cast:
#    category_id: int(raw) if raw else None
#    amount:      Decimal(str(raw_amount.strip())) if raw else None
#    vat_rate:    float(raw_vat_rate) if raw else None
#    vat_deductible_pct: float(raw) if raw not in (None, '') else None
# 4. Set logged_by = user["id"]   ← from session, NEVER from form input
# 5. Set is_active = True
```

### POST /transactions/new — exact sequence

```python
# 1. user = require_auth(request)
# 2. Read form fields with Form(default="") or Form(default=None)
# 3. Normalise (see above)
# 4. errors = validate_transaction(data, db)
# 5. if errors:
#       re-fetch categories for dropdown
#       return TemplateResponse("transactions/create.html",
#           {"request": request, "categories": cats, "errors": errors, "form_data": data},
#           status_code=422)
# 6. if valid:
#       db.execute(
#           "INSERT INTO transactions (date, amount, direction, category_id, payment_method, "
#           "vat_rate, income_type, vat_deductible_pct, description, logged_by) "
#           "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
#           (data["date"], str(data["amount"]), data["direction"], data["category_id"],
#            data["payment_method"], data["vat_rate"], data["income_type"],
#            data["vat_deductible_pct"], data["description"], data["logged_by"])
#       )
#       db.commit()
#       return RedirectResponse(url="/transactions/", status_code=302)
```

### GET /transactions/ — SQL and derived fields

```sql
SELECT t.*, c.label AS category_label, u.username AS logged_by_username
FROM transactions t
JOIN categories c ON t.category_id = c.category_id
JOIN users u ON t.logged_by = u.id
WHERE t.is_active = TRUE
ORDER BY t.created_at DESC
LIMIT 20
```

After fetching, compute derived fields per row:
```python
from app.services.calculations import vat_amount, effective_cost
from decimal import Decimal

# For each row:
gross = Decimal(str(row["amount"]))
va = vat_amount(gross, row["vat_rate"])
ec = effective_cost(gross, row["vat_rate"], row["vat_deductible_pct"]) if row["direction"] == "expense" else None
```

Pass `transactions` list (each with `va` and `ec` attached as extra fields) to the template.

### GET /categories — exact JSON response structure

```python
return JSONResponse([
    {
        "category_id": row["category_id"],
        "name": row["name"],                              # internal code e.g. "petrol"
        "label": row["label"],                            # display name
        "direction": row["direction"],                    # "income" or "expense"
        "default_vat_rate": row["default_vat_rate"],
        "default_vat_deductible_pct": row["default_vat_deductible_pct"],  # float or null
    }
    for row in db.execute(
        "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
        "FROM categories ORDER BY direction, label"
    ).fetchall()
])
# AuthGate already protects this route — no special auth handling needed here
```

### app/main.py — registration only

```python
from app.routes.transactions import router as transactions_router
app.include_router(transactions_router)
```

No other changes to main.py.

---

## Acceptance Check (independent of T3 template)

```bash
python -c "from app.routes.transactions import router; print('router imports ok')"
```

Note: End-to-end HTTP tests (GET /transactions/new returns 200) require T3's template and are covered by T5 tests. T2 acceptance is import-only.

---

## Done

- Router imports without error
- `app/main.py` registers transactions router
- Ruff clean
- PR open → `feature/phase-1/iteration-3`
- Update `iterations/p1-i3/tasks.md`: I3-T2 status → ✅ DONE with one-line note

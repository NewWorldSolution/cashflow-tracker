# I3-T1 — Service Layer: Validation + Calculations

**Owner:** Codex
**Branch:** `feature/p1-i3/t1-services` (from `feature/phase-1/iteration-3`)
**PR target:** `feature/phase-1/iteration-3`
**Depends on:** nothing — first task

---

## Goal

Implement the pure service layer for transaction validation and VAT calculations. No routes, no templates. Business logic only. Every rule that governs what a valid transaction looks like lives here and only here.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i3/prompt.md          ← full iteration spec; read the Validation Rules, VAT Calculations, and Data Normalisation sections
skills/cash-flow/transaction_validator/SKILL.md
skills/cash-flow/schema/SKILL.md
docs/architecture.md                 ← canonical VAT formulas (section "Derived Calculations")
```

---

## Allowed Files

```
app/services/validation.py      ← create new
app/services/calculations.py   ← create new
app/services/__init__.py        ← check if exists; create empty package marker only if missing
```

Do NOT modify any other file.

---

## What to Implement

### app/services/validation.py

```python
def validate_transaction(data: dict, db: sqlite3.Connection) -> list[str]:
```

**Contract:**
- `data` contains stripped strings with empty optional fields normalised to `None`
- user-entered numeric/date fields may still be strings at validation time; this function must validate conversion safely
- `db` is the live connection from the route handler — do not open a new connection
- Returns a list of error strings (human-readable). Empty list = transaction is valid.
- Never raises — catch conversion/type issues and add them to the error list
- Collect ALL errors before returning — do not stop at the first failure

**15 validation rules to enforce:**

| # | Rule |
|---|------|
| 1 | `date` required; parseable as YYYY-MM-DD |
| 2 | `direction` must be `'income'` or `'expense'` |
| 3 | `amount` must be positive `Decimal` (> 0); reject zero, negative, non-numeric |
| 4 | `category_id` must be a valid integer FK in `categories` table |
| 5 | Category `direction` must match transaction `direction` |
| 6 | `payment_method` must be `'cash'`, `'card'`, or `'transfer'` |
| 7 | `vat_rate` must be in `(0, 5, 8, 23)` |
| 8 | `income_type = 'internal'` → `vat_rate` MUST be 0 (hard rule — reject any other value) |
| 9 | `income_type` required when `direction = 'income'` (None rejected) |
| 10 | `income_type` must be None when `direction = 'expense'` |
| 11 | `vat_deductible_pct` required when `direction = 'expense'` (None rejected) |
| 12 | `vat_deductible_pct` must be None when `direction = 'income'` |
| 13 | `vat_deductible_pct` must be in `(0, 50, 100)` if present |
| 14 | `description` required (non-empty string) when category `name` is `'other_expense'` or `'other_income'` |
| 15 | `logged_by` must be a valid integer FK in `users` table |

**Important — category VAT default is a suggestion, not a constraint:**
- A user may select a category with `default_vat_rate=23` and submit `vat_rate=5` — this is valid.
- Do NOT add a rule that `vat_rate` must match category default.
- The only VAT override restriction is rule 8 (internal income → must be 0).

**SQL lookups required (parameterised — never string interpolation):**
```sql
-- Rule 4 + 5:
SELECT category_id, direction, name FROM categories WHERE category_id = ?

-- Rule 14 (category name check):
-- Use the row already fetched for rules 4/5 — do not query twice

-- Rule 15:
SELECT id FROM users WHERE id = ?
```

### app/services/calculations.py

Four pure functions. No database access.

```python
from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal('0.01')

def vat_amount(gross: Decimal, vat_rate: float) -> Decimal:
    # gross - (gross / (1 + vat_rate/100))
    # From architecture.md — use this exact formula

def net_amount(gross: Decimal, vat_rate: float) -> Decimal:
    # gross - vat_amount(gross, vat_rate)

def vat_reclaimable(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal:
    # vat_amount(gross, vat_rate) * vat_deductible_pct / 100

def effective_cost(gross: Decimal, vat_rate: float, vat_deductible_pct: float) -> Decimal:
    # net_amount + (vat_amount * (1 - vat_deductible_pct / 100))
    # This is the canonical formula from architecture.md — do not use the shorthand
```

**Decimal rules:**
- All arithmetic in `Decimal` — never `float`
- Input conversion: `Decimal(str(value))` — **NEVER** `Decimal(float(value))`
- All results: `.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)`

---

## Security Rules

- Parameterised queries only — never string interpolation in SQL
- No `except: pass` — if an exception needs catching, log the specific error to the return list
- No LLM calls anywhere in this layer

---

## Acceptance Check

```bash
python -c "
from app.services.validation import validate_transaction
from app.services.calculations import vat_amount, net_amount, vat_reclaimable, effective_cost
print('imports ok')
"
```

```bash
ruff check app/services/validation.py app/services/calculations.py
# Expected: clean
```

---

## Done

- Both files importable, all exports present
- Ruff clean
- PR open → `feature/phase-1/iteration-3`
- Update `iterations/p1-i3/tasks.md`: I3-T1 status → ✅ DONE with one-line note

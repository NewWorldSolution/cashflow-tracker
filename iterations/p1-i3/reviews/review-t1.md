# Review — I3-T1: Service Layer (Validation + Calculations)
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i3/t1-services`
**PR target:** `feature/phase-1/iteration-3`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Your job is to verify it exactly matches the spec. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/services/validation.py     ← validate_transaction(data, db) → list[str]
app/services/calculations.py   ← vat_amount, net_amount, vat_reclaimable, effective_cost
app/services/__init__.py        ← empty package marker (only if it did not exist)
```

### Required behaviour

| Item | Requirement |
|------|-------------|
| `validate_transaction` | Returns `list[str]`. Empty = valid. Never raises. |
| `validate_transaction` | Collects ALL errors before returning — no early exit on first error |
| `validate_transaction` | Accepts string inputs — handles conversion errors internally |
| `validate_transaction` | Receives live `db` — never opens a new connection |
| `vat_amount` | `gross - (gross / (1 + vat_rate/100))` — canonical formula from architecture.md |
| `effective_cost` | `net_amount + (vat_amount * (1 - vat_deductible_pct/100))` — canonical, not shorthand |
| All calculations | `Decimal` arithmetic; `Decimal(str(x))` for input; `ROUND_HALF_UP` to 2dp |
| `calculations.py` | No database access — pure math only |

---

## Architecture principles to check

| # | Principle | Check |
|---|-----------|-------|
| 2 | No LLM calls | grep |
| 5 | No silent failures — no `except: pass` | grep |
| 7 | Derived values never stored — these functions compute only, no writes | read code |
| 8 | All 15 validation rules in service layer only | read code |

---

## Review steps

### Step 1 — Checkout

```bash
git fetch origin
git checkout feature/p1-i3/t1-services
```

### Step 2 — Scope check

```bash
git diff --name-only feature/phase-1/iteration-3
# Expected: app/services/validation.py, app/services/calculations.py
# app/services/__init__.py acceptable only if it did not already exist
# Any other file = scope violation
```

### Step 3 — Import check

```bash
python -c "
from app.services.validation import validate_transaction
from app.services.calculations import vat_amount, net_amount, vat_reclaimable, effective_cost
print('all imports ok')
"
```

### Step 4 — Ruff

```bash
ruff check app/services/validation.py app/services/calculations.py
# Expected: clean
```

### Step 5 — No SQL injection

```bash
grep -n "f\".*SELECT\|f'.*SELECT\|%.*SELECT\|\.format.*SELECT" app/services/validation.py
# Expected: no output — parameterised queries only
```

### Step 6 — No new DB connection inside validate_transaction

```bash
grep -n "_connect\|sqlite3.connect\|get_db" app/services/validation.py
# Expected: no output — db received as parameter, never opened inside
```

### Step 7 — All 15 rules present

Read `validate_transaction` in full. Mark each rule PRESENT or MISSING:

```
1.  date required + YYYY-MM-DD parseable
2.  direction in ('income', 'expense')
3.  amount positive Decimal — rejects zero, negative, non-numeric
4.  category_id valid FK in categories table (parameterised lookup)
5.  category direction matches transaction direction
6.  payment_method in ('cash', 'card', 'transfer')
7.  vat_rate in (0, 5, 8, 23)
8.  income_type='internal' → vat_rate must be 0
9.  income_type required when direction='income' (None rejected)
10. income_type must be None when direction='expense'
11. vat_deductible_pct required when direction='expense' (None rejected)
12. vat_deductible_pct must be None when direction='income'
13. vat_deductible_pct in (0, 50, 100) if present
14. description required (non-empty) when category name is other_expense or other_income
15. logged_by valid integer FK in users table (parameterised lookup)
```

Any MISSING rule = `CHANGES REQUIRED`.

### Step 8 — All errors collected before return (no early exit)

Read `validate_transaction`. Verify errors accumulate in a list throughout and the full list is returned at the end. A single `return [error_message]` on any failure (except possibly a fatal unparseable state) is a problem.

```bash
# Count early returns that contain a single error — should be 0
grep -n "return \[\"" app/services/validation.py
# This pattern suggests returning on first error — investigate each hit
```

### Step 9 — Category VAT default NOT validated against submitted vat_rate

```bash
grep -n "default_vat_rate" app/services/validation.py
# Expected: no output
# The category default is a UI suggestion — validate_transaction must NOT check
# whether the submitted vat_rate matches the category default.
# Rule 8 (internal income → vat_rate must be 0) is the only VAT restriction.
```

### Step 10 — Canonical formulas in calculations.py

Read each function. Verify exact formula:

```bash
# vat_amount must use: gross - (gross / (1 + vat_rate/100))
# NOT: gross * vat_rate / (100 + vat_rate)  ← equivalent but not canonical
grep -n "def vat_amount" app/services/calculations.py
```

```bash
# effective_cost must use: net_amount + (vat_amount * (1 - vat_deductible_pct/100))
# NOT: gross - vat_reclaimable  ← shorthand, not canonical
grep -n "def effective_cost" app/services/calculations.py
```

### Step 11 — Decimal rules in calculations.py

```bash
grep -n "Decimal(str\|ROUND_HALF_UP\|quantize\|TWO_PLACES\|0\.01" app/services/calculations.py
# Must find Decimal(str(...)), ROUND_HALF_UP, and quantize to 0.01
```

```bash
grep -n "Decimal(float" app/services/calculations.py
# Expected: no output — Decimal(float(x)) introduces floating point error
```

### Step 12 — No DB access in calculations.py

```bash
grep -n "sqlite\|execute\|SELECT\|INSERT\|conn\|db\." app/services/calculations.py
# Expected: no output — pure math functions only
```

### Step 13 — No LLM calls

```bash
grep -rn "anthropic\|openai\|claude\|llm" app/services/validation.py app/services/calculations.py
# Expected: no output
```

### Step 14 — No silent failures

```bash
grep -n "except.*pass\|except:$" app/services/validation.py app/services/calculations.py
# Expected: no output
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every item implemented correctly with file and line references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `app/services/validation.py`, `app/services/calculations.py`, `app/services/__init__.py`.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] validate_transaction and all 4 calculation functions importable
- [PASS|FAIL] validate_transaction returns list[str]; empty = valid; never raises
- [PASS|FAIL] All 15 validation rules implemented (list any missing)
- [PASS|FAIL] All errors collected before return — no early exit on first error
- [PASS|FAIL] No SQL string interpolation — parameterised queries only
- [PASS|FAIL] No new db connection opened inside validate_transaction
- [PASS|FAIL] Category VAT default NOT checked against submitted vat_rate
- [PASS|FAIL] vat_amount uses canonical formula: gross - (gross / (1 + vat_rate/100))
- [PASS|FAIL] effective_cost uses canonical formula: net_amount + (vat_amount * (1 - deductible_pct/100))
- [PASS|FAIL] All Decimal input via Decimal(str(x)) — never Decimal(float(x))
- [PASS|FAIL] All results quantized to 2dp with ROUND_HALF_UP
- [PASS|FAIL] calculations.py has no DB access
- [PASS|FAIL] No except: pass or silent failures
- [PASS|FAIL] Ruff clean
- [PASS|FAIL] Scope: only allowed files modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

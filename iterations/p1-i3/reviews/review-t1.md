# Review — I3-T1: Service Layer
**Reviewer:** Claude Code
**Implemented by:** Codex
**Branch:** `feature/p1-i3/t1-services`
**PR target:** `feature/phase-1/iteration-3`

---

## Reviewer Role

You are an independent code reviewer. You did not write this code. Report problems precisely — file, line number, exact issue, why it matters. Do not fix. Do not approve based on tests alone.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

### Files

```
app/services/validation.py
app/services/calculations.py
app/services/__init__.py   ← only if missing; empty package marker
```

### Required behaviour

- `validate_transaction(data, db) -> list[str]`
- all 15 validation rules enforced in the service layer
- parameterised DB lookups only
- no new DB connection inside validation
- four pure Decimal-based calculation functions

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
# Expected: app/services/validation.py, app/services/calculations.py, optionally app/services/__init__.py only
```

### Step 3 — Imports

```bash
python -c "
from app.services.validation import validate_transaction
from app.services.calculations import vat_amount, net_amount, vat_reclaimable, effective_cost
print('imports ok')
"
```

### Step 4 — No SQL interpolation

```bash
grep -n "f\".*SELECT\|f'.*SELECT\|%.*SELECT\|format.*SELECT" app/services/validation.py
# Expected: no output
```

### Step 5 — Validation service contract

Read `validate_transaction` and verify:
- returns `list[str]`
- handles conversion/type problems without raising
- collects multiple errors
- checks category and user existence with parameterised queries
- does not open a new connection

### Step 6 — Calculation rules

```bash
grep -n "Decimal(str\|ROUND_HALF_UP\|quantize" app/services/calculations.py
```

Verify all arithmetic is Decimal-based and all outputs are quantized.

### Step 7 — No DB access in calculations

```bash
grep -n "sqlite\|execute\|SELECT\|INSERT\|UPDATE\|DELETE" app/services/calculations.py
# Expected: no output
```

### Step 8 — Ruff

```bash
ruff check app/services/validation.py app/services/calculations.py
# Expected: clean
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

Files modified outside the allowed service files.

If none: `None.`

### 5. Acceptance Criteria Check

```
- [PASS|FAIL] validation.py and calculations.py import without error
- [PASS|FAIL] validate_transaction enforces all 15 rules and returns list[str]
- [PASS|FAIL] validate_transaction handles conversion/type errors without raising
- [PASS|FAIL] validate_transaction uses parameterised queries only
- [PASS|FAIL] validate_transaction collects multiple errors
- [PASS|FAIL] calculations.py uses Decimal arithmetic with ROUND_HALF_UP quantization
- [PASS|FAIL] calculations.py has no DB access
- [PASS|FAIL] Ruff clean
- [PASS|FAIL] Scope: only allowed service files modified
```

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

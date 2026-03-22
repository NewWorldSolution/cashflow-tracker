# I4-T4 — Tests + Close

**Owner:** Codex  
**Branch:** `feature/p1-i4/t4-tests` (from `feature/phase-1/iteration-4`)  
**PR target:** `feature/phase-1/iteration-4`  
**Depends on:** I4-T3 ✅ DONE

---

## Goal

Add the calculation and void/correct regression tests, verify the iteration is green, and close the task board.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i4/prompt.md
iterations/p1-i4/prompts/t2-routes.md
iterations/p1-i4/prompts/t3-templates.md
tests/test_transactions.py
app/services/calculations.py
```

---

## Allowed Files

```
tests/test_calculations.py
tests/test_transactions.py
iterations/p1-i4/tasks.md
```

Do NOT modify any other file.

---

## Tests to Add

- `tests/test_calculations.py`: 10 direct unit tests for `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost`
- `tests/test_transactions.py`: add 10 void/correct route tests using the existing `client` fixture

### Route coverage required

```text
test_detail_view_returns_200
test_detail_view_404_for_missing
test_void_form_loads
test_void_requires_void_reason
test_void_success
test_voided_transaction_excluded_from_list
test_void_already_voided_rejected
test_correct_form_prefills_original
test_correct_creates_new_voids_original
test_correct_on_voided_rejected
```

Total expected after completion: **81 passed**.

---

## Closure Steps

```bash
pytest -v
ruff check .
git diff --name-only feature/phase-1/iteration-4
gh pr create --base feature/phase-1/iteration-4
```

- Update `iterations/p1-i4/tasks.md`:
  - I4-T4 → `✅ DONE`
  - iteration status → `✔ COMPLETE`

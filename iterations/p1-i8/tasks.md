# P1-I8 — Hierarchical Categories + Manual VAT + Procedure Metadata
## Task Board

**Status:** ✔ COMPLETE
**Last updated:** 2026-03-24
**Iteration branch:** `feature/phase-1/iteration-8` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-8` → `main` ← QA agent approves before merge

---

## Goal

Replace the flat 22-category testing structure with a real two-level business taxonomy (19 parent groups, 62 subcategories), rename direction from income/expense to cash_in/cash_out, add manual VAT mode for mixed-rate invoices, and introduce procedure metadata (customer_type, document_flow, for_accountant default change).

After I8:
- direction uses `cash_in` / `cash_out` throughout
- `income_type` renamed to `cash_in_type`
- create/correct forms use a two-level category picker
- transactions can use either automatic or manual VAT mode
- every transaction has `customer_type` (private/company/other)
- external cash_in requires `document_flow`; cash_out has it optional
- `for_accountant` defaults to true (except internal cash_in)
- list/detail/dashboard show category paths, manual VAT indicator, and metadata

---

## Dependency Map

```text
T1 (direction rename + schema foundations)
  └── T2 (category seed + hierarchy + i18n)
        └── T3 (validation + services)
              └── T4 (category picker UI)
                    └── T5 (VAT mode UI)
                          └── T6 (procedure metadata UI)
                                └── T7 (list/detail/dashboard display)
                                      └── T8 (tests)
```

All tasks are sequential. Each depends on the previous.

---

## Tasks

| ID    | Title                                          | Owner | Status     | Depends on | Branch |
|-------|------------------------------------------------|-------|------------|------------|--------|
| I8-T1 | Direction rename + schema foundations          | —     | ✅ DONE    | —          | `feature/p1-i8/t1-direction-schema` |
| I8-T2 | Category seed + hierarchy + i18n               | —     | ✅ DONE    | I8-T1      | `feature/p1-i8/t2-category-seed` |
| I8-T3 | Validation + services                          | —     | ✅ DONE    | I8-T2      | `feature/p1-i8/t3-validation-services` |
| I8-T4 | Category picker UI                             | —     | ✅ DONE    | I8-T3      | `feature/p1-i8/t4-category-picker` |
| I8-T5 | VAT mode UI                                    | —     | ✅ DONE    | I8-T4      | `feature/p1-i8/t5-vat-mode-ui` |
| I8-T6 | Procedure metadata UI                          | —     | ✅ DONE    | I8-T5      | `feature/p1-i8/t6-procedure-metadata` |
| I8-T7 | List/detail/dashboard display                  | —     | ✅ DONE    | I8-T6      | `feature/p1-i8/t7-display` |
| I8-T8 | Tests                                          | —     | ✅ DONE    | I8-T7      | `feature/p1-i8/t8-tests` |

---

## Important Notes

- **Fresh start on categories** — old 22 test categories are dropped entirely, no migration needed
- **Direction rename is foundational** — must happen in T1 before anything else
- **`income_type` → `cash_in_type`** — column rename, values stay `internal`/`external`
- **`vat_rate` becomes nullable** — NULL when `vat_mode = manual`
- **No VAT inheritance** — leaf rows are the source of truth for VAT defaults
- **Only leaf categories are selectable** — parent rows are for grouping/reporting only
- **`customer_type` is required on ALL transactions** — `private`/`company`/`other`
- **Internal cash_in forces:** VAT 0, cash, for_accountant=false, customer_type=private (hidden), document_flow hidden, vat_mode=automatic
- **`document_flow`:** required for external cash_in (default `receipt`), optional for cash_out, hidden for internal
- **`invoice_and_receipt` only when `customer_type = private`** — cross-field validation
- **`for_accountant` defaults to true** — except internal cash_in which forces false
- **Correction preserves stored values** — does not re-apply defaults
- **All new labels must have EN + PL translations**
- **Default locale is `pl`** — Polish is the default, English is fallback

---

## Reference Documents

- `iterations/p1-i8/scope-decisions.md` — all locked decisions
- `iterations/p1-i8/category-taxonomy.md` — full taxonomy with slugs and VAT defaults

---

## Prompts & Reviews

| Task  | Implementation prompt | Review prompt | Reviewer |
|-------|-----------------------|---------------|----------|
| I8-T1 | `iterations/p1-i8/prompts/t1-direction-schema.md` | `iterations/p1-i8/reviews/review-t1.md` | — |
| I8-T2 | `iterations/p1-i8/prompts/t2-category-seed.md` | `iterations/p1-i8/reviews/review-t2.md` | — |
| I8-T3 | `iterations/p1-i8/prompts/t3-validation-services.md` | `iterations/p1-i8/reviews/review-t3.md` | — |
| I8-T4 | `iterations/p1-i8/prompts/t4-category-picker.md` | `iterations/p1-i8/reviews/review-t4.md` | — |
| I8-T5 | `iterations/p1-i8/prompts/t5-vat-mode-ui.md` | `iterations/p1-i8/reviews/review-t5.md` | — |
| I8-T6 | `iterations/p1-i8/prompts/t6-procedure-metadata.md` | `iterations/p1-i8/reviews/review-t6.md` | — |
| I8-T7 | `iterations/p1-i8/prompts/t7-display.md` | `iterations/p1-i8/reviews/review-t7.md` | — |
| I8-T8 | `iterations/p1-i8/prompts/t8-tests.md` | `iterations/p1-i8/reviews/review-t8.md` | — |
| —     | — | `iterations/p1-i8/reviews/review-iteration.md` | — (QA) |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-8` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

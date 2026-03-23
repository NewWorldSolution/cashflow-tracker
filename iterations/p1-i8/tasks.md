# P1-I8 — Sub-Categories (Hierarchical Category System)
## Task Board

**Status:** NOT STARTED
**Last updated:** 2026-03-23
**Iteration branch:** `feature/phase-1/iteration-8` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-8` → `main` ← QA agent approves before merge

---

## Goal

Introduce a two-level category system (parent + sub-category) so transactions can be classified more precisely. The initial implementation builds the structure and UI — the final real taxonomy will come from user testing feedback later.

---

## Planned Work

| # | Area | Description |
|---|------|-------------|
| 1 | Schema | Redesign categories table with `parent_id` for hierarchy |
| 2 | Migration | Migration path from current flat 22 categories to hierarchical structure |
| 3 | Seed | Update seed with placeholder/demo parent-child hierarchy |
| 4 | Queries | Update category queries/services to handle hierarchical categories |
| 5 | UI | Build two-level category picker in create/correct forms |
| 6 | Validation | Enforce that only leaf categories can be selected (if decided) |
| 7 | Display | Update list/detail rendering for category path display |
| 8 | i18n | Add/update EN/PL translations for new category keys |
| 9 | Tests | Hierarchy selection, validation, and migration tests |

---

## Tasks

| ID    | Title                              | Owner | Status     | Depends on | Branch |
|-------|------------------------------------|-------|------------|------------|--------|
| I8-T1 | Schema + migration + seed          | —     | ⏳ WAITING | —          | `feature/p1-i8/t1-category-schema` |
| I8-T2 | Services + validation              | —     | ⏳ WAITING | I8-T1      | `feature/p1-i8/t2-category-services` |
| I8-T3 | Two-level category picker UI       | —     | ⏳ WAITING | I8-T2      | `feature/p1-i8/t3-category-picker` |
| I8-T4 | List/detail category path display  | —     | ⏳ WAITING | I8-T3      | `feature/p1-i8/t4-category-display` |
| I8-T5 | Tests                              | —     | ⏳ WAITING | I8-T4      | `feature/p1-i8/t5-tests` |

---

## Important Notes

- **Real taxonomy deferred** — the first implementation uses placeholder/demo sub-categories. The actual business taxonomy will be defined from user testing feedback. Current work is structure/template, not final data.
- **Parent categories may or may not be selectable** — design decision to be made during task breakdown (likely only leaf nodes are selectable)
- **Backward compatibility** — existing transactions must remain valid after migration. Current flat categories become either parents or standalone categories.
- **Category i18n** — all new parent/sub-category labels must have EN + PL translations via the `t('category_' + name)` pattern established in I6-T6
- **No changes to VAT defaults logic** — sub-categories inherit or override parent defaults (design decision in T1)

---

## Prompts & Reviews

| Task  | Implementation prompt | Review prompt | Reviewer |
|-------|-----------------------|---------------|----------|
| I8-T1 | `iterations/p1-i8/prompts/t1-category-schema.md` | `iterations/p1-i8/reviews/review-t1.md` | — |
| I8-T2 | `iterations/p1-i8/prompts/t2-category-services.md` | `iterations/p1-i8/reviews/review-t2.md` | — |
| I8-T3 | `iterations/p1-i8/prompts/t3-category-picker.md` | `iterations/p1-i8/reviews/review-t3.md` | — |
| I8-T4 | `iterations/p1-i8/prompts/t4-category-display.md` | `iterations/p1-i8/reviews/review-t4.md` | — |
| I8-T5 | `iterations/p1-i8/prompts/t5-tests.md` | `iterations/p1-i8/reviews/review-t5.md` | — |
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

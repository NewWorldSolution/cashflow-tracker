# P1-I7 — Multi-Company Support + Accountant Flag
## Task Board

**Status:** NOT STARTED
**Last updated:** 2026-03-23
**Iteration branch:** `feature/phase-1/iteration-7` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-7` → `main` ← QA agent approves before merge

---

## Goal

Support multiple legal/business entities inside one app so transactions, views, and summaries can be separated by company. Also add the `for_accountant` flag to mark transactions that need accountant attention.

### Companies to seed
- **JDG** — sole proprietorship
- **LTD** — limited company
- **Foundation** — foundation entity
- **Private** — personal/non-business

---

## Dependency Map

```
I7-T1 (companies table + schema)
  └── I7-T2 (transaction create/correct with company)
        └── I7-T3 (list/detail/dashboard company display + filtering)
I7-T4 (for_accountant flag) — independent, can run in parallel with T1–T3
I7-T5 (tests) — depends on T1–T4
```

---

## Planned Work

| # | Area | Description |
|---|------|-------------|
| 1 | Schema | Add `companies` table (`id`, `name`, `slug`, `is_active`) |
| 2 | Schema | Add `company_id` FK to `transactions` table |
| 3 | Seed | Seed 4 initial companies: JDG, LTD, Foundation, Private |
| 4 | Migration | Backfill existing transactions to a default company |
| 5 | Create flow | Add company selector to transaction create form |
| 6 | Correct flow | Preserve or allow selecting company during correction |
| 7 | Detail | Show company in transaction detail view |
| 8 | List | Add company display in transaction list |
| 9 | Filtering | Add company filter in list/dashboard views |
| 10 | Dashboard | Company-specific summary support |
| 11 | for_accountant | Add boolean `for_accountant` field on transactions |
| 12 | for_accountant | Create/correct form support for the flag |
| 13 | for_accountant | Display in detail/list as appropriate |
| 14 | i18n | Add EN/PL translations for company names, labels, and for_accountant UI |
| 15 | Tests | Company create/list/detail/filter flows |
| 16 | Tests | for_accountant field tests |

---

## Tasks

| ID    | Title                              | Owner | Status     | Depends on | Branch |
|-------|------------------------------------|-------|------------|------------|--------|
| I7-T1 | Companies schema + seed + migration | —    | ⏳ WAITING | —          | `feature/p1-i7/t1-companies-schema` |
| I7-T2 | Create/correct with company        | —     | ⏳ WAITING | I7-T1      | `feature/p1-i7/t2-company-create` |
| I7-T3 | List/detail/dashboard + filtering  | —     | ⏳ WAITING | I7-T2      | `feature/p1-i7/t3-company-views` |
| I7-T4 | for_accountant flag                | —     | ⏳ WAITING | —          | `feature/p1-i7/t4-accountant-flag` |
| I7-T5 | Tests                              | —     | ⏳ WAITING | I7-T3, I7-T4 | `feature/p1-i7/t5-tests` |

---

## Important Notes

- **Auth model unchanged** — current session-based auth stays as-is
- **Company is mandatory on all new transactions** — no null company_id after migration
- **Existing transactions backfilled** to a default company (likely JDG)
- **`for_accountant` exact UX/reporting behavior** to be defined during task breakdown
- **`for_accountant` is a simple boolean** — no complex workflow in this iteration
- **All company/accountant labels must have EN + PL translations**

---

## Prompts & Reviews

| Task  | Implementation prompt | Review prompt | Reviewer |
|-------|-----------------------|---------------|----------|
| I7-T1 | `iterations/p1-i7/prompts/t1-companies-schema.md` | `iterations/p1-i7/reviews/review-t1.md` | — |
| I7-T2 | `iterations/p1-i7/prompts/t2-company-create.md` | `iterations/p1-i7/reviews/review-t2.md` | — |
| I7-T3 | `iterations/p1-i7/prompts/t3-company-views.md` | `iterations/p1-i7/reviews/review-t3.md` | — |
| I7-T4 | `iterations/p1-i7/prompts/t4-accountant-flag.md` | `iterations/p1-i7/reviews/review-t4.md` | — |
| I7-T5 | `iterations/p1-i7/prompts/t5-tests.md` | `iterations/p1-i7/reviews/review-t5.md` | — |
| —     | — | `iterations/p1-i7/reviews/review-iteration.md` | — (QA) |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-7` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

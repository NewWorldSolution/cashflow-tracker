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

- **sp** — Sole Proprietorship / Jednoosobowa działalność gospodarcza
- **ltd** — Limited Company / Spółka z ograniczoną odpowiedzialnością
- **ff** — Family Foundation / Fundacja rodzinna
- **private** — Private / Prywatny

Database values are language-neutral keys. UI display must go through i18n.

---

## Dependency Map

```text
I7-T1 (schema + seed + migration)
  ├── I7-T2 (create/correct with company + for_accountant input)
  │     └── I7-T3 (list/detail/dashboard company display + filtering)
  └── I7-T4 (for_accountant display rules)
I7-T5 (tests) depends on T1–T4
```

Notes:

- T4 depends on T1 at runtime because the `transactions.for_accountant` column is created in T1.
- T2 and T4 both touch `app/templates/transactions/create.html`; merge planning must account for this overlap.
- Recommended merge order: `T1 → T2 → T3 → T4 → T5`.

---

## Planned Work

| # | Area | Description |
|---|------|-------------|
| 1 | Schema | Add `companies` table (`id`, `name`, `slug`, `is_active`) |
| 2 | Schema | Add `company_id` FK to `transactions` |
| 3 | Schema | Add `for_accountant BOOLEAN NOT NULL DEFAULT FALSE` to `transactions` |
| 4 | Seed | Seed 4 companies: `sp`, `ltd`, `ff`, `private` |
| 5 | Migration | Backfill existing transactions to default company `id = 1` (`sp`) |
| 6 | i18n | Add short company labels (`company_sp`, etc.) in EN + PL |
| 7 | i18n | Add full company labels (`company_sp_full`, etc.) in EN + PL |
| 8 | Create flow | Add company selector using short translated labels |
| 9 | Correct flow | Preserve and allow updating company + `for_accountant` via correction flow |
| 10 | List | Show company short label, remove `Logged by`, add `for_accountant` Yes/No column |
| 11 | Detail | Show company full label and always show `for_accountant` Yes/No |
| 12 | Dashboard | Add company filter with short translated labels |
| 13 | Workflow | No standalone toggle/edit flow for `for_accountant`; changes happen via correction |
| 14 | Tests | Cover company create/filter/detail/backfill flows |
| 15 | Tests | Cover `for_accountant` create/display/correction behavior |

---

## Tasks

| ID    | Title                               | Owner | Status     | Depends on | Branch |
|-------|-------------------------------------|-------|------------|------------|--------|
| I7-T1 | Companies schema + seed + migration | —     | ⏳ WAITING | —          | `feature/p1-i7/t1-companies-schema` |
| I7-T2 | Create/correct with company         | —     | ⏳ WAITING | I7-T1      | `feature/p1-i7/t2-company-create` |
| I7-T3 | List/detail/dashboard + filtering   | —     | ⏳ WAITING | I7-T2      | `feature/p1-i7/t3-company-views` |
| I7-T4 | `for_accountant` display + behavior | —     | ⏳ WAITING | I7-T1      | `feature/p1-i7/t4-accountant-flag` |
| I7-T5 | Tests                               | —     | ⏳ WAITING | I7-T1, I7-T2, I7-T3, I7-T4 | `feature/p1-i7/t5-tests` |

---

## Important Notes

- **Auth model unchanged** — current session-based auth stays as-is
- **Company is mandatory on all new transactions** — no null `company_id` after migration/backfill
- **Existing transactions backfilled** to company `id = 1` (`sp`)
- **Company names are not hardcoded user-facing strings in the DB** — translate from language-neutral keys
- **Short company labels** are for list/filter/form UI
- **Full company labels** are for transaction detail
- **`for_accountant` is a simple boolean in schema**
- **Changing `for_accountant` is not a standalone edit action** — use the existing correction flow
- **Transaction list removes `Logged by`** to make room for company + accountant columns
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

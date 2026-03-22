# P1-I5 — UI/UX Polish
## Task Board

**Status:** NOT STARTED
**Last updated:** 2026-03-22
**Iteration branch:** `feature/phase-1/iteration-5` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-5` → `main` ← QA agent approves before merge

---

## Dependency Map

```
I5-T1 (CSS system + base template)
  ├── I5-T2 (real dashboard)
  ├── I5-T3 (form UX)
  └── I5-T4 (list, detail & void styling)
        └── I5-T5 (flash messages + tests)
```

T1 is the foundation. T2, T3, T4 can run in parallel after T1. T5 depends on T4 because it tests create/void/correct flows end-to-end after styled pages exist, and its flash rendering depends on the base template work from T1 (transitively satisfied via T4).

---

## Tasks

| ID    | Title                              | Owner       | Status     | Depends on | Branch                                    |
|-------|------------------------------------|-------------|------------|------------|-------------------------------------------|
| I5-T1 | CSS system + base template         | Claude Code | ✅ DONE | —          | `feature/p1-i5/t1-css-base`              |
| I5-T2 | Real dashboard                     | Claude Code | ✅ DONE | I5-T1      | `feature/p1-i5/t2-dashboard`             |
| I5-T3 | Transaction form UX                | Claude Code | ✅ DONE | I5-T1      | `feature/p1-i5/t3-form-ux`              |
| I5-T4 | List, detail & void styling        | Codex       | ✅ DONE | I5-T1      | `feature/p1-i5/t4-list-detail-void`     |
| I5-T5 | Flash messages + tests             | Codex       | ✅ DONE | I5-T4      | `feature/p1-i5/t5-flash-tests`          |

---

## Prompts & Reviews

| Task  | Implementation prompt                           | Review prompt                             | Reviewer |
|-------|-------------------------------------------------|-------------------------------------------|----------|
| I5-T1 | `iterations/p1-i5/prompts/t1-css-base.md`     | `iterations/p1-i5/reviews/review-t1.md`  | —        |
| I5-T2 | `iterations/p1-i5/prompts/t2-dashboard.md`    | `iterations/p1-i5/reviews/review-t2.md`  | —        |
| I5-T3 | `iterations/p1-i5/prompts/t3-form-ux.md`      | `iterations/p1-i5/reviews/review-t3.md`  | —        |
| I5-T4 | `iterations/p1-i5/prompts/t4-list-detail.md`  | `iterations/p1-i5/reviews/review-t4.md`  | —        |
| I5-T5 | `iterations/p1-i5/prompts/t5-flash-tests.md`  | `iterations/p1-i5/reviews/review-t5.md`  | —        |
| —     | —                                               | `iterations/p1-i5/reviews/review-iteration.md` | — (QA) |

---

## Task Details

### I5-T1 — CSS system + base template

**Goal:** Establish the visual foundation that all other tasks build on.

**Allowed files:**
```
static/style.css            ← create new
app/templates/base.html     ← modify
```

**Deliverables:**
- `static/style.css` with CSS custom properties (colors, spacing, radius, typography from design reference)
- Base element styles: body, headings, links, tables, forms, buttons, inputs, selects, textareas
- Component classes: `.container`, `.card`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-destructive`, `.flash`, `.flash-success`, `.flash-error`, `.badge`, `.badge-active`, `.badge-voided`, `.toggle-group`, `.toggle-btn`, `.toggle-btn.active`
- SANDBOX banner improvement
- Nav with active state and consistent styling
- Responsive foundation (mobile-first, breakpoints at 768px and 1024px)
- Viewport meta tag in `<head>`
- Flash message rendering in base.html via a context processor or middleware that pops flash from session in Python (not in Jinja2 template)

**Key decisions:**
- System font stack — no external fonts
- No CSS framework — hand-written with custom properties
- Mobile-first responsive
- All colors via `--var` custom properties

**Acceptance check:**
- `style.css` loads on every page
- Base template renders cleanly with improved nav
- Flash message block present (even if no messages yet)
- Responsive meta tag present

---

### I5-T2 — Real dashboard

**Goal:** Replace placeholder dashboard with useful summary content.

**Depends on:** I5-T1 ✅ DONE

**Allowed files:**
```
app/templates/dashboard.html    ← rewrite
app/routes/dashboard.py         ← extend
static/style.css                ← extend (dashboard-specific classes only)
```

**Dashboard content:**
- Opening balance card (amount + as-of date from settings)
- Summary cards in a grid: active transaction count, voided count, total income, total expenses
- Recent transactions (last 5 active) — compact table or card list
- Quick action links: + New Transaction, View All Transactions

**Route changes:**
- Query settings table key-value pairs: `opening_balance` and `as_of_date` (keys in the `settings` table)
- Query transaction counts (active, voided)
- Query SUM for income and expense (active only)
- Query last 5 active transactions with category label

**Acceptance check:**
- Dashboard shows real numbers from the database
- Cards are responsive (stack on mobile, grid on desktop)
- Quick action links work

---

### I5-T3 — Transaction form UX

**Goal:** Make the form comfortable and clear. No logic changes.

**Depends on:** I5-T1 ✅ DONE

**Allowed files:**
```
app/templates/transactions/create.html    ← modify
static/form.js                            ← modify (no business-rule changes; only UI state/classes for new presentation)
```

**Form restructure — 5 sections:**
1. **Basics** — Date + Direction (toggle button style, not plain radio)
2. **Amount** — Prominent input + "Enter gross amount (VAT included)" helper
3. **Details** — Category + Payment method (+ Income type when income selected)
4. **VAT** — VAT rate + VAT deductible % (conditional visibility preserved)
5. **Optional** — Description textarea with conditional required indicator

**UX improvements:**
- Direction as styled toggle buttons (keep hidden radio for form submission)
- Card reminder as info callout (not plain text)
- Error summary box at top (required); inline field highlighting optional but no per-field error mapping
- Submit + Cancel with clear button hierarchy
- Works identically for create and correct flows (form_action variable)

**Critical constraint:** All `form.js` business logic must be preserved — lock/unlock, category filter, auto-defaults, page-load initialization (5b, 5c, 5d). Only add minimal JS for toggle button active class if needed.

**Acceptance check:**
- Form submits correctly (create + correct flows)
- All JS interactions work: direction toggle, category filter, VAT lock, card reminder
- Error re-render preserves form state
- Mobile layout is comfortable

---

### I5-T4 — List, detail & void styling

**Goal:** Make transaction history readable and audit trail easy to follow.

**Depends on:** I5-T1 ✅ DONE

**Allowed files:**
```
app/templates/transactions/list.html      ← modify
app/templates/transactions/detail.html    ← modify
app/templates/transactions/void.html      ← modify
static/style.css                          ← extend (page-specific classes only)
```

**List improvements:**
- Styled table with header, hover states, proper alignment
- Amount formatting: thousands separator, 2 decimal places
- Active/voided distinction in show_all mode: badges + muted rows
- Empty state when no transactions
- Show all / Active only toggle
- Responsive: horizontal scroll on mobile

**Detail improvements:**
- Card layout with field grouping
- Active: green badge + void/correct action buttons
- Voided: red badge + audit trail section (reason, voided by, replacement link)
- Clear timestamps

**Void improvements:**
- Warning-styled confirmation
- Transaction summary in muted card
- Destructive submit button
- Cancel link to detail
- Error display for validation failures

**Acceptance check:**
- List is readable with formatted amounts
- Show all mode distinguishes active vs voided clearly
- Detail shows full audit trail for voided transactions
- Void page looks like a serious confirmation
- All pages work on mobile

---

### I5-T5 — Flash messages + tests

**Goal:** Clear success feedback after every action. Test coverage for new behavior.

**Depends on:** I5-T4 ✅ DONE

**Allowed files:**
```
app/routes/transactions.py     ← modify (add flash on success)
app/main.py                    ← modify (flash middleware if needed)
app/templates/base.html        ← modify (flash rendering if not done in T1)
tests/test_transactions.py     ← extend
```

**Flash messages to add:**
- After create: "Transaction saved successfully."
- After void: "Transaction voided."
- After correct: "Transaction corrected. Original has been voided."

**Implementation:**
- Store: `request.session["flash"] = {"type": "success", "message": "..."}`
- Pop and expose via middleware/context processor in Python; base.html renders from context
- No extra dependencies

**New tests:**
- `test_flash_after_create` — POST create → redirect → GET list → flash message in response
- `test_flash_after_void` — POST void → redirect → GET list → flash message in response
- `test_flash_after_correct` — POST correct → redirect → GET list → flash message in response
- `test_flash_clears_after_display` — GET list (with flash) → GET list again → no flash

**Acceptance check:**
- Flash messages appear after create, void, correct
- Flash clears after one display
- All 94+ existing tests still pass
- New flash tests pass
- ruff clean

---

## Agent Rules

1. **Read this file first.** Find your task. Confirm status is WAITING before starting.
2. **Update status to IN PROGRESS** before writing a line of code.
3. **Check dependencies.** Never start if any dep is not ✅ DONE.
4. **Branch:** check out `feature/phase-1/iteration-5` first, then create your task branch from it. No worktrees needed — T2/T3/T4 can parallel if different agents, but sequential is also fine.
5. **PR targets the iteration branch**, not `main`. One task per PR.
6. **After completing:** set status to ✅ DONE. Add one-line note: what you produced.
7. **Never touch another agent's task.** Add notes under your own task only.
8. **If blocked:** set status to 🚫 BLOCKED with reason. Stop and wait.
9. **No business logic changes.** No validation changes. No schema changes.
10. **Test form interactions** after any template change — JS behavior must be preserved.
11. **Read your task prompt file:** `iterations/p1-i5/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-5` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

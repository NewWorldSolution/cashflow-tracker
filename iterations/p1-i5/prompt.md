# cashflow-tracker Task Prompt — P1-I5: UI/UX Polish

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/ → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point for transaction field rules |

---

## Repository State

- **Iteration branch:** `feature/phase-1/iteration-5`
- **Base branch:** `main` (P1-I4 merged + pre-I5 hotfixes)
- **Tests passing:** 94
- **Ruff:** clean
- **Last completed iteration:** P1-I4 — Corrections, Hardening & Acceptance
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I5 |
| Title | UI/UX Polish |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 5 |
| Feature branch | `feature/phase-1/iteration-5` |
| Depends on | P1-I4 (void/correct routes, detail/void templates, test suite — all merged to main) |
| Blocks | P1-I6 (Polish language UI) |
| PR scope | Task branches PR into `feature/phase-1/iteration-5`. The iteration branch PRs into `main` after QA. Do not combine iterations. Do not push partial work. |

---

## Task Goal

Make the app feel usable and clear without changing core business rules. After I5, users can work comfortably on desktop and mobile without needing developer guidance. Every action (create, void, correct) gives clear visual feedback. The form is well-organized, the list is readable, and the audit trail is easy to follow.

**Execution model:** 5 task branches, each with its own prompt file in `iterations/p1-i5/prompts/`. This file is the full reference; task prompt files are the execution guides.

---

## UI Design Reference

The folder `Minimal Transaction Entry Form/` at the project root contains a Figma-derived UI reference built with shadcn/ui components. This is a **design reference only** — do not use React, Tailwind, or any JS framework. Extract the visual language and translate it to plain CSS + Jinja2 templates.

### Design principles to extract and apply

**Color palette (translate to CSS custom properties):**
- Primary (near-black): `#030213` — main actions, headings, active toggle buttons
- Primary foreground: white — text on primary backgrounds
- Muted background: `#ececf0` — secondary surfaces, table headers
- Input background: `#f3f3f5` — form input fields
- Destructive: `#d4183d` — void actions, error states
- Borders: `rgba(0, 0, 0, 0.1)` — subtle, transparent
- Hover states: `bg-gray-50` equivalent — subtle highlight

**Typography:**
- Base: 16px
- Headings: font-weight 500 (medium)
- Body/input: font-weight 400 (normal)
- Labels: font-weight 500, same as buttons

**Spacing and radius:**
- Border radius base: 10px (--radius)
- Smaller radius: 6px (inputs, buttons)
- Card/section padding: 24px (p-6)
- Input padding: px-3 py-2 (12px 8px)
- Button padding: px-6 py-3 (24px 12px) or px-8 py-3 for submit

**Form structure (5 visual sections):**
1. **Basics** — Date + Income/Expense toggle (not radio buttons — styled toggle buttons)
2. **Amount** — Single prominent number input with gross amount label
3. **Details** — Category dropdown + Payment method dropdown
4. **VAT** — VAT rate + VAT deductible % dropdowns
5. **Optional** — Description textarea

**Toggle button pattern (Income/Expense):**
- Two buttons side by side (flex gap-3)
- Unselected: border-gray-300 bg-white text-gray-700 hover:bg-gray-50
- Selected: border-gray-900 bg-gray-900 text-white
- Full-width with flex-1

**Table pattern:**
- Bordered container with subtle border
- Header: muted background, border-bottom
- Rows: subtle border-bottom, hover highlight
- Right-aligned amounts, left-aligned text

**Error pattern:**
- Error summary box at top: padded, bordered, muted background
- Inline errors near fields: small text, muted color

**Button hierarchy:**
- Submit/primary: dark background, white text, larger padding
- Cancel/secondary: bordered, muted text, standard padding
- Destructive: red background, white text

### What NOT to copy from the design reference
- No React components — translate to Jinja2 + plain HTML
- No Tailwind — write plain CSS with custom properties
- No shadcn/ui library — extract visual patterns only
- No build step — CSS file served directly via FastAPI StaticFiles
- No dark mode — light mode only for now

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md          (I5 section)
```

### Task-specific

| Task | Also read |
|------|-----------|
| I5-T1 | `app/templates/base.html`, `Minimal Transaction Entry Form/src/styles/theme.css` |
| I5-T2 | `app/templates/dashboard.html`, `app/routes/dashboard.py` |
| I5-T3 | `app/templates/transactions/create.html`, `static/form.js`, `Minimal Transaction Entry Form/src/app/components/transaction-form.tsx` |
| I5-T4 | `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/templates/transactions/void.html` |
| I5-T5 | `app/routes/transactions.py`, `app/main.py`, `tests/test_transactions.py` |

---

## Allowed Files

```
static/style.css                         ← create new (T1)
app/templates/base.html                  ← modify: CSS link, nav, flash messages (T1, T5)
app/templates/dashboard.html             ← rewrite: real dashboard (T2)
app/routes/dashboard.py                  ← extend: dashboard data (T2)
app/templates/transactions/create.html   ← modify: form UX (T3)
static/form.js                           ← modify: no business-rule changes; only UI state/classes for new presentation (T3)
app/templates/transactions/list.html     ← modify: readability, formatting (T4)
app/templates/transactions/detail.html   ← modify: styling, audit visibility (T4)
app/templates/transactions/void.html     ← modify: confirmation styling (T4)
app/routes/transactions.py              ← modify: flash messages on success (T5)
app/routes/settings.py                   ← modify: flash message on opening balance save (T5)
app/main.py                              ← modify: flash message middleware if needed (T5)
tests/test_transactions.py               ← extend: flash message tests (T5)
iterations/p1-i5/tasks.md               ← status updates only
```

Do NOT modify:
- `app/services/validation.py` — frozen
- `app/services/calculations.py` — frozen
- `app/services/transaction_service.py` — frozen
- `db/` — no schema changes
- `seed/` — no data changes

---

## Deliverables by Task

### T1 — CSS System + Base Template (style.css, base.html)

**Goal:** Establish the visual foundation. Every subsequent task builds on this.

Create `static/style.css` with:
- CSS custom properties derived from the design reference (colors, spacing, radius, typography)
- Base element styles: body, headings, links, tables, forms, buttons
- Layout utilities: container, responsive breakpoints
- Component classes: `.card`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-destructive`, `.flash`, `.flash-success`, `.flash-error`, `.badge`, `.badge-active`, `.badge-voided`
- SANDBOX banner styling (already exists — improve visual presence)
- Nav styling with active state

Update `app/templates/base.html`:
- Link `style.css` in `<head>`
- Add viewport meta tag for responsive
- Improve nav structure and styling
- Add flash message rendering via a Jinja2 context processor or route helper that pops `request.session["flash"]` and passes it into template context (do not pop directly in the template — clearing belongs in Python, not Jinja2)
- Keep SANDBOX banner

**CSS approach rules:**
- No CSS framework — hand-written CSS using custom properties
- System font stack (no external font loading)
- Mobile-first responsive design
- No `!important` except SANDBOX banner
- All colors via custom properties for future theme changes

### T2 — Real Dashboard (dashboard.html, dashboard.py)

**Goal:** Replace the placeholder dashboard with useful summary content.

Update `app/routes/dashboard.py` to query:
- Opening balance and as-of date (from settings)
- Last 5 active transactions (same query pattern as list, LIMIT 5)
- Count of active transactions
- Count of voided transactions
- Total income (SUM of active income transactions)
- Total expenses (SUM of active expense transactions)

Update `app/templates/dashboard.html`:
- Opening balance card with as-of date
- Summary cards: active count, voided count, total income, total expenses
- Recent transactions preview (last 5) — compact table or card list
- Quick action links: + New Transaction, View All Transactions
- Use CSS classes from T1

### T3 — Transaction Form UX (create.html, form.js)

**Goal:** Make the form comfortable and clear. Keep all existing business logic intact.

Restructure `app/templates/transactions/create.html`:
- Organize into 5 visual sections matching the design reference:
  1. **Basics** — Date + Direction toggle (style as toggle buttons, not radio buttons; keep underlying radio input for form submission)
  2. **Amount** — Prominent input with persistent "Enter gross amount (VAT included)" helper
  3. **Details** — Category + Payment method side by side (or stacked on mobile)
  4. **VAT** — VAT rate + VAT deductible % side by side; conditional visibility preserved
  5. **Optional** — Description textarea with conditional "required" indicator
- Income type row: visible only when direction=income (existing JS handles this)
- Card reminder: styled as an info callout, not plain text
- Error display: summary box at top (required); inline field highlighting optional but no per-field error mapping (validation returns a flat list of strings, not field-keyed errors)
- Submit + Cancel buttons at bottom with clear hierarchy
- Form must work identically on the correct flow (form_action variable)

Update `static/form.js` (no business-rule changes; only minimal JS for UI state/classes required by the new form presentation):
- All existing lock/unlock, filter, and auto-default behavior stays untouched
- If toggle button styling requires JS for active class toggling, add minimal code
- Ensure all page-load initialization (5b, 5c, 5d) still works after template changes

### T4 — List, Detail & Void Styling (list.html, detail.html, void.html)

**Goal:** Make transaction history readable and the audit trail easy to follow.

Update `app/templates/transactions/list.html`:
- Styled table with header row, hover states, proper alignment
- Amount formatting: thousands separator, consistent decimals (Jinja2 filter or format string)
- Active/voided visual distinction in show_all mode: voided rows muted, strikethrough amount
- Status badges: green "Active", red "Voided"
- Empty state message when no transactions exist
- Show all / Active only toggle styled as a link or button
- Responsive: horizontal scroll wrapper on mobile, or card layout for narrow screens

Update `app/templates/transactions/detail.html`:
- Card-style layout with clear field grouping
- Active state: green badge, void/correct action buttons
- Voided state: red badge, audit trail section (void reason, voided by, when, replacement link)
- Back to list link
- Timestamps formatted clearly

Update `app/templates/transactions/void.html`:
- Warning-styled confirmation page
- Transaction summary in a muted card
- Void reason input with clear label
- Destructive-styled submit button
- Cancel link back to detail
- Error display for validation failures

### T5 — Flash Messages + Tests (routes, main.py, tests)

**Goal:** Clear success/error feedback after every action. No new business rules.

Implement session-based flash messages:
- Store in `request.session["flash"]` as `{"type": "success|error", "message": "..."}`
- Pop and expose via a middleware or context processor that reads `request.session.pop("flash", None)` and passes it to the template context — clearing happens in Python, not in Jinja2
- `base.html` renders the flash from context if present
- No extra dependencies — pure session + Jinja2

Add flash messages after:
- Transaction created: "Transaction saved successfully."
- Transaction voided: "Transaction voided."
- Transaction corrected: "Transaction corrected. Original has been voided."
- Opening balance saved: "Opening balance updated."

Add/extend tests:
- Test flash message appears after create
- Test flash message appears after void
- Test flash message appears after correct
- Test flash message clears after being displayed

---

## Responsive Breakpoints

```css
/* Mobile first — base styles for < 768px */
/* Tablet+ */
@media (min-width: 768px) { ... }
/* Desktop+ */
@media (min-width: 1024px) { ... }
```

Key responsive behaviors:
- Form: single column on mobile, two-column groups on desktop
- Table: horizontal scroll wrapper on mobile
- Dashboard cards: stack on mobile, grid on desktop
- Nav: always visible (3 items only — simple enough)

---

## What Must NOT Change

- All 94 existing tests must pass
- `validate_transaction` logic — no modifications
- `void_transaction` logic — no modifications
- Calculation formulas — no modifications
- Form submission behavior — same fields, same values, same redirects
- `form.js` business logic — lock/unlock, category filter, auto-defaults all preserved
- Database schema — no changes
- Route paths — no changes (add flash messages to existing routes only)

---

## Acceptance Checklist

```bash
pytest -v
# Expected: 94+ passed, 0 failed
ruff check .
# Expected: clean
```

- [ ] CSS loads on every page (check `/static/style.css` serves correctly)
- [ ] Dashboard shows real data: balances, counts, recent transactions
- [ ] Form is organized into clear sections with toggle-style direction buttons
- [ ] Form errors display clearly (summary box at top; inline field highlighting optional)
- [ ] Transaction list is readable with proper amount formatting
- [ ] Show all mode clearly distinguishes active vs voided rows
- [ ] Detail page shows full audit trail for voided transactions
- [ ] Void page feels like a real confirmation (warning styling)
- [ ] Flash messages appear after create, void, correct actions
- [ ] Flash messages clear after being displayed once
- [ ] All pages usable on mobile (test at 375px width)
- [ ] No broken form behavior — all JS interactions work as before
- [ ] SANDBOX banner still visible on every page

---

## Agent Rules

1. Read this file first.
2. Read your task prompt file: `iterations/p1-i5/prompts/t[N]-[name].md`
3. Update status to IN PROGRESS before writing any code.
4. Check dependencies — never start if dep is not DONE.
5. Verify acceptance checklist before requesting review.
6. After PR is merged: update `tasks.md` status → DONE with one-line note.
7. No business logic changes. No validation changes. No schema changes.
8. Test all form interactions manually after template changes — JS behavior must be preserved.
9. Mobile responsiveness is not optional — test at 375px.

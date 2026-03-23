# Phase 1 Plan — Web Form & Transaction Capture

**Status:** I1-I5 complete, I6 in progress, I7-I9 planned
**Timeline:** 9 iterations
**Database:** SQLite (sandbox — all data non-production)
**Stack decision (locked):** FastAPI, not Flask. Decision closed. Rationale: Phase 5 (Telegram) and Phase 6 (LLM) bypass the HTML form and call the same validation layer. FastAPI serves Jinja2 templates now and JSON responses later without retrofitting. Pydantic validation maps directly to transaction_validator rules.

---

## What Phase 1 delivers

A working internal tool that lets 3 authenticated users log transactions correctly, view recent history, and correct mistakes — with all VAT rules enforced and a clean audit trail. Phase 1 is done when users can hand the month's records to the accountant without manual reconstruction.

Phase 1 is **not** done when the form works. It is done when the correction flow works and the data is trustworthy.

---

## Project structure (to be created in Iteration 1)

```
cashflow-tracker/
├── app/
│   ├── main.py              # FastAPI app, router registration, session middleware
│   ├── models/
│   │   ├── user.py
│   │   ├── transaction.py
│   │   └── category.py
│   ├── services/
│   │   ├── validation.py    # all transaction_validator rules — single source of truth
│   │   └── calculations.py  # derived VAT formulas — never stored, always computed
│   ├── routes/
│   │   ├── auth.py          # login, logout, session
│   │   ├── transactions.py  # create, list, void, correct
│   │   └── settings.py      # opening balance setup
│   └── templates/
│       ├── base.html        # SANDBOX banner lives here — visible on every page
│       ├── auth/
│       ├── transactions/
│       └── settings/
├── static/
│   └── form.js              # category auto-defaults, field locking, card banner — vanilla JS only
├── seed/
│   ├── categories.sql       # all 22 categories with defaults — INSERT OR IGNORE
│   └── users.sql            # 3 users with bcrypt-hashed passwords — INSERT OR IGNORE
├── tests/
│   ├── test_validation.py
│   └── test_calculations.py
├── db/
│   ├── schema.sql           # all 5 tables: users, categories, transactions, settings, settings_audit
│   └── init_db.py           # schema creation + seed runner (idempotent)
├── .env.example             # SECRET_KEY, DATABASE_URL — never commit .env
├── requirements.txt
└── README.md
```

**Key structure rules:**
- `services/validation.py` is the single enforcement point for all transaction_validator rules — route handlers call it, they do not re-implement rules
- `services/calculations.py` contains all VAT formulas — nothing in templates or route handlers calculates VAT
- No business logic in templates or route handlers — they call services only

---

## Iteration 1 — Foundation
**Days 1–4**

### Goal
Working FastAPI app with database, seeded data, opening balance setup, and nothing broken.

### Scope
```
app/main.py
app/routes/settings.py
app/templates/settings/opening_balance.html
db/schema.sql
db/init_db.py
seed/categories.sql
seed/users.sql
requirements.txt
.env.example
```

### Skills to inject
- `skills/cash-flow/schema`
- `skills/cash-flow/auth_logic`
- `skills/cash-flow/error_handling`

### Deliverables
- FastAPI app with SQLite connection, session middleware, and secret key loaded from `.env`
- `db/schema.sql` creates all 5 tables: users, categories, transactions, settings, settings_audit
- `db/init_db.py` runs schema + seed (idempotent — safe to run multiple times)
- `seed/categories.sql` inserts all 22 categories using `INSERT OR IGNORE` — never duplicates on re-run
- `seed/users.sql` inserts 3 users with bcrypt-hashed passwords using `INSERT OR IGNORE`
- `.env.example` with `SECRET_KEY` and `DATABASE_URL` — `.env` added to `.gitignore`
- Opening balance setup page — captures `opening_balance` (PLN) and `as_of_date`, stored in settings table; every change writes an audit row to `settings_audit`
- Hard redirect to setup screen if opening balance not set — warning is not enough

### Acceptance criteria
- `python db/init_db.py` runs twice without error or duplicate rows (idempotent)
- All 5 tables exist: users, categories, transactions, settings, settings_audit
- All 22 categories present with correct `default_vat_rate` and `default_vat_deductible_pct`
- 3 users present with bcrypt-hashed passwords — plaintext never stored
- Opening balance page saves to settings table; every change creates a row in settings_audit
- Navigating to `/transactions/new` without opening balance set redirects to setup screen

### Constraints (from CLAUDE.md)
- `category_id` is an integer PK — seed data must use the exact names from concept.md
- `logged_by` stores `users.id` FK — never a name string
- `vat_rate` has no CHECK constraint in the database

---

## Iteration 2 — Authentication
**Days 5–7**

### Goal
Login, session management, and route protection. All 3 users can log in and out.

### Scope
```
app/routes/auth.py
app/templates/auth/login.html
app/templates/auth/base.html (update)
```

### Skills to inject
- `skills/cash-flow/auth_logic`
- `skills/cash-flow/error_handling`

### Deliverables
- Login page with username + password fields
- Session set on successful login — `users.id` stored in session, never username string
- All non-auth routes protected — redirect to login if no session
- Logout clears session
- Failed login shows error inline — no generic "wrong credentials" page, show the error on the form

### Acceptance criteria
- All 3 seeded users can log in with correct credentials
- Wrong password shows an error on the login page without redirecting
- Accessing any protected route while logged out redirects to login
- After logout, back button does not restore session
- `session['user_id']` contains `users.id` (integer) — not username, not name

### Constraints (from CLAUDE.md)
- `logged_by` must be `users.id` from session — never typed by user
- No silent failures — login errors surface explicitly on the form

---

## Iteration 3 — Transaction Capture
**Days 8–13**

### Goal
Transaction create form with all VAT rules enforced, all guardrails active, and correct persistence.

### Scope
```
app/routes/transactions.py       (create endpoint)
app/services/validation.py       (all validation rules)
app/services/calculations.py     (VAT formula, for form preview only — not stored)
app/templates/transactions/create.html
app/templates/transactions/list.html   (basic recent list)
```

### Skills to inject
- `skills/cash-flow/transaction_validator`
- `skills/cash-flow/form_logic`
- `skills/cash-flow/error_handling`
- `skills/cash-flow/deterministic_logic`

### Deliverables

**Form fields (all from build-phases.md):**
- Date (default today)
- Direction: income / expense
- Amount (gross)
- Category (dropdown — populates from categories table)
- Payment method: cash / card / transfer
- VAT rate: 0 / 5 / 8 / 23
- Income type: internal / external (shown only for income rows)
- VAT deductible %: 0 / 50 / 100 (shown only for expense rows, mandatory)
- Description (optional; required indicator shown for other_expense / other_income)

**Required guardrails (non-optional):**
- Persistent label on amount: "Enter gross amount (VAT included)"
- Card reminder when payment_method = card: "Log gross amount. Card commission is logged separately at month end from terminal invoice"
- Category selection auto-fills VAT rate and deductible % from category defaults (via `GET /categories` endpoint)
- **SANDBOX banner** — persistent on every page in `base.html`; removed only at go-live (PostgreSQL switch)

**Validation rules enforced (server-side — all mandatory):**
- `income_type = internal` → `vat_rate` must be 0 (reject any other value)
- Expense row → `vat_deductible_pct` must be present (100 / 50 / 0)
- `other_expense` or `other_income` → description must be non-empty
- `category_id` must be a valid FK — free-text category rejected
- `logged_by` set from session — never from form input
- `is_active` defaults to TRUE — not a form field

**Recent transaction list:**
- Shows last 20 transactions (active only — `WHERE is_active = TRUE`)
- Columns: date, category label, direction, amount, payment method, logged by (username)
- Ordered by `created_at DESC`

### Acceptance criteria
- Successful transaction saves to DB with all fields correctly populated
- `logged_by` is always `users.id` from session — never null, never a string
- `income_type = internal` with any `vat_rate ≠ 0` is rejected with an error message
- Expense row submitted without `vat_deductible_pct` is rejected
- `other_expense` submitted without description is rejected
- Card payment reminder appears when payment_method = card
- Gross amount label is visible at all times
- Category selection populates VAT rate and deductible % defaults
- Transaction list shows only active rows, ordered by `created_at DESC`
- All form errors shown inline — form does not reset, user input is preserved

### Constraints (from CLAUDE.md)
- No business logic in templates or route handlers — validation.py is the only enforcement point
- VAT calculations are never stored — computed at query time only
- No LLM anywhere in this iteration

---

## Iteration 4 — Corrections, Hardening & Acceptance
**Days 14–18**

### Goal
Void/correct workflow with full audit trail, test coverage on all validation and calculation rules, basic styling, and a working local setup.

### Scope
```
app/routes/transactions.py       (void + correct endpoints)
app/templates/transactions/detail.html
app/templates/transactions/void.html
tests/test_validation.py
tests/test_calculations.py
README.md                        (local setup + demo credentials)
```

### Skills to inject
- `skills/generic/qa_runner`
- `skills/generic/code_reviewer`
- `skills/cash-flow/transaction_validator`
- `skills/cash-flow/error_handling`

### Deliverables

**Void/correct flow:**
- Transaction detail view — shows all fields for a single transaction
- Void action — requires `void_reason` input; sets `is_active = FALSE`, `voided_by = session user_id`
- Correct action — voids original (as above) and opens create form pre-filled with original values; on save, links new transaction via `replacement_transaction_id` on the voided row
- Voided transactions hidden from the main list — visible in admin view only

**Test suite (test_validation.py):**
- `income_type = internal` with `vat_rate ≠ 0` → rejected
- Expense row with `vat_deductible_pct = NULL` → rejected
- `other_expense` with empty description → rejected
- `other_income` with empty description → rejected
- Free-text category value → rejected
- `is_active = FALSE` without `void_reason` → rejected
- Valid transaction for each of the 22 categories → accepted

**Test suite (test_calculations.py):**
- `vat_amount` formula for each valid rate (0, 5, 8, 23)
- `net_amount` derived correctly
- `vat_reclaimable` for deductible % of 0, 50, 100
- `effective_cost` formula
- `net_vat_position` across a mix of income and expense rows

**Local setup:**
- README updated with: local install steps, how to run `db/init_db.py`, demo credentials for all 3 users
- Basic functional styling — not polished, but usable on desktop

### Acceptance criteria
- A voided transaction does not appear in the transaction list
- Voided row has `is_active = FALSE`, non-empty `void_reason`, and `voided_by` set to the acting user
- Correction creates a new transaction and links it via `replacement_transaction_id` on the voided row
- All test cases in test_validation.py pass
- All test cases in test_calculations.py pass
- A new developer can run the app locally using only the README
- 30 sample transactions entered end-to-end with no schema changes required
- At least 3 of those are corrected via the void/correct flow

### Constraints (from CLAUDE.md)
- No hard deletes — ever
- `void_reason` is mandatory when `is_active` is set to FALSE
- `voided_by` must be `users.id` — never a name string

---

## Iteration 5 — UI/UX Polish
**After I4**

### Goal
Make the app feel usable and clear without changing core business rules. Users should be able to work comfortably on desktop and mobile without needing developer guidance.

### Scope
```
app/templates/base.html              (CSS system, flash messages, nav)
app/templates/dashboard.html         (real dashboard)
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
static/style.css                     (or classless CSS framework)
static/form.js                       (no logic changes — spacing/grouping only)
app/routes/dashboard.py              (dashboard data)
app/routes/transactions.py           (flash messages on success)
```

### Deliverables

**1. Minimal styling system**
- Add a lightweight CSS approach compatible with Jinja2 server-side rendering
- Framework choice is an implementation detail — Pico CSS, Simple.css, or hand-rolled are all acceptable
- Must not introduce any JS framework or build step

**2. Real dashboard**
Replace the placeholder with useful summary content:
- Opening balance and as-of date
- Recent transactions preview (last 5)
- Active vs voided transaction counts
- Quick links to create transaction and full transaction list

**3. Transaction form UX**
- Better spacing and grouping of fields
- Clear separation of always-visible vs conditional fields (income type, VAT deductible)
- Clearer labels and helper text
- Strong error presentation (inline errors near the field, not just top-of-form)
- Keep all current business logic and JS rules intact

**4. Transaction list readability**
- Amount formatting (thousands separator, consistent decimals)
- Clearer active/voided state in show_all mode
- Better column balance and alignment
- Good empty state message
- Responsive behaviour for smaller screens

**5. Detail and void view improvements**
- Detail page clearly shows active vs voided state with visual distinction
- Audit trail (created by, voided by, reason, replacement link, timestamps) easy to read
- Void page feels like a real confirmation screen — warning styling, clear consequences

**6. Flash messages (session-based)**
- Implement server-rendered flash messages via `request.session["flash"]`
- Read and clear in `base.html` on next page load
- Show after: create, void, correct, opening balance save
- No extra dependencies — pure session + Jinja2

**7. Responsive layout**
- All transaction pages usable on mobile
- Explicit mobile behaviour for lists (horizontal scroll or card layout) and detail pages
- Form must be comfortable to fill on a phone screen

**8. Audit visibility**
- Who created and when
- Who voided, why, and when
- Replacement link when corrected
- Timestamps visible on detail view

### Non-goals
- No business rule changes (unless already approved and merged)
- No translation pass — English UI only
- No JS framework migration
- No new routes beyond dashboard data and flash messages

### Acceptance criteria
- UI is visually consistent across dashboard, form, list, detail, void
- Success/error feedback is clear (flash messages work)
- Mobile layout is usable on a phone-sized screen
- All existing tests still pass (94+)
- ruff clean

### Constraints (from CLAUDE.md)
- Vanilla JS only — no frameworks
- Jinja2 server-side rendering only — no SPA
- No business logic in templates

---

## Iteration 6 — Multi-Language Foundation + Polish UI
**After I5**

### Goal
Prepare the app for multiple languages and deliver Polish as the first complete translation. The assistant and wife users work in Polish — the UI must speak their language.

### Scope
```
app/i18n/                            (new — translation dictionaries)
app/i18n/en.py                       (English messages — canonical keys)
app/i18n/pl.py                       (Polish translation)
app/templates/**/*.html              (all templates — use translation keys)
app/routes/*.py                      (pass locale/translator to templates)
app/main.py                          (language selection middleware)
```

### Deliverables

**1. Lightweight i18n structure**
- Simple message dictionary approach (Python dicts, one per language)
- Supported languages: `en`, `pl` (later `tr`)
- No heavy i18n framework unless complexity demands it

**2. Move all user-facing text into translation dictionaries**
Cover all UI text:
- Navigation labels
- Page headings
- Form labels and helper text
- Button text
- Empty state messages
- Flash messages
- Audit labels (created by, voided by, etc.)
- Status labels (Active, Voided)

**3. Translate validation messages at render time (Option A)**
- Validation service (`validation.py`) continues to return English error strings — no changes to frozen service layer
- Translation happens at the route/template layer before rendering to the user
- English strings serve as canonical keys for the translation lookup
- Zero test breakage — all existing assertions remain valid

**4. Polish UI — first complete translation**
- All UI text translated to Polish
- Polish becomes the primary language for the 3 business users
- English remains available as the default/fallback

**5. Locale-aware formatting**
- Date display in Polish convention (e.g., `22 marca 2026` or `22.03.2026`)
- Number/amount formatting consistent with Polish locale (e.g., `1 234,56 zł`)
- Currency formatting can be extended later if needed

**6. Language selection mechanism**
- Session-based or user-setting based
- App default with optional switcher in nav
- No heavy infrastructure — simple and practical

### Non-goals
- No LLM-based translation workflow
- No full enterprise i18n framework unless needed
- Free-text content (descriptions) remains user-entered as-is — not translated
- No changes to validation.py or calculations.py logic

### Acceptance criteria
- App renders all UI text from translation dictionaries
- Polish UI is complete — every label, button, message, heading translated
- Architecture supports adding Turkish later without rewriting templates or services
- Switching language changes all UI text without losing session or data
- All existing tests still pass (validation assertions remain English)
- ruff clean

### Constraints (from CLAUDE.md)
- No LLM calls in validation, calculation, or reporting
- Jinja2 server-side rendering only
- Deterministic Python for all logic layers

---

## Iteration 7 — Multi-Company Support + Accountant Flag
**After I6**

### Goal
Support multiple legal/business entities inside one app so transactions, views, and summaries can be separated by company. Also add the `for_accountant` flag to mark transactions that need accountant attention.

### Companies to seed
- **JDG** — sole proprietorship
- **LTD** — limited company
- **Foundation** — foundation entity
- **Private** — personal/non-business

### Scope
```
db/schema.sql                        (companies table, transactions.company_id FK)
db/init_db.py                        (migration + backfill)
seed/companies.sql                   (4 initial companies)
app/services/transaction_service.py  (company-aware queries)
app/routes/transactions.py           (company selector, filtering)
app/routes/dashboard.py              (company-specific summaries)
app/templates/**/*.html              (company display/selector, for_accountant UI)
app/i18n/en.py, pl.py                (company + accountant labels)
tests/test_transactions.py           (company + accountant tests)
```

### Deliverables
- `companies` table with `id`, `name`, `slug`, `is_active`
- `company_id` FK on transactions — mandatory on all new transactions
- Backfill existing transactions to a default company
- Company selector in transaction create/correct flow
- Company display in detail/list views
- Company filtering in list and dashboard
- Dashboard company-specific summaries
- `for_accountant` boolean field on transactions
- `for_accountant` form support and display in detail/list
- EN + PL translations for all company/accountant labels
- Tests for company create/list/detail/filter and for_accountant flows

### Non-goals
- No role-based permissions per company (same 3-user auth model)
- No multi-currency (explicitly deferred — see below)
- No accountant-facing reporting UI (just the flag)

### Acceptance criteria
- Transactions can be created and viewed per company
- Company filter works in list and dashboard
- for_accountant flag can be set and displayed
- Existing transactions are backfilled to a default company
- All tests pass, ruff clean

---

## Iteration 8 — Sub-Categories (Hierarchical Category System)
**After I7**

### Goal
Introduce a two-level category system (parent + sub-category) so transactions can be classified more precisely. The initial implementation builds the structure and UI — the final real taxonomy will come from user testing feedback later.

### Scope
```
db/schema.sql                        (categories.parent_id)
db/init_db.py                        (migration from flat to hierarchical)
seed/categories.sql                  (placeholder hierarchy)
app/services/validation.py           (hierarchy-aware validation)
app/routes/transactions.py           (two-level picker data)
app/templates/transactions/create.html (two-level picker UI)
app/templates/**/*.html              (category path display)
app/i18n/en.py, pl.py                (new category labels)
static/form.js                       (cascading picker behavior)
tests/                               (hierarchy selection + validation)
```

### Deliverables
- `parent_id` column on categories table for hierarchy
- Migration path from current flat 22 categories
- Placeholder/demo parent-child hierarchy in seed data
- Category queries/services updated for hierarchy
- Two-level category picker in create/correct forms
- Leaf-only selection enforcement (design decision in task breakdown)
- List/detail rendering with category path display
- EN + PL translations for new category keys
- Tests for hierarchy selection and validation

### Important notes
- **Real taxonomy deferred to user testing** — current implementation is structural, not final business data
- **Backward compatibility** — existing transactions must remain valid after migration
- **VAT defaults** — sub-categories inherit or override parent defaults (design decision during T1)

### Acceptance criteria
- Two-level picker works in create/correct forms
- Only valid (leaf) categories can be selected
- Existing transactions display correctly after migration
- All tests pass, ruff clean

---

## Iteration 9 — Azure / Server / Deployment
**After I8**

### Goal
Prepare the app for real deployment and operational use in Azure. This is the transition from SQLite sandbox to production PostgreSQL.

### Scope
```
Azure App Service or Container Apps   (hosting decision)
Azure PostgreSQL                      (production database)
app/main.py                          (production config, health check)
db/init_db.py                        (PostgreSQL compatibility)
requirements.txt                     (psycopg2 or asyncpg)
Dockerfile / deployment config       (if containerized)
.env.production                      (production env vars)
docs/deployment.md                   (runbook)
```

### Deliverables
- Azure hosting model decided and configured
- Production environment variable strategy (Key Vault or App Settings)
- Azure PostgreSQL provisioned and configured
- Schema migration: SQLite → PostgreSQL (data migration optional — sandbox data may be discarded)
- PostgreSQL conditional CHECK for `vat_deductible_pct NOT NULL on expenses` (per CLAUDE.md)
- Health-check endpoint
- Static file serving setup for production
- Logging and error-handling for deployed environment
- Deployment documentation / runbook
- CI/CD pipeline (optional)
- Smoke-test checklist

### Important notes
- **This is the go-live iteration** — SANDBOX banner removed, production data starts
- **All sandbox data may be discarded** — users have been warned since day 1
- **Schema is identical between SQLite and PostgreSQL** (per CLAUDE.md) — only connection string changes
- **Owner has Azure deployment experience** from WBSB project
- **Tests must pass against PostgreSQL**

### Acceptance criteria
- App deployed and accessible in Azure
- PostgreSQL database operational
- All existing tests pass against PostgreSQL
- Health check endpoint responds
- Deployment is repeatable via docs/pipeline
- SANDBOX banner removed

---

## Deferred to later phases

| Item | Phase | Notes |
|---|---|---|
| Monthly summary / reporting | Phase 2 | |
| Card reconciliation check | Phase 3 | |
| WBSB integration | Phase 4 | |
| Telegram bot | Phase 5 | |
| LLM extraction (Haiku / Sonnet) | Phase 6 | |
| PostgreSQL / Azure go-live | P1-I9 | Moved from "between phases" — now a planned iteration |
| CSV export | Phase 2 buffer | |
| Search / filter by date or category | Phase 2 | |
| Responsive mobile styling | P1-I5 (done) | |
| Role permissions beyond basic session auth | Not planned | |
| **Multi-currency / exchange rates** | **Future phase (post-Phase 7)** | **Intentionally deferred — too large for Phase 1. Deeply affects calculations, validation, reporting, and transaction semantics. Must be its own major iteration.** |

---

## Success criteria

Phase 1 is complete when:
1. All 3 users can log in and create transactions without developer help
2. 90%+ of common transactions can be entered without free-text workaround
3. All VAT validation rules pass the test suite
4. Opening balance is captured and stored
5. A mistaken entry can be voided and corrected without deleting history
6. 30+ realistic transactions have been entered end-to-end with no schema changes
7. A user can review the recent ledger and trust what was entered
8. The UI is visually clean, responsive, and gives clear feedback on every action (I5)
9. The assistant and wife can use the app in Polish (I6)
10. Transactions can be separated by company entity (I7)
11. Categories support hierarchical classification (I8)
12. App is deployed and running in Azure with PostgreSQL (I9)

**The real test:** users choose this over WhatsApp, notes, or paper for daily logging. If they do not, Phase 1 is not done regardless of what the code does.

---

## Risks

| Risk | Mitigation |
|---|---|
| Business rules in UI only | Every rule must live in the FastAPI route handler — the form is a convenience layer; Phase 5 Telegram and Phase 6 LLM skip it entirely |
| Void flow skipped as "nice to have" | It is must-have — without it, mistakes destroy audit trail |
| VAT edge cases missed in testing | qa_runner skill mandates specific edge cases regardless of scope |
| Phase 2 features creeping into Phase 1 | Deferred list above is explicit — code_reviewer flags scope violations |
| SQLite quirks masking PostgreSQL issues | Use standard SQL only — avoid SQLite-specific syntax |
| Seed script runs twice, creating duplicate categories | Use `INSERT OR IGNORE` — seed must be idempotent from day 1 |
| Session secret key not persisted across restarts | Set `SECRET_KEY` in `.env` from day 1 — if it changes, all sessions invalidate |
| Real data entered during sandbox phase | SANDBOX banner is not decoration — it sets expectations; users must know this data may be discarded |
| Over-indexing on planning, under-executing | Phase 1 brief is now locked. Start Iteration 1 today. |

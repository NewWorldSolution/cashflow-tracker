# cashflow-tracker

## What it is
A private cash flow tracker for a small Polish business. 3 users: owner, assistant, wife. Not a SaaS product. Records gross transactions, extracts VAT, and produces monthly summaries for the accountant.

## Who it is for
Internal use only. No public access. All 3 users interact via web form (Phases 1–4) and Telegram group bot (Phase 5+).

## What is built

### P1-I1 — Foundation (merged to main 2026-03-21)
- SQLite schema: `users`, `categories`, `transactions`, `settings`, `settings_audit` — 22 categories, 3 bcrypt-hashed users, idempotent init
- FastAPI app with `SECRET_KEY` guard, session middleware, opening balance gate (hard redirect for all unprotected routes)
- Opening balance route: GET/POST `/settings/opening-balance` with full settings_audit trail
- Jinja2 base template with SANDBOX banner + opening balance form
- 11 passing tests, ruff clean

### P1-I2 — Authentication (merged to main 2026-03-21)
- Auth service layer: `get_user_by_username`, `verify_password` (bcrypt UTF-8), `get_opening_balance`, `get_current_user` (isinstance guard + zombie session cleanup), `require_auth`
- Login/logout routes: `GET/POST /auth/login`, `POST /auth/logout` — session fixation prevention, identical error messages
- Placeholder dashboard: `GET /` — renders authenticated username
- Login template: `app/templates/auth/login.html` — extends base.html, inline errors, password field type="password"
- `AuthGate` middleware: replaces `OpeningBalanceGate` — single combined gate (balance → auth), single DB connection per request, EXEMPT_PATHS + EXEMPT_PREFIXES
- `base.html` nav: username display + POST logout button for authenticated users
- 25 passing tests (11 P1-I1 + 14 new), ruff clean

### P1-I3 — Transaction Capture (merged to main 2026-03-22)
- Validation service: `app/services/validation.py` — 15 rules, single enforcement point
- Calculations service: `app/services/calculations.py` — vat_amount, net_amount, vat_reclaimable, effective_cost (Decimal, never stored)
- Transaction routes: `GET/POST /transactions/new`, `GET /transactions/`, `GET /categories`
- Create template: all fields, inline errors, preserved input, card reminder, cash_in/cash_out field toggling
- List template: last 20 active transactions with derived columns
- `static/form.js`: category auto-defaults, cash_in_type VAT lock, card reminder, direction row toggling
- 61 passing tests (25 P1-I1/I2 + 36 new), ruff clean

### P1-I4 — Corrections, Hardening & Acceptance (merged to main 2026-03-22)
- Transaction service: `app/services/transaction_service.py` — `get_transaction` (joined lookup), `void_transaction` (single source of truth for soft-delete preconditions)
- 5 new routes: `GET /transactions/{id}`, `GET/POST /transactions/{id}/void`, `GET/POST /transactions/{id}/correct`
- Templates: `detail.html` (read-only view, active/voided states), `void.html` (reason form); `create.html` and `list.html` minimal updates
- 81 passing tests (61 P1-I1/I2/I3 + 20 new), ruff clean

### P1-I5 — UI/UX Polish (merged to main 2026-03-22)
- Pico CSS classless framework, responsive layout, flash messages (session-based)
- Real dashboard: opening balance, totals, recent transactions, active/voided counts
- Transaction form UX: grouped sections, inline errors, clear labels
- Detail/void view improvements: active/voided visual distinction, audit trail
- 98 passing tests, ruff clean

### P1-I6 — Multi-Language Foundation + Polish UI (merged to main 2026-03-23)
- i18n system: `app/i18n/` with `translate()`, `translate_error()`, `format_date()`, `format_amount()`, `format_datetime()`
- English + Polish dictionaries: all UI labels, validation errors, category labels
- Template extraction: all hardcoded strings → `{{ t('key') }}`; locale-aware formatting throughout
- Language switcher (PL | EN) in nav, session-persistent, default locale `pl`
- `voided_at TIMESTAMP` column with idempotent migration
- UX polish: "Direction" → "Transaction Type", "Void" → "Cancel" in UI, distinct correction vs cancellation details, correction reason required
- 102 passing tests, ruff clean

### P1-I7 — Multi-Company Support (merged to main 2026-03-23)
- `companies` table: 4 entities — Sole Proprietorship (JDG), Limited Company (Sp. z o.o.), Family Foundation, Private
- `company_id` FK added to transactions (NOT NULL, DEFAULT 1)
- `for_accountant` boolean flag on transactions — available in create/correct flows
- Company selector dropdown in create/correct forms, company filter in list/dashboard
- Company displayed in list (short label) and detail (full label)
- i18n: company labels (short + full) in EN and PL
- Validation updated to require company_id as FK
- ~120 passing tests, ruff clean

### P1-I8 — Hierarchical Categories + Manual VAT + Procedure Metadata (merged to main 2026-03-24)
- **Direction rename:** `income`/`expense` → `cash_in`/`cash_out` throughout DB, validation, routes, templates, i18n
- **Field rename:** `income_type` → `cash_in_type`
- **Hierarchical categories:** dropped 22 test categories, seeded 19 parent groups + 62 leaf subcategories from real business taxonomy. Two-level max, only leaves selectable
- **Two-level category picker:** parent group → subcategory cascade in create/correct forms (vanilla JS, no API calls)
- **Manual VAT mode:** `vat_mode` column (automatic/manual), `vat_rate` now nullable (NULL in manual mode), `manual_vat_deductible_amount` for cash_out manual mode
- **customer_type:** required on all transactions — `private` / `company` / `other`
- **document_flow:** `invoice` / `receipt` / `invoice_and_receipt` / `other_document` — required for external cash_in, optional for cash_out, hidden for internal cash_in
- **Cross-field validation:** `invoice_and_receipt` only when customer_type=private, manual_vat_deductible_amount ≤ manual_vat_amount, and more
- **Internal cash_in consolidated rules:** forces vat_mode=automatic, vat_rate=0, payment=cash, for_accountant=false, customer_type=private, document_flow=NULL
- **for_accountant default changed to TRUE** (except internal cash_in)
- 84 passing tests, ruff clean

## What comes next

**Phase 1 — Web form (one iteration remaining)**
- P1-I9: Azure deployment (SQLite → PostgreSQL, go-live)

**Phase 2 — Reporting & Business Logic**
- Per-company balances (each entity has own cash position)
- Internal transfers between companies
- Reporting leveraging parent-group / subcategory hierarchy
- Per-category defaults for customer_type and document_flow
- Role-based access control (receptionist vs admin)
- Time-based correction limits
- Invoice receivables tracking (pending → paid flow)

**Intentionally deferred beyond Phase 2:**
- Multi-currency / exchange rates — too large, deeply affects calculations, validation, reporting, and transaction semantics. Will be its own future major iteration.

## Stack (locked)
Python · FastAPI · SQLite sandbox → Azure PostgreSQL production · Jinja2 templates · Vanilla JS · python-telegram-bot (Phase 5) · Claude Haiku/Sonnet (Phase 6 only)

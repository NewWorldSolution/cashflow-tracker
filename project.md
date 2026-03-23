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
- Create template: all fields, inline errors, preserved input, card reminder, income/expense field toggling
- List template: last 20 active transactions with derived va/ec columns
- `static/form.js`: category auto-defaults, income_type VAT lock, card reminder, direction row toggling
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
- English + Polish dictionaries: all UI labels, validation errors, category labels (22 keys)
- Template extraction: all hardcoded strings → `{{ t('key') }}`; locale-aware formatting throughout
- Language switcher (PL | EN) in nav, session-persistent, default locale `pl`
- `voided_at TIMESTAMP` column with idempotent migration
- UX polish: "Direction" → "Transaction Type", "Void" → "Cancel" in UI, distinct correction vs cancellation details, correction reason required, `format_datetime()` for audit timestamps, "Logged by" removed from detail
- 102 passing tests, ruff clean

## What comes next
**Phase 1 — Web form (in progress)**
- P1-I6: Multi-language foundation + Polish UI (merged to main)
- P1-I7: Multi-company support (JDG, LTD, Foundation, Private) + `for_accountant` flag
- P1-I8: Sub-categories (hierarchical category system — structure first, real taxonomy from user testing)
- P1-I9: Azure / server / deployment (SQLite → PostgreSQL, go-live)

**Intentionally deferred beyond Phase 1:**
- Multi-currency / exchange rates — too large, deeply affects calculations, validation, reporting, and transaction semantics. Will be its own future major iteration.

## Stack (locked)
Python · FastAPI · SQLite sandbox → Azure PostgreSQL production · Jinja2 templates · python-telegram-bot (Phase 5) · Claude Haiku/Sonnet (Phase 6 only)

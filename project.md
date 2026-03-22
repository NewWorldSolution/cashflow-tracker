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

## What comes next
**Phase 1 — Web form (in progress)**
- P1-I3: Transaction entry form with category auto-defaults and required guardrails
- P1-I4: Monthly summary / reporting view

## Stack (locked)
Python · FastAPI · SQLite sandbox → Azure PostgreSQL production · Jinja2 templates · python-telegram-bot (Phase 5) · Claude Haiku/Sonnet (Phase 6 only)

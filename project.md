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

## What comes next
**Phase 1 — Web form (in progress)**
- P1-I2: Username/password login (session-based, one account per user)
- P1-I3: Transaction entry form with category auto-defaults and required guardrails
- P1-I4: Monthly summary / reporting view

## Stack (locked)
Python · FastAPI · SQLite sandbox → Azure PostgreSQL production · Jinja2 templates · python-telegram-bot (Phase 5) · Claude Haiku/Sonnet (Phase 6 only)

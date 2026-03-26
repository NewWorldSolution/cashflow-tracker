# Cash Flow Tracker

A private cash flow notebook for a small Polish service business. Built for 3 users (owner, assistant, wife) — not a SaaS product.

Records gross income and expenses with full Polish VAT tracking, hierarchical categories, multi-company support, and card payment reconciliation. Built iteratively in phases, starting with a web form and expanding to a Telegram group bot and LLM-assisted entry.

## Status
**Phase 1 — Iteration 8 complete.** Web form with SQLite, authentication, transaction capture, corrections, multi-language UI (PL/EN), multi-company support, hierarchical categories (19 groups / 62 subcategories), manual VAT mode, and procedure metadata.

**Next:** P1-I9 — Azure deployment (SQLite → PostgreSQL, go-live).

## What's built (Phase 1)

| Iteration | What | Status |
|---|---|---|
| I1 | Foundation — schema, FastAPI, opening balance gate | Done |
| I2 | Authentication — login/logout, session management, auth middleware | Done |
| I3 | Transaction capture — validation, calculations, create/list forms | Done |
| I4 | Corrections & hardening — void, correct, detail views | Done |
| I5 | UI/UX polish — Pico CSS, dashboard, flash messages | Done |
| I6 | Multi-language — i18n system, Polish + English, language switcher | Done |
| I7 | Multi-company — 4 entities (JDG, Sp. z o.o., Foundation, Private), `for_accountant` flag | Done |
| I8 | Hierarchical categories, direction rename (cash_in/cash_out), manual VAT, procedure metadata | Done |
| I9 | Azure deployment — SQLite → PostgreSQL, go-live | Not started |

## Phases

| Phase | What | Status |
|---|---|---|
| 1 | Web form — structured input, auth, VAT guardrails, categories, multi-company | In progress (I9 remaining) |
| 2 | Reporting, per-company balances, access control, category defaults | Planned |
| 3 | Card reconciliation check | Planned |
| 4 | WBSB integration → Monday report | Planned |
| 5 | Telegram group bot | Planned |
| 6 | LLM extraction — Haiku NLP, Sonnet for images | Planned |
| 7 | Internal financial statements — P&L, cash flow, VAT | Future |

## Architecture approach
- All design decisions closed and documented before code was written
- Skill-based agentic build: agents read domain rules before touching anything
- SQLite sandbox → Azure PostgreSQL at go-live
- Server-side rendering only (Jinja2) — no SPA, no JS frameworks

## Project docs
| Doc | Purpose |
|---|---|
| [`docs/concept.md`](docs/concept.md) | Data model, category list, VAT logic |
| [`docs/architecture.md`](docs/architecture.md) | Schema, stack decisions, derived calculations |
| [`docs/build-phases.md`](docs/build-phases.md) | Phased build plan and acceptance criteria |
| [`docs/agents-and-skills.md`](docs/agents-and-skills.md) | Agentic build structure and domain rules |
| [`CLAUDE.md`](CLAUDE.md) | Agent constitution — rules before touching anything |
| [`project.md`](project.md) | Current state and what comes next |

## Stack (locked)
Python · FastAPI · SQLite (sandbox) → Azure PostgreSQL (production) · Jinja2 templates · Vanilla JS · python-telegram-bot (Phase 5) · Claude Haiku/Sonnet (Phase 6 only)

## Licence
MIT

# Cash Flow Tracker

A private cash flow notebook for a small Polish service business. Built for 3 users (owner, assistant, wife) — not a SaaS product.

Records gross income and expenses with full Polish VAT tracking, card payment reconciliation, and automated monthly reporting. Built iteratively in phases, starting with a web form and expanding to a Telegram group bot and LLM-assisted entry.

## Status
**Phase 1 — In progress.** Web form with SQLite, username/password auth, and transaction entry.

## Architecture approach
- All 17 design decisions closed and documented before any code was written
- Skill-based agentic build: agents read domain rules before touching anything
- SQLite sandbox → Azure PostgreSQL at go-live

## Project docs
| Doc | Purpose |
|---|---|
| [`docs/concept.md`](docs/concept.md) | Data model, category list, VAT logic |
| [`docs/architecture.md`](docs/architecture.md) | Schema, stack decisions, derived calculations |
| [`docs/build-phases.md`](docs/build-phases.md) | Phased build plan and acceptance criteria |
| [`docs/agents-and-skills.md`](docs/agents-and-skills.md) | Agentic build structure and domain rules |
| [`CLAUDE.md`](CLAUDE.md) | Agent constitution — rules before touching anything |
| [`project.md`](project.md) | Current state and what comes next |

## Phases
| Phase | What | Status |
|---|---|---|
| 1 | Web form — structured input, auth, VAT guardrails | In progress |
| 2 | Basic reporting — daily / weekly / monthly | Planned |
| 3 | Card reconciliation check | Planned |
| 4 | WBSB integration → Monday report | Planned |
| 5 | Telegram group bot | Planned |
| 6 | LLM extraction — Haiku NLP, Sonnet for images | Planned |
| 7 | Internal financial statements — P&L, cash flow, VAT | Future |

## Stack
Python · Flask or FastAPI · SQLite → PostgreSQL · Jinja2 · python-telegram-bot · Claude Haiku / Sonnet

## Licence
MIT

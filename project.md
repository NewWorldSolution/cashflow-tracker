# cashflow-tracker

## What it is
A private cash flow tracker for a small Polish business. 3 users: owner, assistant, wife. Not a SaaS product. Records gross transactions, extracts VAT, and produces monthly summaries for the accountant.

## Who it is for
Internal use only. No public access. All 3 users interact via web form (Phases 1–4) and Telegram group bot (Phase 5+).

## What is built
- Project knowledge base complete: concept, architecture, build phases, agents & skills
- All 17 design decisions closed (cashflow-tracker-risk-review-v2.html)
- Category list defined and fixed: 4 income + 18 expense categories
- Full schema designed: users, categories, transactions, settings tables

## What comes next
**Phase 1 — Web form (current)**
- SQLite database initialised with schema
- Username/password login (one account per user)
- Transaction entry form with category auto-defaults and required guardrails
- Opening balance setup screen

## Stack (locked)
Python backend (Flask or FastAPI) · SQLite sandbox → Azure PostgreSQL production · Jinja2 templates · python-telegram-bot (Phase 5) · Claude Haiku/Sonnet (Phase 6 only)

# CLAUDE.md — cashflow-tracker

## Start every session by reading
- `project.md` — what is built, what comes next
- `docs/concept.md` — data model, category list, VAT logic
- `docs/architecture.md` — schema, stack decisions, derived calculations
- `docs/build-phases.md` — what is in scope for each phase

---

## Non-negotiable rules

### Amounts and VAT
- Always store gross amounts — never net. VAT is extracted from gross, never added on top.
- `income_type = internal` forces `vat_rate = 0`. Enforced in UI and backend. Not a default — a hard rule.
- `vat_deductible_pct` is mandatory on every expense row. Default 100. Never NULL.
- VAT amount, net amount, vat_reclaimable, and effective_cost are always derived at query time — never stored in the database.

### Categories
- `category_id` is always an integer FK — never store or accept free-text category names.
- The category list is fixed (4 income, 18 expense). Do not add categories without a migration plan.
- `other_expense` and `other_income` require a non-empty `description`. Enforce in UI and backend.

### Audit trail
- Transactions are never hard-deleted. Soft-delete only: set `is_active = FALSE`, provide `void_reason` and `voided_by` (FK to users.id).
- All queries and reports filter `WHERE is_active = TRUE` unless explicitly building an admin view.
- `created_at` is the authoritative ordering field. Never order correction or audit queries by `date` alone.

### Identity
- `logged_by` stores `users.id` (integer FK) — never a name string.
- Telegram identity is matched via `users.telegram_user_id`. Messages from unrecognized Telegram IDs are ignored.

### Schema constraints
- VAT rate validation lives in the application layer only — no CHECK constraint in the database.
- The PostgreSQL conditional CHECK for `vat_deductible_pct NOT NULL on expenses` is added at go-live only, not in the SQLite sandbox.

### No LLM in logic layers
- No LLM calls in validation, calculation, or reporting. All financial logic is deterministic Python.
- LLM is used only in Phase 6 (natural language → structured fields extraction) and only for that purpose.

---

## Database boundary
| Phase | Database | Data status |
|---|---|---|
| 1–4 (sandbox) | SQLite | Non-production — may be discarded |
| Go-live | Azure PostgreSQL | Production from this point |

Schema is identical between both engines. Only the connection string changes.

---

## Stack (locked — do not propose alternatives)
| Layer | Choice |
|---|---|
| Backend | Python — FastAPI (not Flask; decision closed) |
| Database | SQLite (sandbox) / PostgreSQL (production) |
| Templates | Jinja2 — server-side rendering only, no SPA |
| Client-side JS | Vanilla JS only — form behaviour, field locking, auto-defaults |
| Telegram | python-telegram-bot |
| LLM (Phase 6 only) | Claude Haiku (text) / Claude Sonnet (images) |

FastAPI rationale: Phase 5 (Telegram) and Phase 6 (LLM) bypass the HTML form entirely and call the same validation layer. FastAPI serves both Jinja2 templates (Phase 1–4) and JSON responses (Phase 5+) cleanly. Pydantic validation reduces boilerplate for the transaction_validator rules. Flask would require retrofitting an API layer later.

---

## What not to do
- Do not store derived values (vat_amount, net_amount, vat_reclaimable, effective_cost) in the database.
- Do not use free-text for `logged_by` or `category` — always resolve to the FK integer.
- Do not rename or delete categories that have transactions attached.
- Do not add LLM calls to any validation, calculation, or reporting layer.
- Do not propose JavaScript frameworks or client-side rendering.
- Do not skip the confirmation step in the Telegram bot — it is mandatory, not optional.

# Architecture Decisions

## Core Principles
- **Individual transactions** (not daily summaries) — enables correction, reconciliation, flexible querying
- **Gross amounts always** — commissions handled as separate cash_out transactions
- **No silent failures** — every validation error surfaces explicitly
- **Two-level category hierarchy** — parent groups for reporting, leaf subcategories for transactions

## Stack
| Layer | Choice | Rationale |
|---|---|---|
| Backend | Python — FastAPI | Serves both Jinja2 templates (Phase 1–4) and JSON responses (Phase 5+); Pydantic validation reduces boilerplate |
| Database | SQLite (sandbox only) → PostgreSQL (production at go-live) | SQLite for Phase 1 validation; go-live switches to Azure PostgreSQL — schema identical between both |
| Templates | Jinja2 — server-side rendering only | No SPA, no JS frameworks |
| Client-side JS | Vanilla JS only | Form behaviour, field locking, auto-defaults, category cascade |
| i18n | Custom `app/i18n/` with EN + PL dictionaries | `translate()`, `format_date()`, `format_amount()`, locale-aware throughout |
| Telegram bot | python-telegram-bot | Group bot, everyone sees confirmations |
| LLM extraction | Claude Haiku (text), Claude Sonnet (images) | Haiku near-free for text; Sonnet only for receipts |
| CSS | Pico CSS (classless) | Responsive, minimal, no build step |

## LLM Strategy
| Task | Model | Reason |
|---|---|---|
| Parse natural language message into transaction fields | Haiku | Near-free, fast |
| Extract data from photo (receipt, bank statement) | Sonnet | Vision capability needed |
| CSV/XLSX bank export parsing | No LLM | Deterministic parsing is better |
| Web form input | No LLM | User provides structured data directly |

### Tool Use / Function Calling for Telegram Bot
- Haiku extracts fields from user message using function calling
- Enforces output schema → eliminates parsing failures
- User confirms extracted fields before transaction is saved
- Fixed category + VAT rate lists in system prompt → improves classification reliability
- `logged_by` stores `users.id` — resolved by matching Telegram sender's user ID against `users.telegram_user_id`

## Telegram Bot Behaviour
- **Group bot** — owner, assistant, wife all in same group
- Everyone sees confirmations passively → natural audit trail
- Any member can send a transaction or ask a query
- **Identity:** Telegram user ID matched against `users.telegram_user_id` — messages from unrecognized Telegram IDs are ignored
- Corrections: user sends "fix last" or "delete that" → bot confirms before acting

## Database Schema

**Database boundary:** SQLite is the sandbox (Phase 1). Go-live = switch to Azure PostgreSQL. All data entered before go-live is non-production. From go-live onward, all data is real. The schema is identical between both engines — only the connection string changes.

```sql
CREATE TABLE users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    username         TEXT NOT NULL UNIQUE,
    password_hash    TEXT NOT NULL,
    telegram_user_id TEXT UNIQUE,  -- nullable; populated when Telegram bot is set up in Phase 5
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id                INTEGER PRIMARY KEY,
    name                       TEXT NOT NULL UNIQUE,  -- globally unique slug, e.g. cout_fuel
    label                      TEXT NOT NULL,          -- display name (translated via i18n)
    direction                  TEXT NOT NULL CHECK(direction IN ('cash_in','cash_out')),
    default_vat_rate           REAL,                   -- NULL for parent groups
    default_vat_deductible_pct REAL,                   -- cash_out subcategories only
    parent_id                  INTEGER REFERENCES categories(category_id)  -- NULL = parent group
);
-- Parent groups: IDs 1-19, parent_id = NULL
-- Leaf subcategories: IDs 101-162, parent_id references parent
-- Two-level max: only leaf nodes are selectable on transactions

CREATE TABLE companies (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE,  -- language-neutral key: sp, ltd, ff, private
    slug      TEXT NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
-- 4 entities: Sole Proprietorship, Limited Company, Family Foundation, Private

CREATE TABLE transactions (
    id                           INTEGER PRIMARY KEY AUTOINCREMENT,
    date                         DATE NOT NULL,
    amount                       DECIMAL(10,2) NOT NULL,  -- always gross
    direction                    TEXT NOT NULL CHECK(direction IN ('cash_in','cash_out')),
    category_id                  INTEGER NOT NULL REFERENCES categories(category_id),
    company_id                   INTEGER NOT NULL DEFAULT 1 REFERENCES companies(id),
    payment_method               TEXT NOT NULL CHECK(payment_method IN ('cash','card','transfer')),
    vat_rate                     REAL,  -- nullable: NULL when vat_mode = manual; validated in app layer
    cash_in_type                 TEXT CHECK(cash_in_type IN ('internal','external')),  -- cash_in rows only
    vat_deductible_pct           REAL,  -- cash_out rows only; enforced NOT NULL in app layer (default 100)
    manual_vat_amount            DECIMAL(10,2),  -- manual mode: user-entered VAT amount
    vat_mode                     TEXT NOT NULL DEFAULT 'automatic' CHECK(vat_mode IN ('automatic','manual')),
    manual_vat_deductible_amount DECIMAL(10,2),  -- manual mode, cash_out only
    customer_type                TEXT NOT NULL CHECK(customer_type IN ('private','company','other')),
    document_flow                TEXT CHECK(document_flow IN ('invoice','receipt','invoice_and_receipt','other_document')),
    description                  TEXT,  -- mandatory when category is other_expense or other_income
    for_accountant               BOOLEAN NOT NULL DEFAULT FALSE,
    logged_by                    INTEGER NOT NULL REFERENCES users(id),
    is_active                    BOOLEAN NOT NULL DEFAULT TRUE,
    void_reason                  TEXT,  -- mandatory when is_active set to FALSE
    voided_by                    INTEGER REFERENCES users(id),
    voided_at                    TIMESTAMP,
    replacement_transaction_id   INTEGER REFERENCES transactions(id),
    created_at                   TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- authoritative ordering field
);

-- PostgreSQL only — add at go-live
-- ALTER TABLE transactions
-- ADD CONSTRAINT chk_expense_vat_deductible
-- CHECK (direction != 'cash_out' OR vat_deductible_pct IS NOT NULL);

CREATE TABLE settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- opening_balance, as_of_date stored here

CREATE TABLE settings_audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    key        TEXT NOT NULL,
    old_value  TEXT,
    new_value  TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Cross-Field Validation Rules

All enforced in `app/services/validation.py`:

| Rule | Description |
|------|-------------|
| `invoice_and_receipt` only when `customer_type = private` | Polish business rule: both documents only for private persons |
| `manual_vat_deductible_amount <= manual_vat_amount` | Cannot deduct more VAT than was charged |
| `vat_rate` required when `vat_mode = automatic` | Automatic mode needs a rate |
| `vat_rate` must be NULL when `vat_mode = manual` | No sentinel values |
| `manual_vat_amount` required when `vat_mode = manual` | Manual mode needs explicit amount |
| `manual_vat_deductible_amount` required for cash_out when `vat_mode = manual` | Cash_out manual mode needs deductible amount |
| `document_flow` required when `cash_in + cash_in_type = external` | External sales need document tracking |
| `document_flow` must be NULL when `cash_in_type = internal` | Internal transfers have no documents |
| `cash_in_type` must be NULL for `cash_out` direction | Field only applies to cash_in |
| `vat_deductible_pct` must be NULL for `cash_in` direction | Deductibility only applies to cash_out |
| `other_income` and `other_expense` require non-empty description | Catch-all categories need explanation |
| `cash_in_type = internal` forces consolidated rules | See concept.md for full list |

## Integration with WBSB
- WBSB reads from the cashflow SQLite/PostgreSQL DB
- Monday morning report auto-triggers → delivered via existing I9 delivery pipeline (Teams/Slack/email)
- No code change to WBSB core — new data loader adapter added

## Derived Calculations (never stored, always computed)
```
-- Automatic mode:
vat_amount       = amount - (amount / (1 + vat_rate/100))
net_amount       = amount - vat_amount
vat_reclaimable  = vat_amount * vat_deductible_pct / 100          -- cash_out only
effective_cost   = amount - vat_reclaimable                        -- cash_out only

-- Manual mode:
vat_amount       = manual_vat_amount
net_amount       = amount - manual_vat_amount
vat_reclaimable  = manual_vat_deductible_amount                    -- cash_out only
effective_cost   = amount - manual_vat_deductible_amount            -- cash_out only

-- Aggregate:
net_vat_position = sum(cash_in vat_amount) - sum(cash_out vat_reclaimable)
```

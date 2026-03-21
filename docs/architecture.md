# Architecture Decisions

## Core Principles
- **Individual transactions** (not daily summaries) — enables correction, reconciliation, flexible querying
- **Gross amounts always** — commissions handled as separate expense transactions
- **No silent failures** — every validation error surfaces explicitly

## Stack
| Layer | Choice | Rationale |
|---|---|---|
| Database | SQLite (sandbox only) → PostgreSQL (production at go-live) | SQLite for Phase 1–4 validation; go-live switches to Azure PostgreSQL — schema identical between both |
| Web form | TBD (Flask / FastAPI + simple HTML form) | Structured input, no training needed |
| Telegram bot | python-telegram-bot | Group bot, everyone sees confirmations |
| LLM extraction | Claude Haiku (text), Claude Sonnet (images) | Haiku near-free for text; Sonnet only for receipts |
| Reporting | Python → Jinja2 → Markdown / HTML | Same pattern as WBSB |
| Delivery | WBSB I9 delivery infrastructure | Reuse Teams/Slack/email pipeline already built |

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

**Database boundary:** SQLite is the sandbox (Phases 1–4). Go-live = switch to Azure PostgreSQL. All data entered before go-live is non-production. From go-live onward, all data is real. The schema is identical between both engines — only the connection string changes.

```sql
CREATE TABLE users (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    username          TEXT NOT NULL UNIQUE,
    password_hash     TEXT NOT NULL,
    telegram_user_id  TEXT UNIQUE,  -- nullable; populated when Telegram bot is set up in Phase 5
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id                INTEGER PRIMARY KEY,
    name                       TEXT NOT NULL UNIQUE,  -- internal code, e.g. petrol
    label                      TEXT NOT NULL,          -- display name
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    default_vat_rate           REAL NOT NULL,
    default_vat_deductible_pct REAL                   -- expense categories only
);

CREATE TABLE transactions (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    date                       DATE NOT NULL,
    amount                     DECIMAL(10,2) NOT NULL,  -- always gross
    direction                  TEXT NOT NULL CHECK(direction IN ('income','expense')),
    category_id                INTEGER NOT NULL REFERENCES categories(category_id),
    payment_method             TEXT NOT NULL CHECK(payment_method IN ('cash','card','transfer')),
    vat_rate                   REAL NOT NULL,  -- validated in app layer; initial valid values: 0, 5, 8, 23
    income_type                TEXT CHECK(income_type IN ('internal','external')),  -- income rows only
    vat_deductible_pct         REAL,           -- expense rows only; enforced NOT NULL in app layer (default 100)
    manual_vat_amount          DECIMAL(10,2),  -- advanced mode: mixed-rate invoices only
    description                TEXT,           -- mandatory when category is other_expense or other_income
    logged_by                  INTEGER NOT NULL REFERENCES users(id),
    is_active                  BOOLEAN NOT NULL DEFAULT TRUE,
    void_reason                TEXT,           -- mandatory when is_active set to FALSE
    voided_by                  INTEGER REFERENCES users(id),
    replacement_transaction_id INTEGER REFERENCES transactions(id),
    created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- authoritative ordering field
);

-- PostgreSQL only — add at go-live
-- ALTER TABLE transactions
-- ADD CONSTRAINT chk_expense_vat_deductible
-- CHECK (direction != 'expense' OR vat_deductible_pct IS NOT NULL);

CREATE TABLE settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- opening_balance, as_of_date stored here
```

## Integration with WBSB
- WBSB reads from the cashflow SQLite/PostgreSQL DB
- Monday morning report auto-triggers → delivered via existing I9 delivery pipeline (Teams/Slack/email)
- No code change to WBSB core — new data loader adapter added

## Derived Calculations (never stored, always computed)
```
vat_amount       = amount - (amount / (1 + vat_rate/100))
               OR = manual_vat_amount  (if advanced mode used)

net_amount       = amount - vat_amount
vat_reclaimable (expense) = vat_amount * vat_deductible_pct / 100
effective_cost   = net_amount + (vat_amount × (1 - vat_deductible_pct / 100))
net_vat_position = sum(vat_collected_income) - sum(vat_reclaimable_expenses)
```

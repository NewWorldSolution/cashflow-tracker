# Build Phases

## Prerequisites (Before Starting)
1. WBSB I12 complete
2. WBSB I13 (Azure deployment) complete
3. User familiar with Azure deployment and server setup
4. Category reference table defined and seeded

---

## Phase 1 — Web Form
**Goal:** Usable structured input for all 3 users immediately. No LLM needed.

**Note:** Phase 1 runs on SQLite. All data entered in Phase 1 is non-production and may be discarded or migrated at go-live (switch to Azure PostgreSQL).

### Completed Iterations

**I1 — Foundation:** SQLite schema, FastAPI app, opening balance gate, settings audit trail.

**I2 — Authentication:** Username/password login, session management, AuthGate middleware, all transactions linked to authenticated user ID.

**I3 — Transaction Capture:** Validation service (15 rules), calculations service (VAT, net, effective cost — never stored), create/list forms with category auto-defaults and card payment reminder.

**I4 — Corrections & Hardening:** Void (soft-delete with reason), correct (new transaction replaces old), detail view. Transactions are never hard-deleted.

**I5 — UI/UX Polish:** Pico CSS, real dashboard (balance, totals, recent transactions), flash messages, responsive layout.

**I6 — Multi-Language:** i18n system with `translate()`, English + Polish dictionaries, language switcher (PL | EN), default locale `pl`, `voided_at` timestamp column.

**I7 — Multi-Company:** 4 company entities (Sole Proprietorship, Limited Company, Family Foundation, Private). Company selector on all transactions. `for_accountant` boolean flag.

**I8 — Hierarchical Categories + Manual VAT + Procedure Metadata:**
- Direction renamed: `income`/`expense` → `cash_in`/`cash_out`
- Field renamed: `income_type` → `cash_in_type`
- 22 test categories dropped, replaced with 19 parent groups + 62 real subcategories (two-level hierarchy, only leaves selectable)
- Manual VAT mode: `vat_rate` nullable, user enters `manual_vat_amount` + `manual_vat_deductible_amount`
- `customer_type`: required on all transactions (`private` / `company` / `other`)
- `document_flow`: required for external cash_in, optional for cash_out (`invoice` / `receipt` / `invoice_and_receipt` / `other_document`)
- Cross-field validation: `invoice_and_receipt` only when customer_type=private
- Internal cash_in consolidated rules: forces vat_mode=automatic, vat_rate=0, payment=cash, for_accountant=false, customer_type=private, document_flow=NULL

### Remaining

**I9 — Azure Deployment (not started):**
- SQLite → Azure PostgreSQL migration
- Environment variable handling for production
- Health check endpoint
- SANDBOX banner removal
- PostgreSQL CHECK constraint for `vat_deductible_pct NOT NULL on expenses`
- Go-live

### Current Fields (post-I8)

- Date (default: today)
- Direction: cash_in / cash_out
- Amount (gross — reminder shown)
- Company (dropdown — 4 entities)
- Category (two-level picker: parent group → subcategory; `category_id` FK to leaf node)
- Payment method: cash / card / transfer
- VAT mode: automatic / manual
- VAT rate: 0% / 5% / 8% / 23% (automatic mode; default set by category; locked if `cash_in_type = internal`)
- Manual VAT amount + Manual VAT deductible amount (manual mode)
- Cash_in type: internal / external (cash_in only)
- VAT deductible %: 100% / 50% / 0% (cash_out only, automatic mode; mandatory, default 100%)
- Customer type: private / company / other (required)
- Document flow: invoice / receipt / invoice_and_receipt / other_document (required for external cash_in, optional for cash_out)
- For accountant: boolean (default true, except internal cash_in)
- Description (optional; mandatory when category is other_expense or other_income)

### Input guardrails
- **Gross amount reminder** — persistent label: "Enter gross amount (VAT included)"
- **Category auto-defaults** — selecting a subcategory auto-fills VAT rate and deductibility; user can override
- **Card payment reminder** — when `payment_method = card`: "Log gross amount. Card commission is logged separately at month end from terminal invoice"
- **Internal cash_in lock** — forces VAT 0%, cash payment, for_accountant false, customer_type private, document_flow hidden

---

## Phase 2 — Reporting & Business Logic
**Goal:** Financial summaries, per-company balances, access control, smart defaults.

Planned scope (from I8 scope decisions, not yet committed):
- **Per-company balances** — each company (JDG, Ltd, Foundation, Private) has own cash position
- **Internal transfers** — move money between company balances
- **Reporting** — leveraging parent-group / subcategory hierarchy for analysis
- **Per-category defaults** — customer_type and document_flow auto-fill from category
- **Role-based access control** — receptionist (view/create/correct within 7 days) vs admin (full access)
- **Invoice receivables tracking** — record sale on invoice date as pending receivable, mark paid when cash arrives
- **Non-cash / amortization category** — needs `affects_cashflow` flag; for profitability analysis

Reports:
```
Monthly Income
──────────────────────────────────────
By payment method:
  Card:                    12,000 PLN
  Cash:                     4,500 PLN
  Transfer:                 2,000 PLN
  Total gross:             18,500 PLN

By VAT rate:
  23% VAT:                 15,000 PLN
  0% / internal:            3,500 PLN
  VAT collected (approx):   2,845 PLN

Monthly Expenses
──────────────────────────────────────
  Card terminal fees:         360 PLN  (100% VAT deductible)
  Petrol:                     800 PLN  (50% VAT deductible)
  Other:                    1,300 PLN  (100% VAT deductible)
  Total:                    2,460 PLN
  VAT reclaimable:            460 PLN

Net VAT position:           2,385 PLN  (collected - reclaimable)
Net cash position:         16,040 PLN
```

---

## Phase 3 — Card Reconciliation Check
**Goal:** Month-end sanity check — catch missing transactions or invoice errors.

```
Expected card deposits = total card sales - total card fees logged
Actual bank deposits   = sum of card transfers received in bank
Difference             = 0 ✓  (flag if mismatch)
```

---

## Phase 4 — WBSB Integration
**Goal:** WBSB reads cashflow DB → Monday morning report auto-delivered.

- New data loader adapter in WBSB (reads cashflow DB instead of CSV)
- Reuse WBSB I9 delivery pipeline (Teams / Slack / email)
- No changes to WBSB core metrics or rules engine

---

## Phase 5 — Telegram Group Bot
**Goal:** Natural language input from the group chat, same database.

- python-telegram-bot
- Group chat: owner, assistant, wife all in one group
- Everyone sees confirmations — passive audit trail
- **Identity:** each user's Telegram user ID is stored in `users.telegram_user_id`. The bot matches incoming messages against this column — messages from unrecognized Telegram IDs are ignored.
- Commands: log transaction, query balance, correct last entry

---

## Phase 6 — LLM Extraction
**Goal:** Haiku parses natural language messages into structured transaction fields.

- Function calling / tool use → enforces output schema
- User confirms extracted fields before save
- Fixed category + VAT lists in system prompt
- Sonnet used only for photo input (receipts, bank statements)

---

## Phase 7 — Internal Financial Statements (future)
**Goal:** Owner-facing P&L, cash flow statement, VAT summary.

- P&L — income vs expenses by category, month over month
- Cash flow statement — opening balance → in → out → closing balance
- VAT summary — collected vs reclaimable, net position per period
- No new data collection needed — just different grouping of existing data
- **Not for submission anywhere** — internal visibility only

---

## Intentionally Deferred — Multi-Currency / Exchange Rates

**Status:** Not scheduled. Deferred to a future phase beyond Phase 7.

**Reason:** Multi-currency support is too large for any current iteration. It deeply affects:
- **Calculations** — every VAT/net/gross formula needs a currency dimension
- **Validation** — exchange rate source, date-of-rate rules, rounding
- **Reporting** — aggregation across currencies, conversion basis
- **Transaction semantics** — base currency vs transaction currency vs reporting currency

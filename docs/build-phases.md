# Build Phases

## Prerequisites (Before Starting)
1. WBSB I12 complete ✅
2. WBSB I13 (Azure deployment) complete — user's current iteration
3. User familiar with Azure deployment and server setup
4. Category reference table defined and seeded (4 income categories, 18 expense categories) — must exist before Phase 1 development starts

---

## Phase 1 — Web Form (2–3 days)
**Goal:** Usable structured input for all 3 users immediately. No LLM needed.

**Note:** Phase 1 runs on SQLite. All data entered in Phase 1 is non-production and may be discarded or migrated at go-live (switch to Azure PostgreSQL).

Authentication (required — not optional):
- Username + password login page, one account per user
- All transactions linked to authenticated user ID, never to a typed name

Fields to expose:
- Date (default: today)
- Direction: income / expense
- Amount (gross — reminder shown)
- Category (dropdown — `category_id` FK; auto-fills VAT rate and deductibility defaults)
- Payment method: cash / card / transfer
- VAT rate: 0% / 5% / 8% / 23% (default set by category; locked if `income_type = internal`)
- Income type: internal / external (income only)
- VAT deductible %: 100% / 50% / 0% (expense only; mandatory, default 100%)
- Description (optional; mandatory when category is `other_expense` or `other_income`)

Required input guardrails (Phase 1 — not optional):
- **Gross amount reminder** — persistent label on the amount field: "Enter gross amount (VAT included)"
- **Category auto-defaults** — selecting a category auto-fills the suggested VAT rate and, for expenses, the default deductibility percentage; user can override consciously
- **Card payment reminder** — when `payment_method = card`: "Log gross amount. Card commission is logged separately at month end from terminal invoice"

Opening balance setup screen (one-time):
- Enter current cash balance + as_of_date
- Warn if not set on first visit

---

## Phase 2 — Basic Reporting (2–3 days)
**Goal:** Daily / weekly / monthly financial summaries.

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

## Phase 3 — Card Reconciliation Check (1 day)
**Goal:** Month-end sanity check — catch missing transactions or invoice errors.

```
Expected card deposits = total card sales - total card fees logged
Actual bank deposits   = sum of card transfers received in bank
Difference             = 0 ✓  (flag if mismatch)
```

---

## Phase 4 — WBSB Integration (2–3 days)
**Goal:** WBSB reads cashflow DB → Monday morning report auto-delivered.

- New data loader adapter in WBSB (reads cashflow DB instead of CSV)
- Reuse WBSB I9 delivery pipeline (Teams / Slack / email)
- No changes to WBSB core metrics or rules engine

---

## Phase 5 — Telegram Group Bot (1–2 weeks)
**Goal:** Natural language input from the group chat, same database.

- python-telegram-bot
- Group chat: owner, assistant, wife all in one group
- Everyone sees confirmations — passive audit trail
- **Identity:** each user's Telegram user ID is stored in `users.telegram_user_id` (set up before Phase 5 goes live). The bot matches incoming messages against this column — messages from unrecognized Telegram IDs are ignored. Identity belongs to the user model, not the settings table.
- Commands: log transaction, query balance, correct last entry

---

## Phase 6 — LLM Extraction (2–3 days)
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

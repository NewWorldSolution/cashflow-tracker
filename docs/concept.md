# Concept & Data Model

## Users
3 users: owner, assistant, wife. Private — not a SaaS product.

## Input Modes
1. **Web form** (Phase 1) — structured dropdowns, immediate usability, no LLM needed
2. **Telegram group bot** (Phase 2) — natural language input, same database backend

---

## Transaction Data Model

```
Transaction
├── date
├── amount                       (ALWAYS gross — full sale amount including VAT)
├── direction                    (income / expense)
├── category_id                  (FK → categories.category_id — never free text)
├── payment_method               (cash / card / transfer)
├── vat_rate                     (0% / 5% / 8% / 23%) — default set by category; validation in app layer
├── income_type                  (income only: internal / external) — internal forces vat_rate to 0%, field locked
├── vat_deductible_pct           (expenses only: 100% / 50% / 0%) — mandatory, default 100%
├── manual_vat_amount            (optional — advanced mode for mixed-rate invoices only)
├── description                  (optional free text; mandatory when category is other_expense or other_income)
├── logged_by                    (FK → users.id)
├── is_active                    (BOOLEAN DEFAULT TRUE — soft-delete flag; reports filter WHERE is_active = TRUE)
├── void_reason                  (mandatory when is_active is set to FALSE)
├── voided_by                    (FK → users.id — who deactivated the row)
├── replacement_transaction_id   (FK → transactions.id — points to the correcting transaction)
└── created_at                   (TIMESTAMP — authoritative ordering field)
```

## Settings / Accounts Table

```
opening_balance:    (PLN amount — log once when system starts, never reconstruct later)
as_of_date:         (date opening balance was recorded)
```

**Critical:** Opening balance must be recorded on day 1. Without it a real cash flow statement is impossible.

---

## VAT Logic

### Income Transactions
- Use `income_type`: `internal` or `external`
- `income_type = internal` → VAT forced to 0%, gross = net, field locked — this is a hard rule, not a default
- `income_type = external` → VAT defaults to 23%, user can change to 5%, 8%, 0%
- No `vat_deductible_pct` field on income rows
- Always record **gross amount** — VAT is extracted from gross, never added on top

### Expense Transactions
- No `income_type` field on expense rows
- `vat_deductible_pct` is mandatory — default 100%, allowed values: 100 / 50 / 0
- Defaults are set by category (see Category Reference below)

### Derived Calculations (never stored)
```
vat_amount       = amount - (amount / (1 + vat_rate / 100))
               OR = manual_vat_amount  (if advanced mode used)

net_amount       = amount - vat_amount
vat_reclaimable  = vat_amount × vat_deductible_pct / 100   (expenses only)
effective_cost   = net_amount + (vat_amount × (1 - vat_deductible_pct / 100))
net_vat_position = SUM(income vat_amount) - SUM(expense vat_reclaimable)
```

---

## Category Reference

The category list is fixed and versioned. Transactions store `category_id` (FK), never free text. Categories are never renamed or deleted once transactions are attached.

### Income Categories — v1
| # | name | label | Default VAT | income_type default |
|---|---|---|---|---|
| 1 | `services` | Services | 23% | external |
| 2 | `products` | Products sold | 23% | external |
| 3 | `internal_transfer` | Internal transfer | 0% (locked) | internal (locked) |
| 4 | `other_income` | Other income | 23% | external |

### Expense Categories — v1
| # | name | label | Default VAT | Default deductible % | Notes |
|---|---|---|---|---|---|
| 1 | `marketing` | Marketing & advertising | 23% | 100% | Ads, agency, promo materials |
| 2 | `marketing_commission` | Sales commissions | 23% | 100% | Commissions paid to resellers |
| 3 | `rent` | Rent & premises | 23% | 100% | |
| 4 | `utilities` | Utilities | 23% | 100% | Electricity, internet, water |
| 5 | `renovation` | Renovation & repairs | 23% | 100% | Flag large amounts to accountant |
| 6 | `office_supplies` | Office supplies | 23% | 100% | |
| 7 | `cleaning` | Cleaning services | 0% | 0% | Cash payments, no invoice — 0% VAT, not deductible |
| 8 | `consumables` | Operational consumables | 23% | 100% | Gloves, towels, materials used in service delivery |
| 9 | `equipment` | Equipment & tools | 23% | 100% | Devices and tools used during operations |
| 10 | `contractor_fees` | Contractor & educator fees | 23% | 100% | Commission to people delivering education |
| 11 | `taxes` | Taxes & ZUS | 0% | 0% | ZUS, PIT, VAT payments — pure cash outflow |
| 12 | `it_software` | IT & software | 23% | 100% | Subscriptions, domains, hosting |
| 13 | `salaries` | Salaries & employee costs | 0% | 0% | Net salary + employer ZUS |
| 14 | `transport_vehicle` | Vehicle & petrol | 23% | 50% | Car, petrol — Polish mixed-use rule |
| 15 | `transport_travel` | Travel & transport | 0% | 100% | Flights, trains — VAT exempt, fully deductible as cost |
| 16 | `training` | Training & education | 23% | 100% | Courses, seminars attended by owner/staff |
| 17 | `inventory` | Inventory purchases | 23% | 100% | Products bought to resell — not operational consumables |
| 18 | `other_expense` | Other expense | 23% | 100% | Description mandatory when this category is selected |

---

## Card Payment Reconciliation

### The Problem
- Sale: 3000 PLN recorded as income (card)
- Bank deposit: 2970 PLN (card company keeps 30 PLN commission)
- End of month: card company sends invoice for total commissions (e.g. 450 PLN)

### The Correct Approach
**Always log gross sale amount.** Handle commission as a separate expense transaction.

```
Transaction 1 — point of sale
├── amount:           3000 PLN  ← GROSS, never 2970
├── direction:        income
├── payment_method:   card
└── vat_rate:         23%

Transaction 2 — end of month from terminal invoice
├── amount:           450 PLN
├── direction:        expense
├── category:         bank_fees
├── vat_rate:         23%
└── vat_deductible_pct: 100%
```

**Why:** Income statement shows true revenue. Commission is a real visible cost. VAT calculated on full sale amount (legally correct in Poland).

### Web Form Reminder
When `payment_method = card`, show note:
> "Log gross amount. Card commission logged separately at month end from terminal invoice."

### Month-End Reconciliation Check
```
Expected card deposits = total card sales - total card fees logged
Actual bank deposits   = sum of card transfers received in bank
Difference             = 0 ✓  (flag if mismatch → missed transaction or invoice error)
```

---

## Scope Boundary (Important)
- Records **facts only** — gross amounts, VAT rate, payment method
- No tax calculation or tax advice
- No connection to any official accounting or tax system
- Accountant uses the monthly summaries — tool does not interpret tax obligations
- Internal financial statements (Phase 3) are for owner visibility only, not for submission anywhere

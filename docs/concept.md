# Concept & Data Model

## Users
3 users: owner, assistant, wife. Private — not a SaaS product.

## Input Modes
1. **Web form** (Phase 1) — structured dropdowns, immediate usability, no LLM needed
2. **Telegram group bot** (Phase 5) — natural language input, same database backend

## Companies
4 business entities tracked in a single system:
- **Sole Proprietorship (JDG)** — main business
- **Limited Company (Sp. z o.o.)** — secondary entity
- **Family Foundation** — non-profit entity
- **Private** — personal transactions

Every transaction belongs to exactly one company via `company_id` FK.

---

## Transaction Data Model

```
Transaction
├── date
├── amount                          (ALWAYS gross — full amount including VAT)
├── direction                       (cash_in / cash_out)
├── category_id                     (FK → categories.category_id — leaf node only, never free text)
├── company_id                      (FK → companies.id — which business entity)
├── payment_method                  (cash / card / transfer)
├── vat_mode                        (automatic / manual — controls which VAT fields are used)
├── vat_rate                        (0% / 5% / 8% / 23%) — automatic mode only; nullable (NULL in manual mode)
├── cash_in_type                    (cash_in only: internal / external) — internal forces vat_rate to 0%, field locked
├── vat_deductible_pct              (cash_out only, automatic mode: 100% / 50% / 0%) — mandatory, default 100%
├── manual_vat_amount               (manual mode: user-entered VAT amount)
├── manual_vat_deductible_amount    (manual mode, cash_out only: deductible portion of manual VAT)
├── customer_type                   (private / company / other — required on all transactions)
├── document_flow                   (invoice / receipt / invoice_and_receipt / other_document — required for external cash_in, optional for cash_out)
├── for_accountant                  (BOOLEAN DEFAULT TRUE — flag for accountant review; internal cash_in forces false)
├── description                     (optional free text; mandatory when category is other_expense or other_income)
├── logged_by                       (FK → users.id)
├── is_active                       (BOOLEAN DEFAULT TRUE — soft-delete flag; reports filter WHERE is_active = TRUE)
├── void_reason                     (mandatory when is_active is set to FALSE)
├── voided_by                       (FK → users.id — who deactivated the row)
├── voided_at                       (TIMESTAMP — when the row was voided)
├── replacement_transaction_id      (FK → transactions.id — points to the correcting transaction)
└── created_at                      (TIMESTAMP — authoritative ordering field)
```

## Settings / Accounts Table

```
opening_balance:    (PLN amount — log once when system starts, never reconstruct later)
as_of_date:         (date opening balance was recorded)
```

**Critical:** Opening balance must be recorded on day 1. Without it a real cash flow statement is impossible.

---

## Hierarchical Categories

Categories use a two-level hierarchy: **parent group → subcategory**. Only leaf nodes (subcategories) are selectable on transactions. Parent groups are used for reporting and analysis grouping.

- 19 parent groups (IDs 1–19, `parent_id = NULL`)
- 62 leaf subcategories (IDs 101–162, `parent_id` references parent)
- Each subcategory carries its own explicit VAT defaults (no inheritance from parent)
- Category names are globally unique slugs with direction prefix convention

### Cash In Parent Groups
| # | Group | Example subcategories |
|---|---|---|
| 1 | Services | Test, Package, Bioresonance, Consultation, etc. |
| 2 | Products | Product Sales, Gift Card Sales |
| 3 | Internal Transfer | Owner Injection, Inter-Company Transfer |
| 4 | Other Income | Refund Received, Insurance Payout, etc. |

### Cash Out Parent Groups
| # | Group | Example subcategories |
|---|---|---|
| 5 | Cost of Services | Materials, Equipment Rental, Subcontractor |
| 6 | Cost of Products | Wholesale Purchase, Packaging |
| 7 | Marketing | Paid Ads, SEO, Print Materials, Events |
| 8 | Rent & Premises | Office Rent, Storage, Coworking |
| 9 | Utilities | Electricity, Internet, Water, Phone |
| 10 | Office & Admin | Office Supplies, Postage, Bank Fees |
| 11 | IT & Software | SaaS Subscriptions, Domains, IT Support |
| 12 | Staff Costs | Salaries, Contractor Fees, Training |
| 13 | Vehicle & Transport | Fuel, Maintenance, Parking, Tolls |
| 14 | Travel | Flights, Hotels, Per Diem |
| 15 | Taxes & Social | ZUS, PIT, VAT Payment, CIT |
| 16 | Insurance | Business Insurance, Vehicle Insurance |
| 17 | Professional Services | Accountant, Legal, Consulting |
| 18 | Renovation | Building Works, Permits |
| 19 | Other Expense | Miscellaneous, Donations, Penalties |

Full taxonomy with subcategory IDs and VAT defaults: see `seed/categories.sql` and `iterations/p1-i8/category-taxonomy.md`.

---

## VAT Logic

### Automatic Mode (default)
Standard behavior — VAT calculated from gross amount and rate.

#### Cash In Transactions
- Use `cash_in_type`: `internal` or `external`
- `cash_in_type = internal` → VAT forced to 0%, gross = net, field locked — this is a hard rule, not a default
- `cash_in_type = external` → VAT defaults to 23%, user can change to 5%, 8%, 0%
- No `vat_deductible_pct` field on cash_in rows
- Always record **gross amount** — VAT is extracted from gross, never added on top

#### Cash Out Transactions
- No `cash_in_type` field on cash_out rows
- `vat_deductible_pct` is mandatory — default 100%, allowed values: 100 / 50 / 0
- Defaults are set by subcategory

### Manual Mode
For mixed-rate invoices or special cases where automatic calculation doesn't apply.

- `vat_rate` is NULL — no sentinel values
- **Cash Out:** user enters `manual_vat_amount` and `manual_vat_deductible_amount`
- **Cash In:** user enters `manual_vat_amount` only
- `manual_vat_deductible_amount` auto-fills from `manual_vat_amount` on first entry; user may override
- Validation: `manual_vat_deductible_amount <= manual_vat_amount`
- Internal cash_in cannot use manual mode

### Internal Cash_In — Consolidated Rules
When `cash_in_type = internal`, all of the following are enforced:

| Field | Behavior |
|-------|----------|
| `vat_mode` | Forced to `automatic` |
| `vat_rate` | Forced to `0` |
| `payment_method` | Forced to `cash` |
| `for_accountant` | Forced to `false` |
| `customer_type` | Forced to `private`, selector hidden |
| `document_flow` | Hidden, not stored (NULL) |
| Manual VAT toggle | Hidden |

### Derived Calculations (never stored)
```
vat_amount       = amount - (amount / (1 + vat_rate / 100))       -- automatic mode
               OR = manual_vat_amount                              -- manual mode

net_amount       = amount - vat_amount
vat_reclaimable  = vat_amount × vat_deductible_pct / 100          -- cash_out, automatic mode
               OR = manual_vat_deductible_amount                   -- cash_out, manual mode
effective_cost   = amount - vat_reclaimable                        -- cash_out only
net_vat_position = SUM(cash_in vat_amount) - SUM(cash_out vat_reclaimable)
```

---

## Procedure Metadata

### customer_type
Required on all transactions. Identifies the counterparty:
- `private` — individual person
- `company` — business entity
- `other` — government, tax office, unknown, non-standard party

### document_flow
Tracks what document supports the transaction:
- `invoice` — standard business invoice
- `receipt` — fiscal receipt (paragon)
- `invoice_and_receipt` — both issued (only allowed when customer_type = private)
- `other_document` — other supporting document

Rules: required for external cash_in (default: `receipt`), optional for cash_out, hidden for internal cash_in.

### for_accountant
Boolean flag indicating whether the transaction needs accountant review. Default: `true`. Internal cash_in forces `false`. Correction form preserves the stored value.

---

## Card Payment Reconciliation

### The Problem
- Sale: 3000 PLN recorded as cash_in (card)
- Bank deposit: 2970 PLN (card company keeps 30 PLN commission)
- End of month: card company sends invoice for total commissions (e.g. 450 PLN)

### The Correct Approach
**Always log gross sale amount.** Handle commission as a separate cash_out transaction.

```
Transaction 1 — point of sale
├── amount:           3000 PLN  ← GROSS, never 2970
├── direction:        cash_in
├── payment_method:   card
└── vat_rate:         23%

Transaction 2 — end of month from terminal invoice
├── amount:           450 PLN
├── direction:        cash_out
├── category:         bank_fees (under Office & Admin group)
├── vat_rate:         23%
└── vat_deductible_pct: 100%
```

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
- Internal financial statements (Phase 7) are for owner visibility only, not for submission anywhere

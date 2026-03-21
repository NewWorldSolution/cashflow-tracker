# Reporting Structure

## Phase 2 — Weekly / Monthly Cash Report

### Monthly Income Block
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
```

### Monthly Expenses Block
```
Monthly Expenses
──────────────────────────────────────
  Card terminal fees:         360 PLN  (100% VAT deductible)
  Petrol:                     800 PLN  (50% VAT deductible)
  Other:                    1,300 PLN  (100% VAT deductible)
  Total:                    2,460 PLN
  VAT reclaimable:            460 PLN
```

### Summary Block
```
Net VAT position:           2,385 PLN  (collected - reclaimable)
Net cash position:         16,040 PLN
```

---

## Phase 3 — Internal Financial Statements (future)

### P&L Statement
```
Income vs expenses by category
Month over month comparison
```

### Cash Flow Statement
```
Opening balance (from settings table)
+ Total income
- Total expenses
= Closing balance
```
Requires `opening_balance` set on day 1 — otherwise statement is impossible to produce correctly.

### VAT Summary
```
VAT collected (from income transactions)
- VAT reclaimable (from expense transactions × vat_deductible_pct)
= Net VAT position (amount owed to tax authority)
```

---

## Derived Calculations
These are never stored — always computed at query time:

| Field | Formula |
|---|---|
| `vat_amount` | `amount - (amount / (1 + vat_rate/100))` |
| `net_amount` | `amount - vat_amount` |
| `vat_reclaimable` | `vat_amount × vat_deductible_pct / 100` (expenses only) |
| `net_vat_position` | `sum(income vat_amount) - sum(expense vat_reclaimable)` |
| `net_cash_position` | `opening_balance + total_income - total_expenses` |

---

## WBSB Monday Report Integration
- WBSB reads from cashflow DB via new data loader adapter
- Report delivered every Monday via existing I9 delivery pipeline (Teams/Slack/email)
- Report covers the previous week's transactions
- Same structured brief format as current WBSB reports

---
# Report Writer
Status: active
Layer: cash-flow
Purpose: Know how to produce correct financial reports from the cashflow database.
---

## Non-negotiable query rules
1. Always filter `WHERE is_active = TRUE` — voided transactions must never appear in any report
2. Always derive VAT values at query time — they are never stored in the database
3. Always `ORDER BY created_at` when row ordering matters — never by `date` alone
4. Group expenses by `categories.label` (joined from the categories table) — never by free-text

## Derived calculation formulas (from docs/architecture.md)
```
vat_amount       = amount - (amount / (1 + vat_rate / 100))
               OR = manual_vat_amount  (if advanced mode was used on that transaction)

net_amount       = amount - vat_amount
vat_reclaimable  = vat_amount × vat_deductible_pct / 100   (expense rows only)
effective_cost   = net_amount + (vat_amount × (1 - vat_deductible_pct / 100))
net_vat_position = SUM(income vat_amount) - SUM(expense vat_reclaimable)
net_cash_position = opening_balance + total_income - total_expenses
```

## Opening balance dependency
- Cash flow statement requires `opening_balance` from the settings table
- If `opening_balance` is not set: block the cash flow statement — do not produce a partial or zero-based result
- All other reports (income summary, expense summary, VAT summary) can run without it

## Report structure (from docs/reporting.md)
Monthly output has three blocks:
1. Income block — by payment method and by VAT rate
2. Expense block — by category label, with deductibility noted
3. Summary block — net VAT position, net cash position

Output format: Jinja2 templates → Markdown or HTML

## Does NOT
- Store any calculated value — calculations are always at query time
- Apply different formulas for SQLite vs PostgreSQL — the same SQL runs on both

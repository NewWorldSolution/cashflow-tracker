---
# Form Logic
Status: active
Layer: cash-flow
Purpose: Know all web form behaviour rules — what fields appear, when, and what defaults are set.
---

## Role
Define the smart behaviour of the transaction entry form. Every rule here applies to both the client-side UI and server-side validation — they must be consistent.

## Field visibility rules
| Field | Shown when |
|---|---|
| `income_type` | `direction = income` only |
| `vat_deductible_pct` | `direction = expense` only |
| `manual_vat_amount` | Only when user explicitly enables advanced VAT mode (hidden by default) |
| `description` (required indicator) | Category is `other_expense` or `other_income` |

## Auto-default rules (triggered on category selection)
- Selecting a category auto-fills `vat_rate` from `categories.default_vat_rate`
- Selecting an expense category auto-fills `vat_deductible_pct` from `categories.default_vat_deductible_pct`
- User can override both — auto-default is a suggestion, not a lock (except the internal rule below)

## Field locking rules
- `income_type = internal` (or category = `internal_transfer`) → `vat_rate` is forced to 0 and the field is greyed out — user cannot change it
- This lock is enforced in the UI AND validated on the server — client-side lock alone is not sufficient

## Required guardrails (Phase 1 — not optional)
These must be present from day 1. They are not nice-to-haves.

1. **Gross amount reminder** — persistent label on the amount field at all times: `"Enter gross amount (VAT included)"`
2. **Card payment reminder** — shown when `payment_method = card`: `"Log gross amount. Card commission is logged separately at month end from terminal invoice"`
3. **Category auto-defaults** — described above; must fire on every category change

## Does NOT
- Define validation rules (see transaction_validator skill)
- Define error display behaviour (see error_handling skill)
- Apply to the Telegram bot or LLM extraction layer

---
# Transaction Validator
Status: active
Layer: cash-flow
Purpose: Know and enforce every domain rule for transaction data. Used by every component that reads or writes transactions.
---

## Role
This skill is the single source of truth for what makes a transaction valid. The web form, Telegram bot, and LLM extractor all enforce these same rules. If a rule is here, it is not optional.

## Validation rules — all mandatory

### Amount
- Always stored as gross — the actual cash amount paid or received
- Never net. VAT is extracted from gross at query time, never added on top.

### Category
- `category_id` is always an integer FK referencing `categories.category_id`
- Free-text category names are never valid — not in input, not in storage
- The category list is fixed: 4 income categories, 18 expense categories (defined in docs/concept.md)

### VAT rate
- Valid values: 0, 5, 8, 23
- Validated in application code — no database CHECK constraint
- If `income_type = internal`: vat_rate must be 0. Any other value is rejected. This is a hard rule.

### Income type
- Applies to income rows only. Must be absent (NULL) on expense rows.
- Values: `internal` or `external`
- `internal` → vat_rate forced to 0, cannot be overridden by user or any process

### VAT deductible percentage
- Applies to expense rows only. Must be absent (NULL) on income rows.
- Mandatory on every expense row — NULL is not permitted
- Default: 100. Allowed values: 0, 50, 100

### Description
- Available on all transactions
- Mandatory (non-empty string) when category is `other_expense` or `other_income`
- Optional on all other categories

### Identity
- `logged_by` must be a `users.id` integer FK — never a name string
- `voided_by` must be a `users.id` integer FK when present — never a name string

### Soft-delete
- Transactions are never hard-deleted
- To deactivate: set `is_active = FALSE`, provide non-empty `void_reason`, provide `voided_by` (users.id)
- All three fields are required together — a deactivation without void_reason or voided_by is rejected

## Does NOT
- Define how errors are shown to the user (see error_handling skill)
- Define form field visibility (see form_logic skill)
- Define how identity is resolved (see auth_logic skill)

---
# Telegram Handler
Status: active
Layer: cash-flow
Purpose: Know the Telegram bot conversation rules, identity model, and command handling.
---

## Identity and access control
- On every incoming message: check sender's Telegram user ID against `users.telegram_user_id`
- No match found → ignore the message — no response, no error, no logging
- Match found → resolve to `users.id` → this becomes `logged_by` for any transaction created in this session
- Telegram user IDs are stored in the `users` table, not in settings

## Confirmation rule — mandatory, not optional
Before saving any transaction:
1. Show the extracted or entered fields to the user in readable form
2. Ask for explicit confirmation
3. Only after confirmation: run validation → save

Do not save on the first message. The confirmation step cannot be skipped.

## Commands (Phase 5)
- **Log a transaction** — user describes the transaction; bot extracts and confirms before saving
- **Query balance or recent transactions** — read-only; no confirmation needed
- **Correct last entry** — bot shows the last transaction and asks what to change; applies as soft-delete + new transaction after confirmation

## Correction flow
Corrections are soft-deletes, not overwrites:
1. Identify the transaction (by `created_at DESC`, not `date`)
2. Show it to the user and confirm what needs to change
3. Set the original `is_active = FALSE`, provide `void_reason`, `voided_by`
4. Create a new correcting transaction
5. Link via `replacement_transaction_id` on the voided row

## Group behaviour
- All 3 users (owner, assistant, wife) are in one group
- Everyone sees all confirmations and responses — passive audit trail by design
- Any member can log a transaction or ask a query

## Does NOT
- Handle LLM extraction logic (see llm_extractor skill)
- Define the identity setup process — `telegram_user_id` values are populated manually before Phase 5 goes live

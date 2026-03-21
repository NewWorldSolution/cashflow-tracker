---
# Auth Logic
Status: active
Layer: cash-flow
Purpose: Know the authentication model and how user identity flows through the system.
---

## Users
3 fixed accounts: owner, assistant, wife. This is not a SaaS product — no registration, no public access.

## Web form (Phase 1)
- Username + password login page
- Session-based: on successful login, `users.id` is stored in the session
- Every transaction created via the web form sets `logged_by = users.id` from the session
- `logged_by` is never typed by the user and never derived from a name string

## Telegram bot (Phase 5)
- No separate login — identity is resolved from Telegram metadata
- Each user's Telegram user ID is stored in `users.telegram_user_id` (nullable column, set up before Phase 5 goes live)
- On every incoming message: check sender's Telegram user ID against `users.telegram_user_id`
  - Match found → resolve to `users.id` → use as `logged_by` for any transaction
  - No match → ignore the message silently — no response, no error
- Telegram user ID is part of the user model (`users` table), not the settings table

## Identity contract (both channels)
- Both channels resolve to the same `users.id`
- `logged_by` is always an integer FK to `users.id`
- `voided_by` follows the same rule — always `users.id`, never a name

## Does NOT
- Define session storage implementation details
- Define password hashing algorithm (use a standard library — bcrypt or equivalent)
- Apply to the LLM extraction layer (identity in Phase 6 still comes from Telegram, same as Phase 5)

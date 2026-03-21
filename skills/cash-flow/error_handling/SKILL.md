---
# Error Handling
Status: active
Layer: cash-flow
Purpose: Define how validation failures and errors are surfaced across all input channels.
---

## Core principle
From CLAUDE.md: **No silent failures. Every validation error surfaces explicitly.**

## Rules

### General
- A transaction with any validation failure must not be saved — partial saves are not permitted
- Errors are never silently swallowed, logged-only, or converted to defaults without user knowledge
- Ambiguous input (e.g. missing description on `other_expense`) blocks the save and prompts the user — a silent default is never applied

### Web form
- Show errors inline, adjacent to the field that caused the failure
- The form must not reset — user's input is preserved so they can correct the specific field
- All errors from a single submission are shown together — do not show one at a time

### Telegram bot
- Respond with a clear plain-text error message before asking for correction
- State specifically what failed — not a generic "something went wrong"
- Do not save anything until the corrected input has been confirmed

### LLM extraction layer (Phase 6)
- If extracted fields fail validation, show the user exactly which fields failed and why
- Ask for correction before attempting to save
- Do not silently drop the invalid fields and save the rest

## Does NOT
- Define infrastructure error handling (network failures, DB connection errors) — out of scope
- Define the specific wording of error messages — that is implementation detail

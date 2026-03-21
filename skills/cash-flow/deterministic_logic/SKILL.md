---
# Deterministic Logic
Status: active
Layer: cash-flow
Purpose: Extend generic/deterministic_logic with cashflow-specific layer boundaries.
---

## Extends
`skills/generic/deterministic_logic/SKILL.md` — read that first.

## Layers that are LLM-free in this project (no exceptions)
- Transaction validation (all rules in transaction_validator skill)
- VAT calculation (all formulas defined in docs/architecture.md)
- Report generation and aggregation (all logic in report_writer skill)
- Web form field logic and locking rules
- Auth and identity resolution
- All database reads and writes

## The only LLM layer in this project
Phase 6 only:
- Claude Haiku: natural language message → transaction fields (via function calling)
- Claude Sonnet: photo or receipt image → transaction fields (via vision)

Even in Phase 6, the LLM does not validate or save. It extracts only.
The sequence is always: LLM extracts → user confirms → application validates → application saves.

## Does NOT
- Change or extend the generic rule that LLM output must be validated before saving
- Apply to any phase before Phase 6

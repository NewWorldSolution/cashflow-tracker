---
# LLM Extractor
Status: active
Layer: cash-flow
Purpose: Know how the LLM extraction layer works — model selection, prompt strategy, and the confirmation loop.
---

## Scope
This skill applies to Phase 6 only. No LLM extraction exists before Phase 6.

## Model selection
| Input type | Model | Reason |
|---|---|---|
| Text message (natural language) | Claude Haiku | Fast and near-free; function calling |
| Photo or image (receipt, bank statement) | Claude Sonnet | Vision capability required |
| CSV / XLSX bank export | No LLM | Deterministic parsing — no model needed |

## Function calling rules
- Always use function calling / tool use — never free-form text output
- The output schema must match transaction fields exactly
- Fixed reference lists must be in the system prompt:
  - Category names (all 22: 4 income + 18 expense)
  - Valid VAT rates: 0, 5, 8, 23
  - Valid payment methods: cash, card, transfer
  - Valid income types: internal, external
- `logged_by` is resolved from Telegram identity — it is never parsed from the message content

## The confirmation loop (mandatory)
```
1. User sends message or photo
2. LLM extracts fields via function calling
3. Bot shows extracted fields to the user in readable form
4. User confirms or corrects
5. Application validates using transaction_validator rules
6. If validation passes: save
7. If validation fails: show what failed, ask for correction — return to step 4
```
The LLM is only in steps 1–2. The application owns everything from step 3 onward.

## LLM output is never saved directly
- Extraction output always goes through transaction_validator before any write
- If the LLM returns an invalid category name: reject and ask for correction — do not guess the category_id
- If the LLM returns income_type = internal with vat_rate ≠ 0: correct vat_rate to 0, inform the user

## Does NOT
- Skip the confirmation step under any circumstance
- Allow LLM to determine whether a transaction is valid — that is application code only
- Apply before Phase 6

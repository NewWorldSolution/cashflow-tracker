---
# Deterministic Logic
Status: active
Layer: generic
Purpose: Enforce the principle that all business logic must be deterministic code, never LLM.
---

## Core rule
LLM is for language. Business logic, financial calculations, and data validation are deterministic code. These two layers must never merge.

## Permitted LLM use
- Natural language → structured data extraction
- Image / photo → structured data extraction
- In both cases: LLM output must be validated by application code before any state change

## Prohibited LLM use
- Validation of any kind
- Financial or mathematical calculation
- Reporting or aggregation
- Deciding whether to save or reject a record
- Any logic where the same input must always produce the same output

## The correct pattern
```
LLM extracts → application validates → application calculates → application stores
```
The LLM touches the input. The application owns everything after.

## Does NOT
- Define project-specific calculation rules (see project-level deterministic_logic skill)
- Apply to UI text, error messages, or display formatting

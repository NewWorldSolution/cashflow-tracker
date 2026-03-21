# Agents & Skills Planning

## Purpose of This Document
This is the foundation document for designing the subagent structure to build the Cash Flow Tracker agenetically.
The actual agent/skill creation comes after this project knowledge base is established.

---

## What Needs to Be Built (Full Scope)

Based on the concept and architecture docs, the system has these distinct domains:

### 1. Data Layer
- SQLite / PostgreSQL schema
- Migration scripts
- Transaction CRUD
- Settings table

### 2. Web Form (Phase 1)
- Backend: Python (Flask or FastAPI)
- Form rendering with smart defaults
- VAT logic (client-side or server-side)
- Input validation

### 3. Reporting Engine (Phase 2)
- SQL queries → aggregate metrics
- Report rendering (Jinja2 templates)
- VAT calculations (derived, never stored)
- Card reconciliation check

### 4. WBSB Integration (Phase 4)
- New data loader adapter for WBSB
- Cashflow DB → WBSB-compatible structure
- Monday report trigger

### 5. Telegram Bot (Phase 5)
- python-telegram-bot setup
- Group chat handling
- Command routing (log / query / correct)
- Confirmation flow before save

### 6. LLM Extraction Layer (Phase 6)
- Haiku function-calling integration
- System prompt with fixed categories + VAT rates
- Confirmation UX loop
- Sonnet for image/photo input

---

## Candidate Roles for Subagents

These are draft roles — to be refined before building:

| Role | Responsibility |
|---|---|
| **architect** | Design decisions, schema, module boundaries, integration contracts |
| **builder** | Implement code within defined boundaries (one task at a time) |
| **qa_agent** | Write and run tests, validate edge cases (VAT rounding, zero-balance, card reconciliation) |
| **data_modeler** | Own the transaction schema, migrations, derived calculations spec |
| **form_designer** | Web form UX, smart defaults, validation rules, VAT field behaviour |
| **reporting_agent** | SQL query design, Jinja2 templates, report output format |
| **telegram_agent** | Bot setup, conversation flow, confirmation UX |
| **llm_extraction_agent** | Function-calling prompt design, Haiku/Sonnet model strategy, confirmation loop |
| **wbsb_integration_agent** | WBSB data loader adapter, Monday delivery trigger |
| **code_reviewer** | Review PRs within architecture constraints |

---

## Key Domain Rules Every Agent Must Know

1. **Always gross amounts** — never net. VAT extracted, not added.
2. **Opening balance is sacred** — must be set day 1; never reconstructed.
3. **Card commissions are separate expense transactions** — never subtract from sale amount.
4. **VAT deductibility varies by category** — petrol/car 50%, meals/entertainment 0%, most others 100%. Defaults are driven by `category_id`; never hardcode per free-text name.
5. **`income_type = internal` always forces `vat_rate = 0%`** — this is a hard rule, not a default. The field is locked in both UI and backend.
6. **All derived calculations are computed, never stored** — vat_amount, net_amount, vat_reclaimable, effective_cost.
7. **Scope boundary: no tax advice, no submission to authorities** — internal tool only.
8. **Soft-delete only — no hard deletes ever.** Deactivating a transaction requires `void_reason` (mandatory) and `voided_by` (FK to users.id). All reports filter `WHERE is_active = TRUE`. Admin view shows full history.
9. **`category_id` is always a FK reference — never free text.** The category list is fixed (4 income, 18 expense categories). Agents must use `category_id` when constructing or validating transactions. Free-text category strings are not valid.
10. **Description is mandatory on "other" categories** — `other_expense` and `other_income` require a non-empty description field. Optional on all other categories.

---

## Next Steps (to do before creating agents)
1. Decide: global (`~/.claude/`) vs project-level (`.claude/`) skill structure
2. Define the SKILL.md format for each role
3. Map which phases each agent is responsible for
4. Define handoff protocol between agents
5. Create CLAUDE.md for the cashflow-tracker project (architecture rules, what agents must not do)

---

## Connection to Agentic Framework Vision
This project will follow the same pattern as planned in the generic agentic framework:
- Generic skills: architect, builder, qa_agent, code_reviewer
- Domain skills (cashflow-specific): data_modeler, form_designer, reporting_agent, telegram_agent, llm_extraction_agent, wbsb_integration_agent

See WBSB memory: `agentic_framework_vision.md` for the full framework structure.

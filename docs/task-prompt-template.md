# cashflow-tracker Task Prompt — {{TASK_ID}}: {{TASK_TITLE}}

<!--
HOW TO USE THIS TEMPLATE
========================
1. Copy this file. Rename it (e.g. `prompt-p1-i1.md`).
2. Replace every {{PLACEHOLDER}} with the real value.
3. Fill in every section marked with a [FILL IN] comment.
4. Remove all comments (<!-- ... -->) before sending to the AI.
5. Sections marked [BOILERPLATE] are fixed — do not change them.
6. Send the completed file as the full prompt.

PLACEHOLDER KEY
  {{TASK_ID}}           e.g. P1-I1
  {{TASK_TITLE}}        e.g. Foundation — Schema, Seed Data, Auth
  {{PHASE}}             e.g. Phase 1 — Web Form
  {{ITERATION}}         e.g. Iteration 1 — Foundation
  {{FEATURE_BRANCH}}    e.g. phase-1/iteration-1
  {{DEPENDS_ON}}        e.g. none | P1-I1
  {{BLOCKS}}            e.g. P1-I2 | none
  {{TEST_COUNT}}        current passing test count (0 at start)
-->

---

## Project Context
<!-- [BOILERPLATE] — do not change this section -->

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/validation.py → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores the actual gross cash; VAT is extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or any reporting layer |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly; block the save, never default silently |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost` are computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point; route handlers and templates call it, never re-implement it |

---

## Repository State
<!-- [FILL IN] Update these values at task start -->

- **Feature branch for this task:** `{{FEATURE_BRANCH}}`
- **Tests passing:** {{TEST_COUNT}}
- **Ruff:** clean
- **Last completed task:** <!-- e.g. none / P1-I1 — Foundation complete -->
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | {{TASK_ID}} |
| Title | {{TASK_TITLE}} |
| Phase | {{PHASE}} |
| Iteration | {{ITERATION}} |
| Feature branch | `{{FEATURE_BRANCH}}` |
| Depends on | {{DEPENDS_ON}} |
| Blocks | {{BLOCKS}} |
| PR scope | One PR per iteration into `main`. Do not combine iterations. Do not push partial work. |

---

## Task Goal
<!-- [FILL IN] One or two paragraphs. What problem does this task solve and why does it matter?
Be specific — reference the module, endpoint, or gap being closed. -->

{{GOAL_PARAGRAPH}}

---

## Files to Read Before Starting
<!-- [BOILERPLATE — mandatory block] + [FILL IN — task-specific block] -->

### Mandatory — read these for every task, in this order

```
CLAUDE.md                                              ← constitution — read first, always
project.md                                             ← current state and what this iteration delivers
skills/cash-flow/schema/SKILL.md                       ← full table structure and SQLite/PG boundary rules
skills/cash-flow/transaction_validator/SKILL.md        ← all 10 domain rules — the single source of truth
skills/cash-flow/error_handling/SKILL.md               ← no silent failures, inline errors, block on any failure
```

### Task-specific — add the skills relevant to this iteration

<!-- [FILL IN] Choose from the list below. Remove skills not relevant to this task. -->

```
{{SKILL_OR_FILE_1}}     ← reason
{{SKILL_OR_FILE_2}}     ← reason
{{SKILL_OR_FILE_3}}     ← reason
```

<!-- Available skills — pick what applies:
skills/cash-flow/auth_logic/SKILL.md         → tasks involving login, session, identity (Iteration 1–2)
skills/cash-flow/form_logic/SKILL.md         → tasks involving the web form, field defaults, guardrails (Iteration 3)
skills/cash-flow/deterministic_logic/SKILL.md → tasks involving any calculation or validation logic
skills/cash-flow/report_writer/SKILL.md      → tasks involving queries, aggregations, VAT calculations (Phase 2+)
skills/cash-flow/telegram_handler/SKILL.md   → tasks involving the Telegram bot (Phase 5)
skills/cash-flow/llm_extractor/SKILL.md      → tasks involving LLM extraction (Phase 6)
skills/generic/qa_runner/SKILL.md            → tasks that include writing or auditing tests
skills/generic/code_reviewer/SKILL.md        → review tasks only

Also consider reading adjacent code files if they already exist:
app/services/validation.py    ← if it exists — do not re-implement rules already there
app/models/                   ← if models exist — understand the contracts before touching
-->

---

## Existing Code This Task Builds On
<!-- [FILL IN] Describe what already exists that this task depends on.
This prevents the AI from reinventing things that already exist. -->

### Already exists and must NOT be reimplemented:

```python
# {{FILE}} — example entries, replace with real ones

{{existing_function_or_class}}
```

### Contracts established by prior tasks that this task must respect:

```
{{CONTRACT_1}}     ← e.g. services/validation.py is the only place validation rules live
{{CONTRACT_2}}     ← e.g. logged_by is always set from session['user_id'], never from form input
```

---

## What to Build
<!-- [FILL IN] The most important section. Be exhaustive.
Do NOT leave implementation decisions open-ended. Specify them here. -->

### New files

```
{{NEW_FILE_1}}     ← purpose
{{NEW_FILE_2}}     ← purpose
```

### Modified files

```
{{MODIFIED_FILE_1}}  ← what changes and why
```

### Public API

<!-- [FILL IN] Define every public function, class, and route this task must produce.
Use Python type annotations. Include FastAPI route decorators where applicable. -->

```python
# {{NEW_FILE_1}}

@router.{{method}}("{{path}}")
async def {{function_name}}(
    {{param_1}}: {{type}},
    {{param_2}}: {{type}},
    session: dict = Depends(get_session),
) -> {{return_type}}:
    """{{docstring}}

    Args:
        {{param_1}}: {{description}}

    Returns:
        {{description}}

    Raises:
        HTTPException(400): {{when}}
        HTTPException(401): when user is not authenticated
    """
```

### Data shapes

<!-- [FILL IN] Define Pydantic models or TypedDicts used across module boundaries. -->

```python
class {{ModelName}}(BaseModel):
    field_one: str          # e.g. void_reason — mandatory when voiding
    field_two: int          # e.g. category_id — FK reference, never text
    field_three: float | None = None  # e.g. manual_vat_amount — advanced mode only
```

### Behaviour rules

<!-- [FILL IN] Specific rules the implementation must enforce. Be explicit about failure modes. -->

- **Rule 1:** e.g. `income_type = internal` → `vat_rate` is forced to 0; reject any other value at the API level
- **Rule 2:** e.g. Expense row submitted without `vat_deductible_pct` → reject with descriptive error; never save with NULL
- **Rule 3:** e.g. `logged_by` is always set from `session['user_id']` — never accepted from the request body
- **Rule 4:** e.g. Seed script runs with `INSERT OR IGNORE` — safe to run twice without creating duplicates

### Input/output examples

```python
# Example: POST /transactions — valid income
POST /transactions
{
    "date": "2026-03-21",
    "amount": 1230.00,
    "direction": "income",
    "category_id": 1,
    "payment_method": "card",
    "vat_rate": 23,
    "income_type": "external"
}
# → 201 Created, transaction saved

# Example: POST /transactions — internal income with wrong VAT
POST /transactions
{
    "income_type": "internal",
    "vat_rate": 23,
    ...
}
# → 400 Bad Request: "income_type=internal requires vat_rate=0"
```

---

## Architecture Constraints
<!-- [BOILERPLATE] — do not change this section -->

These apply to every task without exception. No PR is approved if any of these are violated.

1. **Gross amounts always** — store the actual gross cash amount. Never net. VAT is derived at query time.
2. **Deterministic logic** — no LLM calls in validation, calculation, or reporting. All financial logic is deterministic Python.
3. **Soft-delete only** — never use SQL DELETE on transactions. Deactivation = `is_active = FALSE` + mandatory `void_reason` + `voided_by` (users.id).
4. **category_id is always FK** — never accept free-text category names. Always validate against the categories table.
5. **No silent failures** — never catch an error and return a default. Raise HTTPException with a descriptive message.
6. **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs from `users.id`. Never name strings.
7. **Derived values never stored** — do not add columns for `vat_amount`, `net_amount`, `vat_reclaimable`, or `effective_cost`.
8. **Validation in service layer** — `services/validation.py` is the single enforcement point. Route handlers call it; they do not reimplement rules.

---

## Allowed Files
<!-- [FILL IN] Complete and exhaustive list. Only these files may be created or modified.
If the implementation requires touching a file not on this list, STOP and ask. -->

```
{{FILE_PATH_1}}     ← new | modify: {{why}}
{{FILE_PATH_2}}     ← new | modify: {{why}}
{{FILE_PATH_3}}     ← new | modify: {{why}}
```

---

## Files NOT to Touch
<!-- [FILL IN] Files adjacent to the work that must NOT be modified. -->

The following files are adjacent to this task but must not be modified:

```
{{ADJACENT_FILE_1}}    ← reason: e.g. owned by next iteration (P1-I2)
{{ADJACENT_FILE_2}}    ← reason: e.g. schema is frozen until go-live
```

If any of these seem like they need to change to complete this task, **stop and raise it** rather than modifying them.

---

## Acceptance Criteria
<!-- [FILL IN] Checkable, binary criteria. Each item must be true for the PR to merge.
Avoid vague criteria like "works correctly" — specify what correct means. -->

- [ ] {{Criterion 1}} — e.g. `db/init_db.py` runs twice without error or duplicate rows
- [ ] {{Criterion 2}} — e.g. Submitting expense without `vat_deductible_pct` returns 400, not 200 with NULL
- [ ] {{Criterion 3}} — e.g. `logged_by` in every saved transaction is a valid integer FK — verified by direct DB query
- [ ] All {{TEST_COUNT}}+ existing tests still pass — `pytest` exit code 0
- [ ] Ruff clean — `ruff check .` exit code 0

---

## Tests Required
<!-- [FILL IN] Specific test cases. Each row = one test function.
Name tests descriptively: test_<subject>_<condition>_<expected>
All new tests go in {{TEST_FILE}}. -->

**Test file:** `{{TEST_FILE}}`

| Test function | What it verifies |
|---------------|-----------------|
| `test_{{subject}}_{{condition}}` | {{expected behaviour in plain English}} |
| `test_{{subject}}_{{condition}}` | {{expected behaviour in plain English}} |

<!-- Test patterns for this project: -->

```python
# Pattern: route handler test with TestClient
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_example_rejects_invalid_input():
    # Arrange — log in first
    client.post("/auth/login", data={"username": "owner", "password": "test"})

    # Act
    response = client.post("/transactions", json={
        "income_type": "internal",
        "vat_rate": 23,  # invalid — must be 0 for internal
        ...
    })

    # Assert
    assert response.status_code == 400
    assert "vat_rate" in response.json()["detail"]
```

```python
# Pattern: service-layer unit test
from app.services.validation import validate_transaction

def test_validate_rejects_internal_income_with_nonzero_vat():
    with pytest.raises(ValueError, match="income_type=internal requires vat_rate=0"):
        validate_transaction({
            "income_type": "internal",
            "vat_rate": 23,
            ...
        })
```

---

## Edge Cases to Handle Explicitly
<!-- [FILL IN] Cases most likely to be silently ignored without this prompt. -->

| Edge case | Expected behaviour |
|-----------|-------------------|
| `income_type = internal` with `vat_rate ≠ 0` | Rejected with 400; error names the field |
| Expense row with `vat_deductible_pct = NULL` | Rejected with 400; never saved |
| `other_expense` with empty description | Rejected with 400; description is mandatory |
| `category_id` that does not exist in categories table | Rejected with 400; FK violation surfaced |
| Void without `void_reason` | Rejected with 400; row not deactivated |
| Seed script run twice | No duplicate rows; `INSERT OR IGNORE` used throughout |
| {{Edge case specific to this task}} | {{expected}} |

---

## What NOT to Do
<!-- [FILL IN] Common mistakes to pre-empt. Be specific to this task. -->

- Do not validate in route handlers or templates — `services/validation.py` is the only enforcement point
- Do not store `vat_amount`, `net_amount`, or any other derived value in the database
- Do not accept `category` as a text string — only `category_id` (integer FK)
- Do not set `logged_by` from the request body — always from `session['user_id']`
- Do not use SQL DELETE on any transaction row — soft-delete only
- Do not add a JavaScript framework — vanilla JS only, form behaviour only
- Do not modify files outside the allowed list, even if you notice improvements
- Do not add `except: pass` or any silent exception swallowing

---

## Handoff: What the Next Task Needs From This One
<!-- [FILL IN] Describe the contract this task establishes for tasks that depend on it. -->

After this task merges, the following will be available for `{{BLOCKS}}`:

```python
# {{WHAT_IS_EXPORTED}}
# e.g. from app.services.validation import validate_transaction
# e.g. Database tables: users, categories, transactions, settings, settings_audit

# Contract:
# - validate_transaction(data: dict) raises ValueError with descriptive message on failure
# - session['user_id'] always contains users.id (integer) after successful login
```

---

## Execution Workflow
<!-- [BOILERPLATE] — do not change this section -->

Follow this sequence exactly. Do not skip or reorder steps.

### Step 0 — Branch setup and draft PR (before anything else)

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Confirm the working tree is clean
git status
# Expected: "nothing to commit, working tree clean"
# If not clean: stop and resolve before continuing

# 3. Create and switch to the feature branch
git checkout -b {{FEATURE_BRANCH}}

# 4. Confirm you are on the right branch
git branch --show-current
# Expected: {{FEATURE_BRANCH}}

# 5. Push the branch immediately
git push -u origin {{FEATURE_BRANCH}}

# 6. Open a DRAFT PR before writing any code
gh pr create \
  --base main \
  --head {{FEATURE_BRANCH}} \
  --title "{{TASK_ID}}: {{TASK_TITLE}}" \
  --body "Work in progress. See iteration plan for full task spec." \
  --draft
# Expected: GitHub URL of the new draft PR
```

### Step 1 — Verify the baseline

```bash
pytest
# Expected: all {{TEST_COUNT}}+ tests passing, exit code 0

ruff check .
# Expected: no issues, exit code 0
```

If either fails: stop. Do not proceed until the baseline is clean.

### Step 2 — Read before writing

Read all files listed in "Files to Read Before Starting" in order. Do not write a line of implementation until you understand the existing code.

### Step 3 — Plan before multi-file changes

If this task touches more than 2 files, present the full plan (which files, what changes, in what order) before implementing. Wait for confirmation.

### Step 4 — Confirm allowed files

Before editing any file, cross-check against the "Allowed Files" list. If a file you need is not on the list, **stop and ask**.

### Step 5 — Implement

Write code that satisfies all acceptance criteria and handles all edge cases.

### Step 6 — Test and lint

```bash
pytest
# Must pass: all prior tests + all new tests. Zero failures.

ruff check .
# Must be clean. Fix all issues before committing.
```

Do not submit if either command fails.

### Step 7 — Verify scope

```bash
git diff --name-only main
```

Every file in the output must appear in the "Allowed Files" list. Revert any unexpected file before committing.

### Step 8 — Commit and mark PR ready

```bash
# Commit with the format below
git commit -m "..."

# Mark the draft PR ready for review
gh pr ready {{FEATURE_BRANCH}}
```

Add a summary comment to the PR: what was built, what was tested, any decisions made. Do not merge — merging is a human decision.

---

## Commit Message Format
<!-- [BOILERPLATE] — do not change this section -->

```
{{type}}: {{concise imperative description}} ({{TASK_ID}})

{{Body: what was built and why. One paragraph.
Reference the task ID. Mention key design decisions and behaviour rules enforced.}}

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**Types:** `feat` (new code), `fix` (bug), `test` (tests only), `docs` (docs only), `refactor` (no behaviour change)

**Example:**
```
feat: foundation schema, seed data, and auth (P1-I1)

Creates db/schema.sql (5 tables), idempotent seed via INSERT OR IGNORE,
and FastAPI auth routes. Session stores users.id (integer FK) — never
a name string. Opening balance setup screen hard-blocks the transaction
form until opening_balance exists in settings. SANDBOX banner added to
base template.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## Definition of Done
<!-- [FILL IN] Copy from Acceptance Criteria and add the boilerplate items below. -->

This task is complete when ALL of the following are true:

- [ ] {{Criterion 1}}
- [ ] {{Criterion 2}}
- [ ] All {{TEST_COUNT}}+ prior tests still pass (`pytest` exit code 0)
- [ ] All new tests listed in "Tests Required" pass
- [ ] Ruff clean (`ruff check .` exit code 0)
- [ ] Only files in "Allowed Files" were modified (`git diff --name-only main`)
- [ ] Feature branch pushed, draft PR opened, marked ready for review
- [ ] No `except: pass`, no hard deletes, no free-text categories, no stored derived values

---

<!--
CHECKLIST BEFORE SENDING
=========================
[ ] All {{PLACEHOLDER}} values replaced
[ ] "Files to Read Before Starting" is specific and ordered
[ ] "What to Build" includes actual function signatures and data shapes
[ ] "Allowed Files" is complete and exhaustive
[ ] "Files NOT to Touch" lists obvious adjacent files
[ ] "Handoff" filled in if BLOCKS is not "none"
[ ] All [FILL IN] comments removed
[ ] All [BOILERPLATE] sections unchanged
[ ] Template instructions and this checklist removed before sending
-->

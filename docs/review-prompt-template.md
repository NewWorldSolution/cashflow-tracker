# cashflow-tracker Review Prompt — {{TASK_ID}}: {{TASK_TITLE}}

<!--
HOW TO USE THIS TEMPLATE
========================
1. Copy this file. Rename it (e.g. `review-p1-i1.md`).
2. Replace every {{PLACEHOLDER}} with the real value.
3. Fill in every section marked with a [FILL IN] comment.
4. Remove all comments (<!-- ... -->) before sending to the AI reviewer.
5. Sections marked [BOILERPLATE] are fixed — do not change them.
6. Send the completed file as the full prompt to the reviewing AI.
   Use a DIFFERENT AI than the one that implemented the task.

PLACEHOLDER KEY
  {{TASK_ID}}             e.g. P1-I1
  {{TASK_TITLE}}          e.g. Foundation — Schema, Seed Data, Auth
  {{PHASE}}               e.g. Phase 1 — Web Form
  {{ITERATION}}           e.g. Iteration 1 — Foundation
  {{FEATURE_BRANCH}}      e.g. phase-1/iteration-1
  {{IMPLEMENTER}}         Claude | ChatGPT | Copilot  (who built it)
  {{REVIEWER}}            Claude | ChatGPT | Copilot  (reviewer — must differ)
  {{TEST_COUNT_BEFORE}}   test count before this task
  {{TEST_COUNT_AFTER}}    expected test count after this task
-->

---

## Reviewer Role & Mandate
<!-- [BOILERPLATE] — do not change this section -->

You are an **independent code reviewer** for the cashflow-tracker project.

Your role is to evaluate a completed task implementation with the same rigour as a senior engineer reviewing a PR for a financial system. You did not write this code. You have no bias toward approving it. Your job is to protect the data integrity and audit trail.

**Your mandate:**

- Verify the implementation satisfies every acceptance criterion — not approximately, exactly.
- Identify violations of the architecture constraints — even minor ones.
- Flag silent failures, free-text categories, stored derived values, hard deletes, and scope creep.
- Report problems precisely: file path, line number, exact issue, why it matters.
- Be specific. "Looks fine" is not acceptable. "Line 47: `logged_by = request.form['username']` stores a name string instead of `users.id` FK, violating identity rule 6" is acceptable.

**What you must NOT do:**

- Do not fix the code. Report problems. Fixing is the implementer's job.
- Do not approve based on tests passing alone — tests can be incomplete.
- Do not overlook an issue because it seems minor. Log it with `severity: minor`.
- Do not invent problems. Every finding must be backed by evidence (file path + line number).

**Your verdict has three options:**

| Verdict | Meaning |
|---------|---------|
| `PASS` | All acceptance criteria met, no architecture violations, tests adequate. Ready to merge. |
| `CHANGES REQUIRED` | One or more problems found. List every fix needed before re-review. |
| `BLOCKED` | A fundamental design decision is wrong and the approach must be reconsidered. |

---

## Project Context
<!-- [BOILERPLATE] — do not change this section -->

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business. It records gross income and expense transactions with full Polish VAT tracking and a soft-delete audit trail. Input is via FastAPI web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 · Vanilla JS · bcrypt · pytest · ruff

**Architecture principles (violations of any of these = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT is extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no SQL DELETE on transactions; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — no free-text category names accepted or stored anywhere |
| 5 | **No silent failures** — no `except: pass`; every validation error raises explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived values never stored** — `vat_amount`, `net_amount`, `vat_reclaimable`, `effective_cost` computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point; never in route handlers or templates |

---

## Task Under Review
<!-- [FILL IN] -->

| Field | Value |
|-------|-------|
| Task ID | {{TASK_ID}} |
| Title | {{TASK_TITLE}} |
| Phase | {{PHASE}} |
| Iteration | {{ITERATION}} |
| Implemented by | {{IMPLEMENTER}} |
| Reviewed by | {{REVIEWER}} |
| Feature branch | `{{FEATURE_BRANCH}}` |
| Expected test count | {{TEST_COUNT_BEFORE}} before → {{TEST_COUNT_AFTER}} after |

---

## What This Task Was Supposed to Build
<!-- [FILL IN] Copy the "What to Build" section from the task prompt verbatim.
Do not summarise — the reviewer needs the exact spec to check against. -->

### New files

```
{{NEW_FILE_1}}     ← purpose
{{NEW_FILE_2}}     ← purpose
```

### Modified files

```
{{MODIFIED_FILE_1}}  ← what changes and why
```

### Public API (required signatures)

```python
{{PASTE_PUBLIC_API_FROM_TASK_PROMPT}}
```

### Behaviour rules the implementation must enforce

- **Rule 1:** {{e.g. income_type=internal forces vat_rate=0 — enforced in API handler, not just UI}}
- **Rule 2:** {{e.g. Expense row without vat_deductible_pct rejected with 400}}
- **Rule 3:** {{e.g. logged_by always set from session, never from request body}}
- **Rule 4:** {{e.g. Seed is idempotent — INSERT OR IGNORE used throughout}}

---

## Allowed Files
<!-- [FILL IN] Copy from task prompt. Only these files may have been created or modified. -->

```
{{FILE_PATH_1}}     ← new | modify: {{why}}
{{FILE_PATH_2}}     ← new | modify: {{why}}
```

**Files that must NOT have been touched:**

```
{{ADJACENT_FILE_1}}    ← reason
{{ADJACENT_FILE_2}}    ← reason
```

---

## Acceptance Criteria to Verify
<!-- [FILL IN] Copy from task prompt exactly. You will mark each PASS or FAIL. -->

- [ ] {{Criterion 1}}
- [ ] {{Criterion 2}}
- [ ] All {{TEST_COUNT_BEFORE}}+ prior tests still pass (`pytest` exit code 0)
- [ ] New tests for this task all pass
- [ ] Ruff clean (`ruff check .` exit code 0)
- [ ] Only allowed files were modified

---

## Tests Required (from task prompt)
<!-- [FILL IN] Copy the test table from the task prompt.
The reviewer will check that each test exists AND that the assertion is strong enough. -->

| Test function | What it verifies |
|---------------|-----------------|
| `test_{{subject}}_{{condition}}` | {{expected behaviour}} |
| `test_{{subject}}_{{condition}}` | {{expected behaviour}} |

---

## Edge Cases to Check
<!-- [FILL IN] Copy from task prompt. Reviewer verifies each is handled AND tested. -->

| Edge case | Required behaviour |
|-----------|-------------------|
| `income_type = internal` with `vat_rate ≠ 0` | Rejected with 400 |
| Expense with `vat_deductible_pct = NULL` | Rejected with 400, never saved |
| `other_expense` with empty description | Rejected with 400 |
| Void without `void_reason` | Rejected with 400, row not deactivated |
| {{Edge case specific to this task}} | {{expected}} |

---

## Review Execution Steps
<!-- [BOILERPLATE] — do not change this section -->

Run these commands in order. Report the output for each.

### Step 1 — Checkout and baseline

```bash
git fetch origin
git checkout {{FEATURE_BRANCH}}
git pull origin {{FEATURE_BRANCH}}
```

### Step 2 — Run tests and lint

```bash
pytest --tb=short -q
# Expected: {{TEST_COUNT_AFTER}} passing, 0 failures

ruff check .
# Expected: no issues
```

Report the exact output. If either fails, the verdict is `CHANGES REQUIRED` immediately.

### Step 3 — Verify scope

```bash
git diff --name-only main
```

Every file listed must appear in the "Allowed Files" section above.
Any unexpected file = scope violation = `CHANGES REQUIRED`.

### Step 4 — Read the implementation

Read every file in "Allowed Files" in full. Then:

- Compare each public API signature against the spec in "What to Build".
- Check each behaviour rule is implemented as specified.
- Check each edge case is handled.
- Check for architecture principle violations (see Project Context).

### Step 5 — Audit the tests

For each test in "Tests Required":

1. Confirm the test function exists by name.
2. Read the test body — does the assertion actually verify what the test claims?
3. Flag any test where passing could mask a real bug (e.g. only checks status code, not DB state).

### Step 6 — Check for hard deletes

```bash
grep -rn "\.delete\|DELETE FROM" app/
# Expected: no matches on transactions (soft-delete only)
```

### Step 7 — Check for stored derived values

```bash
grep -rn "vat_amount\|net_amount\|vat_reclaimable\|effective_cost" db/schema.sql
# Expected: no matches — these are never stored
```

### Step 8 — Check for free-text categories

```bash
grep -rn "category[^_]" app/routes/ app/services/
# Expected: no string-typed category values — only category_id integers
```

### Step 9 — Check for silent failures

```bash
grep -rn "except.*pass\|except:$" app/
# Expected: no matches
```

### Step 10 — Check logged_by source

```bash
grep -rn "logged_by" app/routes/
# Expected: all assignments use session['user_id'] or equivalent — never form input
```

---

## Required Output Format
<!-- [BOILERPLATE] — do not change this section -->

Your review must be structured exactly as follows. Do not add extra sections.
Do not omit a section even if it has no findings.

---

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

---

### 2. What's Correct

List everything implemented correctly and matching the spec. Be specific — reference file paths and line numbers. This section must not be empty on a PASS verdict.

---

### 3. Problems Found

For each problem, use this format:

```
- severity: critical | major | minor
  file: app/path/to/file.py:LINE
  exact problem: one or two sentences describing what is wrong
  why it matters: one sentence explaining the consequence
```

Severity guide:
- `critical` — data integrity issue, audit trail broken, or security issue. Blocks merge.
- `major` — violates an architecture constraint or acceptance criterion. Blocks merge.
- `minor` — code quality issue, weak test, or style deviation. Must be fixed but lower urgency.

If no problems found, write: `None.`

---

### 4. Missing or Weak Tests

For each test that is absent or has a weak assertion:

```
- test: test_function_name (missing | weak assertion)
  issue: what is missing or what the assertion fails to verify
  suggestion: what a correct assertion would look like
```

If all required tests are present and strong, write: `None.`

---

### 5. Scope Violations

List any files modified that are not in the "Allowed Files" list.

```
- file: path/to/unexpected_file.py
  change: what was changed
  verdict: revert | move to correct task
```

If no violations, write: `None.`

---

### 6. Acceptance Criteria Check

Copy the criteria list and mark each:

```
- [PASS | FAIL] {{Criterion 1}}
- [PASS | FAIL] {{Criterion 2}}
...
```

---

### 7. Exact Fixes Required

Numbered list. Each fix must be actionable — file path, line number, what to change.
If verdict is PASS, write: `None.`

```
1. app/routes/transactions.py:LINE — replace X with Y because Z
2. tests/test_transactions.py — add test_X to verify Y
3. ...
```

---

### 8. Final Recommendation

```
approve | request changes | block
```

One sentence explaining the recommendation.

---

<!--
CHECKLIST BEFORE SENDING
=========================
[ ] All {{PLACEHOLDER}} values replaced
[ ] "What to Build" populated from task prompt verbatim (not summarised)
[ ] Acceptance criteria copied exactly from task prompt
[ ] Test table populated from task prompt
[ ] Edge cases table populated from task prompt
[ ] Allowed files list complete
[ ] Files NOT to touch list complete
[ ] Reviewer AI is different from implementer AI
[ ] All [FILL IN] comments removed
[ ] All [BOILERPLATE] sections unchanged
[ ] Template instructions and this checklist removed before sending
-->

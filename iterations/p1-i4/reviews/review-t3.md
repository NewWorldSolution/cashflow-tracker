# Review — I4-T3: Void/Correct Templates
**Reviewer:** Codex
**Implemented by:** Claude Code
**Branch:** `feature/p1-i4/t3-templates`
**PR target:** `feature/phase-1/iteration-4`

---

## Reviewer Role

Review only the changes in this task branch. Report problems precisely; do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- New templates:
  - `app/templates/transactions/detail.html`
  - `app/templates/transactions/void.html`
- One-line updates:
  - `app/templates/transactions/create.html`
  - `app/templates/transactions/list.html`

---

## Review steps

1. Confirm scope is limited to the four template files.
2. Verify `detail.html` shows the expected fields and active/voided conditional sections.
3. Verify `void.html` shows summary, inline errors, input, submit, cancel.
4. Verify `create.html` uses `form_action | default('/transactions/new')`.
5. Verify `list.html` links the date cell to `/transactions/{{ t.id }}`.
6. Run:

```bash
python -c "from fastapi.templating import Jinja2Templates; Jinja2Templates(directory='app/templates'); print('templates loadable ok')"
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside the four allowed template files.

### 5. Acceptance Criteria Check

- [PASS|FAIL] scope limited to detail.html, void.html, create.html, list.html
- [PASS|FAIL] detail.html shows required fields and links
- [PASS|FAIL] void.html shows summary, errors, void_reason input, and cancel link
- [PASS|FAIL] create.html form action is configurable via form_action
- [PASS|FAIL] list.html date links to transaction detail
- [PASS|FAIL] templates load without Jinja2 errors

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# Review — I6-T2: Template String Extraction
**Branch:** `feature/p1-i6/t2-template-extraction`
**PR target:** `feature/phase-1/iteration-6`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- Modified: all 8 templates — replace hardcoded English strings with `{{ t('key') }}` calls
- Optionally extended: `app/i18n/en.py` — add any new keys discovered during extraction

---

## Review steps

1. Confirm diff scope is only template files and optionally `app/i18n/en.py`. No routes, services, JS, CSS, or tests modified.
2. Verify `base.html`: SANDBOX banner, nav links, sign out button all use `{{ t('key') }}`.
3. Verify `dashboard.html`: title, all card labels, "active"/"voided", "as of", buttons, heading, empty state use `{{ t('key') }}`.
4. Verify `transactions/create.html`: title, all form labels, helper text, placeholders, required indicator, card reminder, error heading, buttons use `{{ t('key') }}`.
5. Verify `transactions/list.html`: title, column headers, badges, toggle text, empty state, buttons, split view labels use `{{ t('key') }}`.
6. Verify `transactions/detail.html`: title, back link, all field labels, badges, void details labels, correction callout, buttons use `{{ t('key') }}`.
7. Verify `transactions/void.html`: title, warning, label, placeholder, buttons use `{{ t('key') }}`.
8. Verify `auth/login.html`: title, labels, button use `{{ t('key') }}`.
9. Verify `settings/opening_balance.html`: title, description, labels, button use `{{ t('key') }}`.
10. Verify free-text content is NOT wrapped: `{{ t.description }}`, `{{ t.void_reason }}`, usernames, category labels, amounts, dates.
11. Verify inline JS strings in `list.html` use template-rendered variables (e.g., `STRINGS` object).
12. Verify all HTML structure, CSS classes, and Jinja2 logic blocks remain intact.
13. Verify any new keys added to `en.py` are properly formatted.
14. Verify app still renders English output (no visible change to user).
15. Run:

```bash
pytest -v   # all existing tests must pass (98 before T5 merges, 101 after)
ruff check .
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

Files modified outside templates and `app/i18n/en.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] base.html: all hardcoded strings replaced
- [PASS|FAIL] dashboard.html: all hardcoded strings replaced
- [PASS|FAIL] create.html: all hardcoded strings replaced
- [PASS|FAIL] list.html: all hardcoded strings replaced
- [PASS|FAIL] detail.html: all hardcoded strings replaced
- [PASS|FAIL] void.html: all hardcoded strings replaced
- [PASS|FAIL] login.html: all hardcoded strings replaced
- [PASS|FAIL] opening_balance.html: all hardcoded strings replaced
- [PASS|FAIL] free-text/dynamic values NOT wrapped in t()
- [PASS|FAIL] inline JS strings use template-rendered variables
- [PASS|FAIL] HTML structure and CSS classes unchanged
- [PASS|FAIL] Jinja2 logic blocks intact
- [PASS|FAIL] app renders identically (English output unchanged)
- [PASS|FAIL] all existing tests pass (98 before T5 merges, 101 after)
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

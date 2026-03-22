# Review — I6-T3: Polish Translation + Language Switcher
**Branch:** `feature/p1-i6/t3-polish-translation`
**PR target:** `feature/phase-1/iteration-6`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- New file: `app/i18n/pl.py` — complete Polish `MESSAGES` and `VALIDATION_ERRORS` dicts
- Modified: `app/i18n/__init__.py` — register `pl` module in `_LOCALE_MAP`
- Modified: `app/templates/base.html` — language switcher (PL | EN)
- Modified: `app/routes/transactions.py` — translate validation errors at route layer
- Modified: `app/routes/auth.py` — translate errors if any
- Modified: `app/routes/settings.py` — translate errors if any
- Modified: `app/main.py` — `/lang/{locale}` route, EXEMPT_PATHS update
- Extended: `static/style.css` — `.lang-switch` styling

---

## Review steps

1. Confirm diff scope matches allowed files only. No changes to `validation.py`, `calculations.py`, `form.js`, or tests.
2. Verify `app/i18n/pl.py` has a `MESSAGES` dict with a Polish translation for EVERY key in `en.py`.
3. Cross-check: count keys in `en.MESSAGES` vs `pl.MESSAGES` — must be identical.
4. Verify `app/i18n/pl.py` has a `VALIDATION_ERRORS` dict with Polish translation for every key in `en.VALIDATION_ERRORS`.
5. Verify translations are professional Polish (business context, not informal).
6. Verify `_LOCALE_MAP` in `__init__.py` now includes `"pl": pl`.
7. Verify validation errors are translated at the route layer in `transactions.py` using `translate_error()`.
8. Verify `auth.py` and `settings.py` translate errors if they pass error strings to templates.
9. Verify flash messages are translated at render time (in `base.html` or middleware).
10. Verify language switcher in `base.html`: shows PL | EN, highlights current language.
11. Verify `/lang/{locale}` route exists, sets session locale, redirects to referer.
12. Verify `/lang/en` and `/lang/pl` are in `EXEMPT_PATHS`.
13. Verify `.lang-switch` CSS styling.
14. Verify app defaults to Polish (since `DEFAULT_LOCALE = "pl"`).
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

Files modified outside allowed list.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `pl.py` exists with complete `MESSAGES` dict
- [PASS|FAIL] `pl.py` exists with complete `VALIDATION_ERRORS` dict
- [PASS|FAIL] every `en.py` key has a Polish translation (no missing keys)
- [PASS|FAIL] translations are professional Polish
- [PASS|FAIL] `_LOCALE_MAP` includes `"pl"`
- [PASS|FAIL] validation errors translated at route layer
- [PASS|FAIL] flash messages translated at render time
- [PASS|FAIL] language switcher visible in nav (PL | EN)
- [PASS|FAIL] `/lang/{locale}` route works and sets session
- [PASS|FAIL] `/lang/en` and `/lang/pl` in EXEMPT_PATHS
- [PASS|FAIL] app defaults to Polish
- [PASS|FAIL] switching language changes all UI text
- [PASS|FAIL] all existing tests pass — 98 before T5 merges, 101 after (validation assertions remain English internally)
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

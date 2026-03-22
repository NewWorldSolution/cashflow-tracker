# Review — I6-T1: i18n Foundation + English Dictionary
**Branch:** `feature/p1-i6/t1-i18n-foundation`
**PR target:** `feature/phase-1/iteration-6`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- New file: `app/i18n/__init__.py` — `translate()`, `translate_error()`, `get_messages()` functions
- New file: `app/i18n/en.py` — `MESSAGES` and `VALIDATION_ERRORS` dicts
- Modified: `app/main.py` — `LocaleMiddleware`, `t()` Jinja2 global

---

## Review steps

1. Confirm diff scope is only `app/i18n/__init__.py`, `app/i18n/en.py`, and `app/main.py`.
2. Verify `app/i18n/__init__.py` has `translate()`, `translate_error()`, and `get_messages()` functions.
3. Verify `DEFAULT_LOCALE` is `"pl"`.
4. Verify `_LOCALE_MAP` contains only `"en"` — no placeholder import for `pl`.
5. Verify `translate()` falls back to English, then to the key itself.
6. Verify `translate_error()` falls back to the original English error string.
7. Verify `app/i18n/en.py` has a `MESSAGES` dict covering all sections: nav, dashboard, form, list, badges, detail, void details, void page, auth, settings, flash messages, language.
8. Verify `app/i18n/en.py` has a `VALIDATION_ERRORS` dict that is an identity mapping (key = value).
9. Cross-check `VALIDATION_ERRORS` keys against ALL error strings in `app/services/validation.py` — every string must be present.
10. Verify `LocaleMiddleware` reads from `request.session.get("locale", "pl")` and sets `request.state.locale`.
11. Verify `t()` is registered as a Jinja2 global and uses `request.state.locale`.
12. Verify no template files were modified (that's T2).
13. Run:

```bash
pytest -v   # all 98 tests must pass
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

Files modified outside `app/i18n/__init__.py`, `app/i18n/en.py`, and `app/main.py`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] `translate()` function with English + key fallback
- [PASS|FAIL] `translate_error()` function with original string fallback
- [PASS|FAIL] `get_messages()` function returns locale-specific MESSAGES
- [PASS|FAIL] `DEFAULT_LOCALE` is `"pl"`
- [PASS|FAIL] `_LOCALE_MAP` contains only `"en"` (no `pl` placeholder)
- [PASS|FAIL] `MESSAGES` dict covers all UI sections
- [PASS|FAIL] `VALIDATION_ERRORS` is identity mapping of all validation.py strings
- [PASS|FAIL] Every validation.py error string has a corresponding key
- [PASS|FAIL] `LocaleMiddleware` sets `request.state.locale` (default `"pl"`)
- [PASS|FAIL] `t()` Jinja2 global registered and working
- [PASS|FAIL] No template files modified
- [PASS|FAIL] all 98 tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

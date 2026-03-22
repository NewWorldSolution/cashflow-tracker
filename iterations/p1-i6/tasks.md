# P1-I6 — Multi-Language Foundation + Polish UI
## Task Board

**Status:** NOT STARTED
**Last updated:** 2026-03-23
**Iteration branch:** `feature/phase-1/iteration-6` ← all task PRs target this branch
**Final PR:** `feature/phase-1/iteration-6` → `main` ← QA agent approves before merge

---

## Dependency Map

```
I6-T1 (i18n foundation + English dict)
  └── I6-T2 (template string extraction)
        └── I6-T3 (Polish translation + language switcher)
              └── I6-T4 (locale-aware formatting)
I6-T5 (voided_at timestamp) — independent, can run in parallel with any task
```

T1 creates the infrastructure. T2 extracts all strings. T3 adds Polish and the switcher. T4 adds date/number formatting. T5 is a standalone schema + service change that can run at any time.

---

## Tasks

| ID    | Title                              | Owner | Status     | Depends on | Branch                                    |
|-------|------------------------------------|-------|------------|------------|-------------------------------------------|
| I6-T1 | i18n foundation + English dict     | —     | ⏳ WAITING | —          | `feature/p1-i6/t1-i18n-foundation`       |
| I6-T2 | Template string extraction         | —     | ⏳ WAITING | I6-T1      | `feature/p1-i6/t2-template-extraction`   |
| I6-T3 | Polish translation + switcher      | —     | ⏳ WAITING | I6-T2      | `feature/p1-i6/t3-polish-translation`    |
| I6-T4 | Locale-aware formatting            | —     | ⏳ WAITING | I6-T3      | `feature/p1-i6/t4-locale-formatting`     |
| I6-T5 | voided_at timestamp                | —     | ⏳ WAITING | —          | `feature/p1-i6/t5-voided-at`            |

---

## Prompts & Reviews

| Task  | Implementation prompt                           | Review prompt                             | Reviewer |
|-------|-------------------------------------------------|-------------------------------------------|----------|
| I6-T1 | `iterations/p1-i6/prompts/t1-i18n-foundation.md` | `iterations/p1-i6/reviews/review-t1.md` | —        |
| I6-T2 | `iterations/p1-i6/prompts/t2-template-extraction.md` | `iterations/p1-i6/reviews/review-t2.md` | —        |
| I6-T3 | `iterations/p1-i6/prompts/t3-polish-translation.md` | `iterations/p1-i6/reviews/review-t3.md` | —        |
| I6-T4 | `iterations/p1-i6/prompts/t4-locale-formatting.md` | `iterations/p1-i6/reviews/review-t4.md` | —        |
| I6-T5 | `iterations/p1-i6/prompts/t5-voided-at.md`     | `iterations/p1-i6/reviews/review-t5.md`  | —        |
| —     | —                                               | `iterations/p1-i6/reviews/review-iteration.md` | — (QA) |

---

## Task Details

### I6-T1 — i18n foundation + English dictionary

**Goal:** Create the translation infrastructure so templates can call `{{ t('key') }}` and get localized text.

**Allowed files:**
```
app/i18n/__init__.py     ← create new
app/i18n/en.py           ← create new
app/main.py              ← modify (locale middleware, Jinja2 global)
```

**Deliverables:**
- `app/i18n/__init__.py` with `get_translations()`, `translate()`, `translate_error()` functions
- `app/i18n/en.py` with `MESSAGES` dict (all UI strings) and `VALIDATION_ERRORS` dict (all validation.py error strings as identity mapping)
- `LocaleMiddleware` in `app/main.py` — reads locale from session, defaults to `pl`
- `t()` function registered as Jinja2 global — available in all templates

**Acceptance check:**
- `t('key')` works in templates (verified by loading any page)
- Default locale is `pl`
- Fallback to English works when Polish key is missing
- All 98 existing tests pass
- ruff clean

---

### I6-T2 — Template string extraction

**Goal:** Replace every hardcoded user-facing string in every template with `{{ t('key') }}`. After T2, the app still shows English (only en.py exists) but all text flows through the translation system.

**Depends on:** I6-T1 ✅ DONE

**Allowed files:**
```
app/templates/base.html                        ← modify
app/templates/dashboard.html                   ← modify
app/templates/transactions/create.html         ← modify
app/templates/transactions/list.html           ← modify
app/templates/transactions/detail.html         ← modify
app/templates/transactions/void.html           ← modify
app/templates/auth/login.html                  ← modify
app/templates/settings/opening_balance.html    ← modify
app/i18n/en.py                                 ← extend (add any missing keys)
```

**Rules:**
- Do NOT translate free-text content (descriptions, void reasons, usernames)
- Do NOT translate category labels (from database)
- Do NOT change HTML structure or CSS classes
- Keep all Jinja2 logic intact

**Acceptance check:**
- Every user-facing string in templates uses `{{ t('key') }}`
- App renders identically to before (English output unchanged)
- All 98 existing tests pass
- ruff clean

---

### I6-T3 — Polish translation + language switcher

**Goal:** Full Polish UI with the ability to switch to English.

**Depends on:** I6-T2 ✅ DONE

**Allowed files:**
```
app/i18n/pl.py                        ← create new
app/templates/base.html               ← modify (add language switcher)
app/routes/transactions.py            ← modify (translate validation errors)
app/routes/auth.py                    ← modify (translate errors if any)
app/routes/settings.py                ← modify (translate errors if any)
app/main.py                           ← modify (add language switch route)
static/style.css                      ← extend (switcher styling if needed)
```

**Deliverables:**
- `app/i18n/pl.py` — complete `MESSAGES` and `VALIDATION_ERRORS` dicts in Polish
- Language switcher in nav (PL | EN toggle)
- Language switch route — sets session locale and redirects back
- Validation errors translated at route layer before passing to template
- Flash messages translated at render time

**Acceptance check:**
- App defaults to Polish — all UI text in Polish
- Switching to English shows all text in English
- Language preference persists across page loads (session)
- Validation errors appear in the selected language
- All 98 existing tests pass (assertions remain English)
- ruff clean

---

### I6-T4 — Locale-aware formatting

**Goal:** Dates and amounts display according to the selected locale's conventions.

**Depends on:** I6-T3 ✅ DONE

**Allowed files:**
```
app/i18n/__init__.py                           ← extend (format functions)
app/main.py                                    ← modify (register Jinja2 filters)
app/templates/transactions/list.html           ← modify (use format filters)
app/templates/transactions/detail.html         ← modify (use format filters)
app/templates/dashboard.html                   ← modify (use format filters)
```

**Deliverables:**
- `format_date` Jinja2 filter — Polish: `23.03.2026`, English: `2026-03-23`
- `format_amount` Jinja2 filter — Polish: `1 234,56`, English: `1,234.56`
- All date and amount displays in list, detail, and dashboard use these filters
- Filters respect `request.state.locale`

**Acceptance check:**
- Polish locale shows dates as `dd.mm.yyyy` and amounts with space/comma
- English locale shows dates as `yyyy-mm-dd` and amounts with comma/period
- All 98 existing tests pass
- ruff clean

---

### I6-T5 — voided_at timestamp

**Goal:** Record and display when a transaction was voided. Deferred from I5 (required schema change).

**Depends on:** none (can run in parallel with T1–T4)

**Allowed files:**
```
db/schema.sql                                  ← modify (add column)
db/init_db.py                                  ← modify (migration for existing DBs)
app/services/transaction_service.py            ← modify (set voided_at)
app/routes/transactions.py                     ← modify (set voided_at in correct flow)
app/templates/transactions/detail.html         ← modify (display voided_at)
tests/test_transactions.py                     ← extend (3 new tests)
```

**Deliverables:**
- `voided_at TIMESTAMP` column added to transactions table
- `void_transaction()` sets `voided_at = CURRENT_TIMESTAMP`
- Correct flow sets `voided_at` on the original transaction
- Detail page shows voided_at in void details section
- Migration handles existing databases (ALTER TABLE with try/except)
- 3 new tests: voided_at set on void, set on correct, null on active

**Acceptance check:**
- `voided_at` column exists in schema
- `voided_at` populated after void and correct operations
- `voided_at` displayed in detail page
- `voided_at` is NULL for active transactions
- All 98 existing + 3 new tests pass
- ruff clean

---

## Agent Rules

1. **Read this file first.** Find your task. Confirm status is WAITING before starting.
2. **Update status to IN PROGRESS** before writing a line of code.
3. **Check dependencies.** Never start if any dep is not ✅ DONE.
4. **Branch:** check out `feature/phase-1/iteration-6` first, then create your task branch from it.
5. **PR targets the iteration branch**, not `main`. One task per PR.
6. **After completing:** set status to ✅ DONE. Add one-line note: what you produced.
7. **Never touch another agent's task.** Add notes under your own task only.
8. **If blocked:** set status to 🚫 BLOCKED with reason. Stop and wait.
9. **No validation.py changes.** No calculations.py changes. No form.js changes.
10. **Validation errors are translated at the route layer**, not in the validation service.
11. **Default locale is `pl`** — Polish is the primary business language.
12. **Read your task prompt file:** `iterations/p1-i6/prompts/t[N]-[name].md`

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ⏳ WAITING | Not started — waiting for dependency |
| 🔄 IN PROGRESS | Agent actively working |
| ✅ DONE | Branch merged into `feature/phase-1/iteration-6` |
| 🚫 BLOCKED | Stopped — see note below task |
| ✔ COMPLETE | All tasks DONE, iteration merged to `main` |

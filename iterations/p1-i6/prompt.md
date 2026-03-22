# cashflow-tracker Task Prompt — P1-I6: Multi-Language Foundation + Polish UI

---

## Project Context

**cashflow-tracker** is a private cash flow notebook for a 3-person Polish service business (owner, assistant, wife). It records gross income and expense transactions with full Polish VAT tracking, card payment reconciliation, and a soft-delete audit trail. Input is via web form (Phase 1–4), Telegram group bot (Phase 5), and LLM-assisted entry (Phase 6).

**Stack:** Python · FastAPI · SQLite (sandbox) → PostgreSQL (production) · Jinja2 (server-side only) · Vanilla JS (form behaviour only) · bcrypt · pytest · ruff

**Core data flow:**
```
User (web form) → FastAPI route → services/ → SQLite → Jinja2 template
```

**Architecture principles (violations = CHANGES REQUIRED minimum):**

| # | Principle |
|---|-----------|
| 1 | **Gross amounts always** — `amount` stores actual gross cash; VAT extracted at query time, never stored |
| 2 | **Deterministic logic** — no LLM in validation, calculation, or reporting |
| 3 | **Soft-delete only** — no hard deletes ever; deactivation requires `is_active = FALSE` + `void_reason` + `voided_by` |
| 4 | **category_id is always FK** — never accept or store free-text category names |
| 5 | **No silent failures** — every validation error surfaces explicitly |
| 6 | **Identity via users.id** — `logged_by` and `voided_by` are always integer FKs; never name strings |
| 7 | **Derived calculations never stored** — computed at query time only |
| 8 | **Validation in service layer** — `services/validation.py` is the single enforcement point for transaction field rules |

---

## Repository State

- **Iteration branch:** `feature/phase-1/iteration-6`
- **Base branch:** `main` (P1-I5 merged — UI/UX polish complete)
- **Tests passing:** 98
- **Ruff:** clean
- **Last completed iteration:** P1-I5 — UI/UX Polish (CSS system, dashboard, form UX, list/detail/void styling, flash messages, UX improvements)
- **Python:** 3.11+
- **Package install:** `pip install -r requirements.txt`

---

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | P1-I6 |
| Title | Multi-Language Foundation + Polish UI |
| Phase | Phase 1 — Web Form & Transaction Capture |
| Iteration | Iteration 6 (final Phase 1 iteration) |
| Feature branch | `feature/phase-1/iteration-6` |
| Depends on | P1-I5 (UI/UX polish — all merged to main) |
| Blocks | Phase 2 (reporting) |
| PR scope | Task branches PR into `feature/phase-1/iteration-6`. The iteration branch PRs into `main` after QA. |

---

## Task Goal

Make the app speak Polish for the assistant and wife users, while keeping English available for the owner. After I6, all UI text comes from translation dictionaries, Polish is the default language, and the architecture supports adding Turkish later without rewriting templates.

Additionally, add the `voided_at` timestamp that was deferred from I5 (required a schema change which I5 did not allow).

**Execution model:** 5 task branches, each with its own prompt file in `iterations/p1-i6/prompts/`. This file is the full reference; task prompt files are the execution guides.

---

## Files to Read Before Starting

### Mandatory — all tasks, in this order

```
CLAUDE.md
project.md
docs/concept.md
docs/architecture.md
iterations/phase-1-plan.md          (I6 section)
```

### Task-specific

| Task | Also read |
|------|-----------|
| I6-T1 | `app/main.py`, `app/templates/base.html` |
| I6-T2 | All `app/templates/**/*.html`, `app/routes/*.py` |
| I6-T3 | `app/i18n/en.py` (created in T1), `app/routes/transactions.py` (validation error translation) |
| I6-T4 | `app/templates/transactions/list.html`, `app/templates/transactions/detail.html`, `app/templates/dashboard.html` |
| I6-T5 | `db/schema.sql`, `app/services/transaction_service.py`, `app/routes/transactions.py`, `app/templates/transactions/detail.html` |

---

## Translation Strategy

### Key design decisions

1. **Simple Python dicts** — one `.py` file per language (`en.py`, `pl.py`). No heavy i18n framework.
2. **English as canonical keys** — validation.py continues to return English error strings. Translation happens at the route/template layer.
3. **Template helper function** — a `t()` function available in all Jinja2 templates that looks up the translation key and returns the localized string.
4. **Session-based language** — language preference stored in session. Switchable via nav toggle.
5. **Fallback to English** — if a Polish key is missing, fall back to English string.

### What gets translated

- Navigation labels
- Page headings
- Form labels, helper text, placeholders
- Button text
- Empty state messages
- Flash messages (stored in English in session, translated at render time)
- Audit labels (Created by, Voided by, etc.)
- Status labels (Active, Voided, Corrected)
- Error summary heading ("Please fix the following errors:")

### What does NOT get translated

- Validation error strings from `validation.py` — these stay English internally. They are translated via a lookup dict at the route/template layer before rendering.
- Free-text content (descriptions, void reasons) — user-entered, shown as-is
- Category labels — these stay as-is for now (already meaningful in English: "Food", "Petrol", etc.)
- Log/debug output

### Validation error translation approach

`validation.py` returns a flat list of English error strings. These are canonical keys. The translation layer maps each English string to its Polish equivalent. If no match, the English string is shown as fallback.

```python
# In i18n/en.py — validation error translations (identity mapping)
VALIDATION_ERRORS = {
    "Date is required.": "Date is required.",
    "Amount must be a positive number.": "Amount must be a positive number.",
    ...
}

# In i18n/pl.py — Polish validation error translations
VALIDATION_ERRORS = {
    "Date is required.": "Data jest wymagana.",
    "Amount must be a positive number.": "Kwota musi być liczbą dodatnią.",
    ...
}
```

The route layer translates errors before passing to the template:
```python
errors = validate_transaction(data, db)
errors = [translate_error(e, locale) for e in errors]
```

---

## Allowed Files

```
app/i18n/__init__.py                     ← create new (T1)
app/i18n/en.py                           ← create new (T1)
app/i18n/pl.py                           ← create new (T3)
app/main.py                              ← modify: language middleware (T1)
app/templates/base.html                  ← modify: language switcher, use translation keys (T1, T2, T3)
app/templates/dashboard.html             ← modify: use translation keys (T2)
app/templates/transactions/create.html   ← modify: use translation keys (T2)
app/templates/transactions/list.html     ← modify: use translation keys, locale formatting (T2, T4)
app/templates/transactions/detail.html   ← modify: use translation keys, locale formatting, voided_at (T2, T4, T5)
app/templates/transactions/void.html     ← modify: use translation keys (T2)
app/templates/auth/login.html            ← modify: use translation keys (T2)
app/templates/settings/opening_balance.html ← modify: use translation keys (T2)
app/routes/transactions.py              ← modify: translate validation errors before render (T3)
app/routes/dashboard.py                 ← modify: pass locale context if needed (T2)
app/routes/auth.py                      ← modify: translate validation errors if any (T3)
app/routes/settings.py                  ← modify: translate validation errors if any (T3)
db/schema.sql                           ← modify: add voided_at column (T5)
db/init_db.py                           ← modify: if migration logic needed (T5)
app/services/transaction_service.py     ← modify: set voided_at on void/correct (T5)
app/routes/transactions.py              ← modify: pass voided_at to template (T5)
tests/test_transactions.py              ← extend: voided_at tests (T5)
static/style.css                        ← extend: language switcher styling if needed (T3)
iterations/p1-i6/tasks.md               ← status updates only
```

Do NOT modify:
- `app/services/validation.py` — frozen (returns English strings; translation at route layer)
- `app/services/calculations.py` — frozen
- `static/form.js` — no changes needed for i18n

---

## Deliverables by Task

### T1 — i18n Foundation (module, middleware, English dictionary)

**Goal:** Create the translation infrastructure. After T1, the system has a working `t()` helper, language middleware, and an English dictionary — but templates still use hardcoded strings.

Create `app/i18n/__init__.py`:
- `get_translations(locale: str) -> dict` — returns the message dict for the given locale
- `translate(key: str, locale: str) -> str` — look up a single key; fallback to English if missing
- `translate_error(error: str, locale: str) -> str` — look up a validation error string
- Supported locales: `en`, `pl`
- Default locale: `pl` (Polish is the primary business language)

Create `app/i18n/en.py`:
- `MESSAGES` dict with ALL UI strings as keys and English values
- `VALIDATION_ERRORS` dict mapping validation.py error strings to English (identity mapping)
- Organize by page/section for maintainability

Update `app/main.py`:
- Add `LocaleMiddleware` that reads `request.session.get("locale", "pl")` and sets `request.state.locale`
- Make `t()` function available as a Jinja2 global so templates can call `{{ t('key') }}`

### T2 — Template String Extraction (all templates use translation keys)

**Goal:** Replace every hardcoded user-facing string in every template with a `{{ t('key') }}` call. After T2, the app still shows English (because only en.py exists), but all text flows through the translation system.

Templates to update:
- `base.html` — nav labels, SANDBOX banner text, flash message wrapper
- `dashboard.html` — headings, card labels, empty state, button text
- `transactions/create.html` — form labels, helpers, placeholders, buttons, error heading
- `transactions/list.html` — headings, column headers, badges, empty state, buttons
- `transactions/detail.html` — headings, field labels, audit labels, badges, buttons
- `transactions/void.html` — headings, warning text, labels, buttons
- `auth/login.html` — heading, labels, button, error text
- `settings/opening_balance.html` — heading, labels, button, helper text

**Rules:**
- Do NOT translate free-text content (descriptions, void reasons, usernames)
- Do NOT translate category labels (they come from the database)
- Do NOT change any HTML structure or CSS classes — only replace text content
- Keep all existing Jinja2 logic (`{% if %}`, `{% for %}`, etc.) intact

### T3 — Polish Translation + Language Switcher

**Goal:** Full Polish UI. After T3, the app defaults to Polish and users can switch to English.

Create `app/i18n/pl.py`:
- `MESSAGES` dict — complete Polish translation of all keys from `en.py`
- `VALIDATION_ERRORS` dict — Polish translations of all validation.py error strings

Update routes to translate validation errors:
- `app/routes/transactions.py` — wrap errors list through `translate_error()` before passing to template
- `app/routes/auth.py` — same if login errors exist
- `app/routes/settings.py` — same if validation errors exist

Add language switcher to `base.html`:
- Simple toggle in nav: "PL | EN"
- Links to a language switch endpoint that sets `request.session["locale"]` and redirects back
- Add the switch route to `app/main.py` or a dedicated route

Add to `static/style.css` if needed:
- Minimal styling for the language switcher

### T4 — Locale-Aware Formatting (dates, numbers)

**Goal:** Dates and amounts display in Polish convention when locale is `pl`.

Date formatting:
- Polish: `23.03.2026` or `23 marca 2026` (day.month.year)
- English: `2026-03-23` (ISO, current format)
- Implement as a Jinja2 filter: `{{ t.date | format_date }}`

Number/amount formatting:
- Polish: `1 234,56` (space as thousands separator, comma as decimal)
- English: `1,234.56` (current format)
- Implement as a Jinja2 filter: `{{ t.amount | format_amount }}`

Pages to update:
- `list.html` — date column, amount column
- `detail.html` — date field, amount field, created_at
- `dashboard.html` — amounts in summary cards, dates in recent transactions

### T5 — voided_at Timestamp (schema + service + template + tests)

**Goal:** Show when a transaction was voided. Deferred from I5 because it requires a schema change.

Schema change (`db/schema.sql`):
- Add `voided_at TIMESTAMP` column to `transactions` table (nullable, no default)

Migration (`db/init_db.py`):
- Handle existing databases: `ALTER TABLE transactions ADD COLUMN voided_at TIMESTAMP` wrapped in try/except (column may already exist on re-run)

Service change (`app/services/transaction_service.py`):
- In `void_transaction()`: set `voided_at = CURRENT_TIMESTAMP` alongside `is_active = 0`

Route change (`app/routes/transactions.py`):
- In `post_correct_transaction()`: set `voided_at` when voiding the original
- The `voided_at` value is already in the query result (via `t.*`) — no extra query needed

Template change (`app/templates/transactions/detail.html`):
- In the "Void Details" section, add `voided_at` display:
```html
<dt>{{ t('voided_at') }}</dt><dd>{{ t.voided_at | format_date }}</dd>
```

New tests (`tests/test_transactions.py`):
- `test_voided_at_set_on_void` — void a transaction, verify `voided_at` is not NULL
- `test_voided_at_set_on_correct` — correct a transaction, verify original's `voided_at` is not NULL
- `test_voided_at_null_on_active` — create a transaction, verify `voided_at` is NULL

---

## What Must NOT Change

- `validate_transaction` logic — no modifications (returns English strings)
- Calculation formulas — no modifications
- Form submission behavior — same fields, same values, same redirects
- `form.js` business logic — no changes needed for i18n
- Route paths — no changes
- All 98 existing tests must pass (validation assertions remain English)

---

## Acceptance Checklist

```bash
pytest -v
# Expected: 101+ passed (98 existing + 3 new voided_at tests), 0 failed
ruff check .
# Expected: clean
```

- [ ] `app/i18n/` module exists with `en.py` and `pl.py`
- [ ] All templates use `{{ t('key') }}` for user-facing text
- [ ] App defaults to Polish — all labels, buttons, headings in Polish
- [ ] Language switcher in nav toggles between PL and EN
- [ ] Switching language preserves session and data
- [ ] Validation errors display in the selected language
- [ ] Dates display in Polish format when locale is `pl`
- [ ] Amounts display with Polish number formatting when locale is `pl`
- [ ] English fallback works — missing Polish key shows English
- [ ] `voided_at` column exists in schema
- [ ] `voided_at` populated on void and correct operations
- [ ] `voided_at` displayed in detail page void section
- [ ] All existing 98 tests still pass
- [ ] 3 new `voided_at` tests pass
- [ ] Architecture supports adding Turkish later (just add `tr.py`)
- [ ] Category labels remain untranslated (from database)
- [ ] Free-text content (descriptions, void reasons) shown as-is
- [ ] SANDBOX banner still visible on every page
- [ ] No business logic changes in validation.py or calculations.py

---

## Agent Rules

1. Read this file first.
2. Read your task prompt file: `iterations/p1-i6/prompts/t[N]-[name].md`
3. Update status to IN PROGRESS before writing any code.
4. Check dependencies — never start if dep is not DONE.
5. Verify acceptance checklist before requesting review.
6. After PR is merged: update `tasks.md` status → DONE with one-line note.
7. No validation.py changes. No calculations.py changes. No form.js changes.
8. Validation errors are translated at the route layer — not in the validation service.
9. Default locale is `pl` (Polish) — English is the fallback, not the default.
10. Test with both locales before marking done.

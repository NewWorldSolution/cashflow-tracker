# I6-T3 — Polish Translation + Language Switcher

**Branch:** `feature/p1-i6/t3-polish-translation` (from `feature/phase-1/iteration-6`)
**PR target:** `feature/phase-1/iteration-6`
**Depends on:** I6-T2 ✅ DONE

---

## Goal

Deliver a full Polish UI and a language switcher. After T3, the app defaults to Polish and users can toggle to English.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i6/prompt.md                    (translation strategy, validation error approach)
app/i18n/__init__.py                           (translation functions)
app/i18n/en.py                                 (all keys to translate)
app/routes/transactions.py                     (where validation errors are passed to templates)
app/routes/auth.py                             (login error handling)
app/routes/settings.py                         (settings error handling)
app/templates/base.html                        (where switcher goes)
```

---

## Allowed Files

```
app/i18n/__init__.py           ← modify (register pl module)
app/i18n/pl.py                 ← create new
app/templates/base.html        ← modify (add language switcher)
app/routes/transactions.py     ← modify (translate validation errors)
app/routes/auth.py             ← modify (translate login errors if any)
app/routes/settings.py         ← modify (translate settings errors if any)
app/main.py                    ← modify (add language switch route)
static/style.css               ← extend (switcher styling if needed)
```

Do NOT modify `app/services/validation.py`, `app/services/calculations.py`, `static/form.js`, or tests.

---

## What to Implement

### 1. Create `app/i18n/pl.py`

Complete Polish translation of ALL keys from `en.py`:

**`MESSAGES`** dict — every key from `en.py` with Polish values. Examples:

```python
MESSAGES = {
    # Navigation
    "nav_brand": "cashflow-tracker",
    "nav_transactions": "Transakcje",
    "nav_new": "+ Nowa",
    "nav_sign_out": "Wyloguj",
    "sandbox_banner": "SANDBOX — to jest środowisko testowe. Dane mogą zostać usunięte.",

    # Dashboard
    "dashboard_title": "Panel",
    "dashboard_opening_balance": "Saldo początkowe",
    "dashboard_as_of": "na dzień",
    "dashboard_not_set": "Nie ustawiono",
    "dashboard_total_income": "Łączny przychód",
    "dashboard_total_expenses": "Łączne wydatki",
    "dashboard_transactions": "Transakcje",
    "dashboard_active": "aktywne",
    "dashboard_voided": "anulowane",
    ...
}
```

Translate ALL keys. Do not skip any. Use professional Polish — this is a business tool for daily use. The owner's wife and assistant will read this.

**`VALIDATION_ERRORS`** dict — Polish translations of all validation.py error strings:

```python
VALIDATION_ERRORS = {
    "Date is required.": "Data jest wymagana.",
    "Date must be a valid YYYY-MM-DD value.": "Data musi być w formacie RRRR-MM-DD.",
    "Direction must be income or expense.": "Kierunek musi być przychód lub wydatek.",
    "Amount must be a positive number.": "Kwota musi być liczbą dodatnią.",
    "Amount must be greater than 0.": "Kwota musi być większa od 0.",
    ...
}
```

Translate ALL error strings from `en.py`. Every key in `en.VALIDATION_ERRORS` must have a corresponding entry in `pl.VALIDATION_ERRORS`.

### 2. Register `pl` module in `app/i18n/__init__.py`

```python
from app.i18n import en, pl

_LOCALE_MAP = {
    "en": en,
    "pl": pl,
}
```

### 3. Translate validation errors at route layer

In `app/routes/transactions.py`, after calling `validate_transaction()`, translate errors before passing to template:

```python
from app.i18n import translate_error

# In post_create_transaction and post_correct_transaction:
errors = validate_transaction(data, db)
locale = request.state.locale
errors = [translate_error(e, locale) for e in errors]
```

Do the same in `app/routes/auth.py` and `app/routes/settings.py` if they pass error strings to templates.

### 4. Translate flash messages at render time

Flash messages are stored in English in the session. They should be translated when rendered. Update the flash rendering in `base.html` or the flash middleware to translate the message:

```html
<!-- In base.html, translate flash message -->
{{ t(request.state.flash.message) if request.state.flash else '' }}
```

Or translate in the middleware/context before it reaches the template. Choose the cleanest approach. The flash message strings ("Transaction saved successfully.", etc.) must exist as keys in both `en.py` and `pl.py` MESSAGES dicts.

### 5. Add language switcher to `base.html`

Add a simple toggle in the nav area:

```html
<div class="lang-switch">
  {% if request.state.locale == 'pl' %}
  <strong>PL</strong> | <a href="/lang/en">EN</a>
  {% else %}
  <a href="/lang/pl">PL</a> | <strong>EN</strong>
  {% endif %}
</div>
```

### 6. Add language switch route

In `app/main.py` or a dedicated route file:

```python
@app.get("/lang/{locale}")
async def switch_language(locale: str, request: Request):
    if locale in ("en", "pl"):
        request.session["locale"] = locale
    referer = request.headers.get("referer", "/")
    return RedirectResponse(url=referer, status_code=302)
```

Add `/lang/en` and `/lang/pl` to `EXEMPT_PATHS` in `app/main.py` so they work without auth.

### 7. Minimal switcher styling in `static/style.css`

```css
.lang-switch {
  font-size: var(--font-size-sm);
  color: var(--color-muted-fg);
}

.lang-switch a {
  color: var(--color-muted-fg);
}

.lang-switch strong {
  color: var(--color-primary);
}
```

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all existing tests must pass (98 before T5 merges, 101 after)
```

- [ ] `app/i18n/pl.py` exists with complete `MESSAGES` and `VALIDATION_ERRORS`
- [ ] Every key in `en.py` has a corresponding Polish translation in `pl.py`
- [ ] App defaults to Polish — all labels, buttons, headings in Polish
- [ ] Language switcher visible in nav (PL | EN)
- [ ] Switching language changes all UI text
- [ ] Language preference persists across page loads (session)
- [ ] Validation errors display in the selected language
- [ ] Flash messages display in the selected language
- [ ] All existing tests pass — 98 before T5 merges, 101 after (validation assertions remain English internally)
- [ ] ruff clean

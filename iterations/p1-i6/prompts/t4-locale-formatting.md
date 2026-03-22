# I6-T4 — Locale-Aware Formatting

**Branch:** `feature/p1-i6/t4-locale-formatting` (from `feature/phase-1/iteration-6`)
**PR target:** `feature/phase-1/iteration-6`
**Depends on:** I6-T3 ✅ DONE

---

## Goal

Dates and amounts display according to the selected locale's conventions. Polish users see `23.03.2026` and `1 234,56`. English users see `2026-03-23` and `1,234.56`.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i6/prompt.md
app/i18n/__init__.py
app/main.py                                    (Jinja2 globals/filters)
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/dashboard.html
```

---

## Allowed Files

```
app/i18n/__init__.py                           ← extend (format functions)
app/main.py                                    ← modify (register Jinja2 filters)
app/templates/transactions/list.html           ← modify (use format filters)
app/templates/transactions/detail.html         ← modify (use format filters)
app/templates/dashboard.html                   ← modify (use format filters)
```

Do NOT modify routes, services, JS, CSS, or tests.

---

## What to Implement

### 1. Add formatting functions to `app/i18n/__init__.py`

```python
def format_date(value, locale: str) -> str:
    """Format a date string for display.

    Polish: 23.03.2026
    English: 2026-03-23 (ISO, unchanged)
    """
    if not value:
        return "—"
    if locale == "pl":
        # value is typically "YYYY-MM-DD" string or date object
        if hasattr(value, "strftime"):
            return value.strftime("%d.%m.%Y")
        # String parsing fallback
        parts = str(value).split("-")
        if len(parts) == 3:
            return f"{parts[2]}.{parts[1]}.{parts[0]}"
    return str(value)


def format_amount(value, locale: str) -> str:
    """Format an amount for display.

    Polish: 1 234,56 (space thousands, comma decimal)
    English: 1,234.56 (comma thousands, period decimal)
    """
    if value is None:
        return "—"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)

    if locale == "pl":
        # Format with 2 decimal places, then swap separators
        formatted = f"{num:,.2f}"  # "1,234.56"
        # Swap: comma → temp, period → comma, temp → space
        formatted = formatted.replace(",", "\x00").replace(".", ",").replace("\x00", "\u00a0")
        return formatted
    return f"{num:,.2f}"
```

Use `\u00a0` (non-breaking space) as the thousands separator for Polish to prevent line breaks mid-number.

### 2. Register Jinja2 filters in `app/main.py`

Make `format_date` and `format_amount` available as Jinja2 filters that automatically use the current locale:

```python
from app.i18n import format_date, format_amount

# After registering t() global, also register filters:
# These need locale from request.state — wrap them as closures or use a different approach

# Option A: Register as globals that take locale explicitly
# {{ format_date(t.date, request.state.locale) }}

# Option B: Register as filters that read locale from a context variable
# {{ t.date | format_date }}
```

**Recommended approach:** Register `format_date` and `format_amount` as Jinja2 globals (not filters) that take the value and locale:

```python
# In template usage:
{{ format_date(t.date, request.state.locale) }}
{{ format_amount(t.amount, request.state.locale) }}
```

This is explicit and avoids needing to pass locale through filter context. Choose whichever approach is cleanest — the requirement is that dates and amounts format correctly per locale.

### 3. Update templates

**`transactions/list.html`:**
- Date column: `{{ format_date(t.date, request.state.locale) }}`
- Amount column: `{{ format_amount(t.amount, request.state.locale) }}`

**`transactions/detail.html`:**
- Date field value
- Amount field value
- Created at timestamp (format date portion)

**`dashboard.html`:**
- Amount values in summary cards
- Dates in recent transactions table
- Opening balance amount (if numeric)

### 4. Do NOT format

- Form input values (date picker needs ISO format `YYYY-MM-DD`)
- Form input values for amounts (number input needs standard decimal)
- Data attributes (`data-amount`)
- Database values

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all 98 existing tests must pass
```

- [ ] Polish locale: dates show as `dd.mm.yyyy`
- [ ] Polish locale: amounts show as `1 234,56` (non-breaking space + comma)
- [ ] English locale: dates show as `yyyy-mm-dd`
- [ ] English locale: amounts show as `1,234.56`
- [ ] Form input values remain in standard format (ISO date, decimal amount)
- [ ] Dashboard, list, and detail pages all use formatting
- [ ] All 98 tests pass
- [ ] ruff clean

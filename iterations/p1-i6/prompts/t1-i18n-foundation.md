# I6-T1 — i18n Foundation + English Dictionary

**Branch:** `feature/p1-i6/t1-i18n-foundation` (from `feature/phase-1/iteration-6`)
**PR target:** `feature/phase-1/iteration-6`
**Depends on:** —

---

## Goal

Create the translation infrastructure so templates can call `{{ t('key') }}` and get localized text. After T1, the system has a working translation helper, language middleware, and an English dictionary — but templates still use hardcoded strings (T2 will extract them).

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i6/prompt.md                    (full iteration reference — translation strategy section)
app/main.py                                    (current middleware stack)
app/templates/base.html                        (current template structure)
app/services/validation.py                     (all error strings to catalogue)
```

---

## Allowed Files

```
app/i18n/__init__.py     ← create new
app/i18n/en.py           ← create new
app/main.py              ← modify (locale middleware, Jinja2 global)
```

Do NOT modify any template, route, service, or test file.

---

## What to Implement

### 1. Create `app/i18n/__init__.py`

```python
from app.i18n import en

_LOCALE_MAP = {
    "en": en,
}

DEFAULT_LOCALE = "pl"

def get_messages(locale: str) -> dict:
    """Return the MESSAGES dict for the given locale, fallback to English."""
    module = _LOCALE_MAP.get(locale, en)
    return module.MESSAGES

def translate(key: str, locale: str) -> str:
    """Look up a UI string. Fallback to English if missing, then to key itself."""
    module = _LOCALE_MAP.get(locale, en)
    return module.MESSAGES.get(key, en.MESSAGES.get(key, key))

def translate_error(error: str, locale: str) -> str:
    """Translate a validation error string. Fallback to English (original)."""
    module = _LOCALE_MAP.get(locale, en)
    return module.VALIDATION_ERRORS.get(error, error)
```

Note: `pl` module will be added in T3. Until then, `pl` locale falls back to English via the `en` default.

Update `_LOCALE_MAP` when `pl.py` is added in T3 — do NOT add a placeholder import for `pl` now.

### 2. Create `app/i18n/en.py`

Two dictionaries:

**`MESSAGES`** — all user-facing UI strings organized by section:

```python
MESSAGES = {
    # Navigation
    "nav_brand": "cashflow-tracker",
    "nav_transactions": "Transactions",
    "nav_new": "+ New",
    "nav_sign_out": "Sign out",
    "sandbox_banner": "SANDBOX — this is a test environment. Data may be discarded.",

    # Dashboard
    "dashboard_title": "Dashboard",
    "dashboard_opening_balance": "Opening Balance",
    "dashboard_as_of": "as of",
    "dashboard_not_set": "Not set",
    "dashboard_total_income": "Total Income",
    "dashboard_total_expenses": "Total Expenses",
    "dashboard_transactions": "Transactions",
    "dashboard_active": "active",
    "dashboard_voided": "voided",
    "dashboard_new_transaction": "+ New Transaction",
    "dashboard_view_all": "View All Transactions",
    "dashboard_recent": "Recent Transactions",
    "dashboard_no_transactions": "No transactions yet.",

    # Transaction form
    "form_title": "New transaction",
    "form_date": "Date",
    "form_direction": "Direction",
    "form_income": "Income",
    "form_expense": "Expense",
    "form_amount": "Amount",
    "form_amount_helper": "Enter gross amount (VAT included)",
    "form_category": "Category",
    "form_category_placeholder": "— select —",
    "form_payment_method": "Payment Method",
    "form_income_type": "Income Type",
    "form_income_type_internal": "Internal",
    "form_income_type_external": "External",
    "form_vat_rate": "VAT Rate (%)",
    "form_vat_deductible": "VAT Deductible (%)",
    "form_description": "Description",
    "form_description_required": "(required)",
    "form_description_placeholder": "Optional notes...",
    "form_save": "Save Transaction",
    "form_cancel": "Cancel",
    "form_card_reminder": "Log gross amount. Card commission is logged separately at month end from terminal invoice.",
    "form_error_heading": "Please fix the following errors:",

    # Transaction list
    "list_title": "Transactions",
    "list_new": "+ New Transaction",
    "list_show_active_only": "Show Active Only",
    "list_show_all": "Show All (incl. voided)",
    "list_split_view": "Split View",
    "list_combined_view": "Combined View",
    "list_col_id": "#",
    "list_col_date": "Date",
    "list_col_category": "Category",
    "list_col_direction": "Direction",
    "list_col_amount": "Amount",
    "list_col_payment": "Payment",
    "list_col_logged_by": "Logged by",
    "list_col_status": "Status",
    "list_no_transactions": "No transactions yet.",
    "list_create_first": "Create your first transaction",
    "list_income": "Income",
    "list_expenses": "Expenses",
    "list_no_income": "No income transactions",
    "list_no_expenses": "No expense transactions",

    # Badges
    "badge_active": "Active",
    "badge_voided": "Voided",
    "badge_corrected": "Corrected",

    # Transaction detail
    "detail_title": "Transaction",
    "detail_back": "← Back to list",
    "detail_date": "Date",
    "detail_direction": "Direction",
    "detail_category": "Category",
    "detail_amount_gross": "Amount (gross)",
    "detail_vat_rate": "VAT rate",
    "detail_income_type": "Income type",
    "detail_vat_deductible": "VAT deductible",
    "detail_payment": "Payment",
    "detail_description": "Description",
    "detail_logged_by": "Logged by",
    "detail_created_at": "Created at",
    "detail_correct": "Correct",
    "detail_void": "Void",
    "detail_correction_of": "This transaction is a correction of",

    # Void details
    "void_details_title": "Void Details",
    "void_reason": "Void reason",
    "voided_by": "Voided by",
    "voided_at": "Voided at",
    "replaced_by": "Replaced by",

    # Void page
    "void_title": "Void Transaction",
    "void_warning": "This action cannot be undone. The transaction will be marked as voided.",
    "void_reason_label": "Reason for voiding (required)",
    "void_reason_placeholder": "Why is this transaction being voided?",
    "void_submit": "Void Transaction",
    "void_cancel": "Cancel",

    # Auth
    "login_title": "Sign in",
    "login_username": "Username",
    "login_password": "Password",
    "login_submit": "Sign in",

    # Settings
    "settings_title": "Opening Balance Setup",
    "settings_description": "Set the starting cash position before logging transactions.",
    "settings_balance_label": "Opening balance (PLN)",
    "settings_date_label": "As of date",
    "settings_save": "Save opening balance",

    # Flash messages
    "flash_transaction_saved": "Transaction saved successfully.",
    "flash_transaction_voided": "Transaction voided.",
    "flash_transaction_corrected": "Transaction corrected. Original has been voided.",

    # Language
    "lang_switch_pl": "PL",
    "lang_switch_en": "EN",
}
```

**`VALIDATION_ERRORS`** — identity mapping of all validation.py error strings:

```python
VALIDATION_ERRORS = {
    "Date is required.": "Date is required.",
    "Date must be a valid YYYY-MM-DD value.": "Date must be a valid YYYY-MM-DD value.",
    "Direction must be income or expense.": "Direction must be income or expense.",
    "Amount must be a positive number.": "Amount must be a positive number.",
    "Amount must be greater than 0.": "Amount must be greater than 0.",
    "Category must be a valid category id.": "Category must be a valid category id.",
    "Payment method must be cash, card, or transfer.": "Payment method must be cash, card, or transfer.",
    "VAT rate must be one of 0, 5, 8, or 23.": "VAT rate must be one of 0, 5, 8, or 23.",
    "Income type is required for income transactions.": "Income type is required for income transactions.",
    "Income type must be internal or external.": "Income type must be internal or external.",
    "Income type must be empty for expense transactions.": "Income type must be empty for expense transactions.",
    "VAT deductible percentage is required for expense transactions.": "VAT deductible percentage is required for expense transactions.",
    "Internal income must use a VAT rate of 0.": "Internal income must use a VAT rate of 0.",
    "Internal income must use cash as payment method.": "Internal income must use cash as payment method.",
    "Category direction must match transaction direction.": "Category direction must match transaction direction.",
    "This category is not available for manual transactions.": "This category is not available for manual transactions.",
    "Description is required for other_expense and other_income.": "Description is required for other_expense and other_income.",
    "logged_by must be a valid user id.": "logged_by must be a valid user id.",
}
```

Read `app/services/validation.py` to verify you have captured ALL error strings. If there are any strings not listed above, add them.

### 3. Update `app/main.py`

Add `LocaleMiddleware`:

```python
class LocaleMiddleware(BaseHTTPMiddleware):
    """Read locale from session and expose on request state."""

    async def dispatch(self, request: Request, call_next):
        request.state.locale = request.session.get("locale", "pl")
        return await call_next(request)
```

Register it in `create_app()` alongside the other middleware (after SessionMiddleware, before or after FlashMessageMiddleware).

Register `t()` as a Jinja2 global. Since templates are created via `Jinja2Templates`, the cleanest approach is to add the global after app creation:

```python
from app.i18n import translate

# After app is created and routers are included:
# Make t() available in all templates
templates_env = None
for router in [settings_router, auth_router, dashboard_router, transactions_router]:
    for route in router.routes:
        if hasattr(route, 'dependant'):
            pass  # routes don't hold template refs
```

**Alternative (simpler):** Since each route module creates its own `Jinja2Templates` instance, add the global to each one. Or create a shared templates instance. Choose whichever approach is cleanest — the requirement is that `{{ t('key') }}` works in every template.

One clean approach: create a `get_templates()` helper that returns a configured `Jinja2Templates` with the `t` global, and use it in every route module.

The `t()` function passed to templates needs access to the current locale. It should accept a key and use `request.state.locale`:

```python
# In the template context, t is a closure over the current locale
def make_t(locale: str):
    def t(key: str) -> str:
        return translate(key, locale)
    return t
```

Pass `t` into every template context via middleware or a context processor pattern.

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all 98 existing tests must pass
```

- [ ] `app/i18n/__init__.py` exists with `translate()`, `translate_error()`, `get_messages()`
- [ ] `app/i18n/en.py` exists with `MESSAGES` and `VALIDATION_ERRORS` dicts
- [ ] `VALIDATION_ERRORS` covers ALL strings from `validation.py`
- [ ] `LocaleMiddleware` sets `request.state.locale` (default `pl`)
- [ ] `t()` function available in Jinja2 templates
- [ ] No template changes (that's T2)
- [ ] All 98 tests pass
- [ ] ruff clean

# I6-T2 — Template String Extraction

**Branch:** `feature/p1-i6/t2-template-extraction` (from `feature/phase-1/iteration-6`)
**PR target:** `feature/phase-1/iteration-6`
**Depends on:** I6-T1 ✅ DONE

---

## Goal

Replace every hardcoded user-facing string in every template with a `{{ t('key') }}` call. After T2, the app still shows English (only `en.py` exists) but all text flows through the translation system.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i6/prompt.md                    (translation strategy)
app/i18n/en.py                                 (all available keys)
app/templates/base.html
app/templates/dashboard.html
app/templates/transactions/create.html
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/transactions/void.html
app/templates/auth/login.html
app/templates/settings/opening_balance.html
```

---

## Allowed Files

```
app/templates/base.html                        ← modify
app/templates/dashboard.html                   ← modify
app/templates/transactions/create.html         ← modify
app/templates/transactions/list.html           ← modify
app/templates/transactions/detail.html         ← modify
app/templates/transactions/void.html           ← modify
app/templates/auth/login.html                  ← modify
app/templates/settings/opening_balance.html    ← modify
app/i18n/en.py                                 ← extend (add missing keys if discovered)
```

Do NOT modify routes, services, JS, CSS, or tests.

---

## What to Implement

### Extraction rules

1. **Replace** every hardcoded English string visible to the user with `{{ t('key') }}`.
2. **Do NOT translate:**
   - Free-text content: `{{ t.description }}`, `{{ t.void_reason }}`, usernames
   - Category labels: `{{ t.category_label }}` (from database)
   - Dynamic values: amounts, dates, IDs, percentages
   - HTML attributes: `placeholder` values should use `{{ t('key') }}`
   - `{% block title %}` content — use `{{ t('key') }}` here too
3. **Keep intact:** All HTML structure, CSS classes, Jinja2 logic blocks, form names/IDs/values.
4. **Format strings:** For strings like `"Transaction #{{ t.id }}"`, use concatenation: `{{ t('detail_title') }} #{{ t.id }}`.

### Templates to update

**`base.html`:**
- SANDBOX banner text → `{{ t('sandbox_banner') }}`
- Nav links: "Transactions" → `{{ t('nav_transactions') }}`, "+ New" → `{{ t('nav_new') }}`
- Sign out button text → `{{ t('nav_sign_out') }}`

**`dashboard.html`:**
- Page title, heading → `{{ t('dashboard_title') }}`
- Card labels: "Opening Balance", "Total Income", "Total Expenses", "Transactions"
- "active", "voided" labels
- "as of" text
- Button text: "+ New Transaction", "View All Transactions"
- "Recent Transactions" heading
- Empty state text

**`transactions/create.html`:**
- Page title, heading → `{{ t('form_title') }}`
- All form labels: Date, Direction, Income, Expense, Amount, Category, Payment Method, etc.
- Helper text: "Enter gross amount (VAT included)"
- Placeholder text: "— select —", "Optional notes..."
- "(required)" indicator
- Card reminder text
- Error heading: "Please fix the following errors:"
- Button text: "Save Transaction", "Cancel"

**`transactions/list.html`:**
- Page title, heading → `{{ t('list_title') }}`
- All column headers
- Badge text: "Active", "Voided", "Corrected"
- Toggle text: "Show Active Only", "Show All (incl. voided)"
- Empty state text
- Button text: "+ New Transaction", "Create your first transaction"
- Split view: "Split View", "Combined View", "Income", "Expenses", "No income transactions", "No expense transactions"

**`transactions/detail.html`:**
- Page title, heading
- Back link text
- All field labels (Date, Direction, Category, Amount, etc.)
- Badge text
- Audit labels: "Void Details", "Void reason", "Voided by", "Replaced by"
- Correction callout text
- Button text: "Correct", "Void"

**`transactions/void.html`:**
- Page title, heading
- Warning text
- Label text, placeholder
- Button text: "Void Transaction", "Cancel"

**`auth/login.html`:**
- Page title, heading → `{{ t('login_title') }}`
- Labels: "Username", "Password"
- Button: "Sign in"

**`settings/opening_balance.html`:**
- Page title, heading
- Description text
- Labels: "Opening balance (PLN)", "As of date"
- Button: "Save opening balance"

### Inline script strings (list.html split view)

The inline `<script>` in `list.html` has JS strings like "Split View", "Combined View", "No income transactions", "No expense transactions". These should be set from data attributes or template-rendered JS variables:

```html
<script>
var STRINGS = {
  splitView: '{{ t("list_split_view") }}',
  combinedView: '{{ t("list_combined_view") }}',
  noIncome: '{{ t("list_no_income") }}',
  noExpenses: '{{ t("list_no_expenses") }}'
};
</script>
```

Then use `STRINGS.splitView` etc. in the JS code instead of hardcoded strings.

---

## Acceptance Check

```bash
ruff check .
pytest -v   # all 98 existing tests must pass
```

- [ ] Every user-facing string in every template uses `{{ t('key') }}`
- [ ] App renders identically to before (English output unchanged)
- [ ] No HTML structure or CSS class changes
- [ ] All Jinja2 logic blocks intact
- [ ] Free-text content, category labels, and dynamic values NOT wrapped in `t()`
- [ ] Any new keys discovered during extraction added to `en.py`
- [ ] Inline JS strings in list.html use template-rendered variables
- [ ] All 98 tests pass
- [ ] ruff clean

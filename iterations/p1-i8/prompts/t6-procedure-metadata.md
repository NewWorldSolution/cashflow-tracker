# I8-T6 — Procedure Metadata UI

**Branch:** `feature/p1-i8/t6-procedure-metadata`
**Base:** `feature/phase-1/iteration-8` (after T5 merged)
**Depends on:** I8-T5

---

## Goal

Add customer_type selector, document_flow selector, and update for_accountant default behavior in the create and correct forms. After this task, all procedure metadata fields are captured during transaction entry with correct visibility rules and cross-field validation enforced in the UI.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md     ← internal cash_in consolidated rules table
app/routes/transactions.py
app/templates/transactions/create.html
app/templates/transactions/detail.html
static/form.js
app/i18n/en.py
app/i18n/pl.py
```

---

## Deliverables

### 1. Route changes in `app/routes/transactions.py`

#### Create route (GET)
- No new data to fetch — values are enum-like, defined in template

#### Create route (POST)
- Accept `customer_type` from form
- Accept `document_flow` from form (may be empty/null for cash_out or internal)
- Both pass through to validation (T3 already validates)

#### Correct route (GET)
- Pass stored `customer_type`, `document_flow`, `for_accountant` to template

#### Correct route (POST)
- Same as create POST

### 2. Template changes in `app/templates/transactions/create.html`

#### customer_type selector

```html
<div id="customer-type-section">
  <label for="customer_type">{{ t('form_customer_type') }}</label>
  <select id="customer_type" name="customer_type" required>
    <option value="">-- {{ t('select_customer_type') }} --</option>
    <option value="private">{{ t('customer_type_private') }}</option>
    <option value="company">{{ t('customer_type_company') }}</option>
    <option value="other">{{ t('customer_type_other') }}</option>
  </select>
</div>
```

- Required on ALL transactions
- Hidden and forced to `private` when `cash_in_type = internal`

#### document_flow selector

```html
<div id="document-flow-section">
  <label for="document_flow">{{ t('form_document_flow') }}</label>
  <select id="document_flow" name="document_flow">
    <option value="">-- {{ t('select_document_flow') }} --</option>
    <option value="invoice">{{ t('document_flow_invoice') }}</option>
    <option value="receipt">{{ t('document_flow_receipt') }}</option>
    <option value="invoice_and_receipt">{{ t('document_flow_invoice_and_receipt') }}</option>
    <option value="other_document">{{ t('document_flow_other_document') }}</option>
  </select>
</div>
```

Visibility rules:
- **External cash_in**: shown, required, default `receipt`
- **Internal cash_in**: hidden entirely
- **Cash out**: shown, optional, no default

#### for_accountant default change

- Create form: checkbox defaults to **checked** (true)
- Exception: when `cash_in_type = internal`, force unchecked and disable
- Correct form: shows the stored value — do NOT re-apply the default

#### Correction pre-selection

- `customer_type` dropdown pre-selects stored value
- `document_flow` dropdown pre-selects stored value
- `for_accountant` checkbox reflects stored value

### 3. JavaScript changes in `static/form.js`

#### customer_type visibility
- When `cash_in_type = internal`: hide customer_type section, set hidden input to `private`
- When switching away from internal: show customer_type section, clear forced value

#### document_flow visibility
- When direction = `cash_in` AND `cash_in_type = external`: show document_flow, set as required, default to `receipt`
- When direction = `cash_in` AND `cash_in_type = internal`: hide document_flow, clear value
- When direction = `cash_out`: show document_flow, set as optional (not required), no default
- When direction changes: re-evaluate visibility

#### invoice_and_receipt cross-field rule
- When `customer_type` changes: if value is NOT `private`, disable the `invoice_and_receipt` option in document_flow dropdown
- If `invoice_and_receipt` was selected and customer_type changes to non-private: reset document_flow to empty
- When `customer_type = private`: enable the `invoice_and_receipt` option

#### for_accountant behavior
- When `cash_in_type = internal`: uncheck and disable for_accountant checkbox
- When switching away from internal: re-enable checkbox (but don't force-check it — let user decide)
- Create mode: checkbox starts checked (default true)
- Correct mode: checkbox reflects stored value

### 4. i18n labels

Add to both `app/i18n/en.py` and `app/i18n/pl.py`:

| Key | EN | PL |
|-----|----|----|
| `form_customer_type` | Customer Type | Typ kontrahenta |
| `select_customer_type` | Select customer type | Wybierz typ kontrahenta |
| `customer_type_private` | Private Person | Osoba prywatna |
| `customer_type_company` | Company | Firma |
| `customer_type_other` | Other | Inny |
| `form_document_flow` | Document Flow | Obieg dokumentów |
| `select_document_flow` | Select document flow | Wybierz obieg dokumentów |
| `document_flow_invoice` | Invoice | Faktura |
| `document_flow_receipt` | Receipt | Paragon |
| `document_flow_invoice_and_receipt` | Invoice and Receipt | Faktura i paragon |
| `document_flow_other_document` | Other Document | Inny dokument |

---

## Important Rules

- **T3 already validates all cross-field rules** — the JS enforcement is for UX (disable invalid options, show/hide fields). The backend is the final authority.
- **Internal cash_in consolidated rules** — customer_type forced to `private` (hidden), document_flow hidden (NULL), for_accountant forced to `false`. These must work together with the existing internal cash_in JS logic from earlier tasks.
- **invoice_and_receipt only for private** — this is both a JS UX rule and a backend validation rule.
- **Correction does NOT re-apply defaults** — it shows stored values. This applies to for_accountant, customer_type, and document_flow.
- **Do NOT modify list/detail/dashboard** — that is T7's job.

---

## Allowed Files

```text
app/routes/transactions.py
app/templates/transactions/create.html
app/templates/transactions/detail.html
static/form.js
app/i18n/en.py
app/i18n/pl.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] customer_type selector appears on all transactions
- [ ] customer_type forced to `private` and hidden for internal cash_in
- [ ] document_flow appears for external cash_in (required, default `receipt`)
- [ ] document_flow hidden for internal cash_in
- [ ] document_flow appears for cash_out (optional, no default)
- [ ] invoice_and_receipt option disabled when customer_type != private
- [ ] for_accountant defaults to checked in create form
- [ ] for_accountant forced unchecked for internal cash_in
- [ ] Correct form pre-selects all stored values without re-defaulting
- [ ] All i18n labels added (EN + PL)
- [ ] `ruff check .` passes
- [ ] Form submits successfully with all metadata fields

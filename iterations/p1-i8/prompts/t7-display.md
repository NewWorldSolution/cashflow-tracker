# I8-T7 — List/Detail/Dashboard Display

**Branch:** `feature/p1-i8/t7-display`
**Base:** `feature/phase-1/iteration-8` (after T6 merged)
**Depends on:** I8-T6

---

## Goal

Update the list view, detail view, and dashboard to surface I8 data correctly.

- **List view**: category path (Parent > Subcategory) and translated direction labels. No metadata columns.
- **Detail view**: full category path, manual VAT indicator, customer_type, document_flow (when present), and for_accountant.
- **Dashboard**: translated `cash_in`/`cash_out` direction labels and VAT-mode-aware aggregations. Category breakdown by parent group only if the dashboard already has a category breakdown — do not add one if it does not exist.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/dashboard.html
app/routes/dashboard.py
app/routes/transactions.py
```

---

## Deliverables

### 1. Route changes

#### `app/routes/transactions.py` — list route
- Ensure category path (Parent > Child) is available for each transaction in the list
- Use the category path helper from T3
- Pass `direction` display values using new labels (`cash_in`/`cash_out` → translated)

#### `app/routes/transactions.py` — detail route
- Pass all new fields to the detail template: `vat_mode`, `manual_vat_amount`, `manual_vat_deductible_amount`, `customer_type`, `document_flow`, `for_accountant`
- Pass category path string
- Pass calculated values using the correct mode (automatic vs manual) from T3 calculations

#### `app/routes/dashboard.py`
- Update any aggregation queries to use `cash_in`/`cash_out` direction values
- If dashboard shows category breakdown, use parent groups for grouping
- Ensure VAT calculations use the correct mode per transaction

### 2. List view — `app/templates/transactions/list.html`

- **Category column**: Show `Parent > Subcategory` path instead of flat category name
- **Direction column**: Show translated `cash_in`/`cash_out` labels
- **No manual VAT marker needed** in list (per scope-decisions.md)
- **No customer_type/document_flow needed** in list

### 3. Detail view — `app/templates/transactions/detail.html`

Show all new information:

#### Category
- Display as "Parent Group > Subcategory" (e.g., "Services > Test")
- Use translated labels

#### VAT section
- Show `vat_mode` (Automatic / Manual)
- When manual: show `manual_vat_amount` and `manual_vat_deductible_amount` (cash_out only)
- When manual: show a visible indicator (e.g., small badge or label) that manual VAT was used
- When automatic: show `vat_rate` and derived values as before

#### Procedure metadata
- `customer_type`: show translated label (Private Person / Company / Other)
- `document_flow`: show translated label — only if value is not NULL
- `for_accountant`: show Yes/No indicator

#### Calculated values (detail)
- `vat_amount`: use manual value when `vat_mode = manual`, derived when automatic
- `net_amount`: `amount - vat_amount`
- `vat_reclaimable` (cash_out): manual deductible when manual mode, derived when automatic
- `effective_cost` (cash_out): calculated correctly per mode

### 4. Dashboard — `app/templates/dashboard.html`

- Update direction labels from income/expense to cash_in/cash_out (translated)
- If category breakdown exists: group by parent category
- Ensure totals and aggregations work with both VAT modes
- No need to show manual VAT indicator on dashboard

### 5. i18n labels

Add to both `app/i18n/en.py` and `app/i18n/pl.py`:

| Key | EN | PL |
|-----|----|----|
| `direction_cash_in` | Cash In | Wpływ |
| `direction_cash_out` | Cash Out | Wydatek |
| `detail_vat_mode` | VAT Mode | Tryb VAT |
| `detail_manual_vat_indicator` | Manual VAT | Ręczny VAT |
| `detail_customer_type` | Customer Type | Typ kontrahenta |
| `detail_document_flow` | Document Flow | Obieg dokumentów |
| `detail_for_accountant` | For Accountant | Dla księgowej |
| `detail_category_path` | Category | Kategoria |
| `value_yes` | Yes | Tak |
| `value_no` | No | Nie |

Note: `direction_cash_in`/`direction_cash_out` may already exist from T1 i18n updates. Check before adding duplicates.

---

## Important Rules

- **Category path format**: "Parent > Subcategory" using translated labels
- **Manual VAT indicator**: visible in detail view only, not in list or dashboard
- **Calculations must respect vat_mode** — do not assume automatic mode everywhere
- **Do NOT modify create/correct forms** — those are done in T4-T6
- **Do NOT modify tests** — that is T8's job
- **Direction display**: use translated labels, not raw `cash_in`/`cash_out` strings

---

## Allowed Files

```text
app/routes/transactions.py
app/routes/dashboard.py
app/templates/transactions/list.html
app/templates/transactions/detail.html
app/templates/dashboard.html
app/i18n/en.py
app/i18n/pl.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] List view shows "Parent > Subcategory" for each transaction
- [ ] List view shows translated direction labels
- [ ] Detail view shows full category path
- [ ] Detail view shows VAT mode with manual indicator when applicable
- [ ] Detail view shows manual VAT amounts when vat_mode = manual
- [ ] Detail view shows customer_type with translated label
- [ ] Detail view shows document_flow when present
- [ ] Detail view shows for_accountant status
- [ ] Detail view calculations correct for both automatic and manual VAT modes
- [ ] Dashboard uses cash_in/cash_out direction labels
- [ ] Dashboard aggregations work with both VAT modes
- [ ] All new i18n labels added (EN + PL)
- [ ] `ruff check .` passes

# I8-T4 — Category Picker UI

**Branch:** `feature/p1-i8/t4-category-picker`
**Base:** `feature/phase-1/iteration-8` (after T3 merged)
**Depends on:** I8-T3

---

## Goal

Replace the flat category dropdown with a two-level category picker in both create and correct forms. The user selects a parent group first, then a subcategory populates in a second dropdown. Only leaf nodes are submitted. Correction pre-selects both levels from the stored category.

---

## Read Before Starting

```text
CLAUDE.md
iterations/p1-i8/prompt.md
iterations/p1-i8/scope-decisions.md
iterations/p1-i8/category-taxonomy.md
app/routes/transactions.py
app/templates/transactions/create.html
static/form.js
```

---

## Deliverables

### 1. Route changes in `app/routes/transactions.py`

#### Create route (GET)
- Fetch all categories with hierarchy (parents + children) for the current direction
- Pass hierarchy data to template as a structured object (e.g., list of parent groups, each with their children)
- Include VAT defaults per subcategory for JS auto-fill

#### Create route (POST)
- Accept `category_id` from the form (this is always a leaf node ID)
- Pass through to validation (T3 already validates leaf-only)

#### Correct route (GET)
- Fetch the stored transaction's category
- Look up the parent group of the stored category
- Pass both parent_id and category_id to the template for pre-selection
- Include same hierarchy data as create

#### Correct route (POST)
- Same as create POST — accept leaf category_id

### 2. Template changes in `app/templates/transactions/create.html`

Replace the single category dropdown with two dropdowns:

```html
<!-- Parent Group -->
<select id="category_group" name="category_group">
  <option value="">-- {{ t('select_category_group') }} --</option>
  {% for parent in category_groups %}
    <option value="{{ parent.category_id }}">{{ t('cat_' ~ parent.name) }}</option>
  {% endfor %}
</select>

<!-- Subcategory (populated by JS) -->
<select id="category_id" name="category_id">
  <option value="">-- {{ t('select_subcategory') }} --</option>
</select>
```

- `category_group` is NOT submitted to the server — it only drives the JS cascade
- `category_id` is the actual submitted value (always a leaf node)
- Both dropdowns should filter by the current direction (cash_in/cash_out) — the direction toggle already exists in the form

#### Hierarchy data for JS

Embed category hierarchy as a JSON script block on page load:

```html
<script>
  window.CATEGORY_HIERARCHY = {{ category_hierarchy_json | safe }};
</script>
```

Structure:
```json
{
  "cash_in": [
    {
      "id": 1, "slug": "ci_services", "label": "Services",
      "children": [
        {"id": 101, "slug": "ci_services_test", "label": "Test", "vat_rate": 23, "vat_deductible_pct": null},
        ...
      ]
    },
    ...
  ],
  "cash_out": [...]
}
```

#### Correction pre-selection

When in correction mode, the template must set initial values:
- `category_group` dropdown pre-selects the parent group
- `category_id` dropdown is populated with the parent's children and pre-selects the stored subcategory

### 3. JavaScript changes in `static/form.js`

#### Category cascade logic
- When `category_group` changes: populate `category_id` dropdown with children of the selected parent
- When `category_id` changes: auto-fill VAT defaults from the selected subcategory's data
- When direction changes (cash_in ↔ cash_out): reset both dropdowns and repopulate parent groups for the new direction

#### VAT auto-fill from category
- When a subcategory is selected, set `vat_rate` to the category's `default_vat_rate`
- For cash_out: also set `vat_deductible_pct` to the category's `default_vat_deductible_pct`
- Only auto-fill if the user hasn't manually changed these fields (or always auto-fill on category change — match existing behavior)

#### Correction initialization
- On page load in correction mode: trigger the cascade to populate the subcategory dropdown based on the pre-selected parent group
- Ensure the stored subcategory remains selected after population

### 4. i18n labels

Add to both `app/i18n/en.py` and `app/i18n/pl.py`:

| Key | EN | PL |
|-----|----|----|
| `select_category_group` | Select category group | Wybierz grupę kategorii |
| `select_subcategory` | Select subcategory | Wybierz podkategorię |
| `form_category_group` | Category Group | Grupa kategorii |
| `form_subcategory` | Subcategory | Podkategoria |

---

## Important Rules

- **No API calls** — all hierarchy data is embedded on page load via the JSON block
- **Vanilla JS only** — no frameworks, no fetch calls for cascade
- **Only leaf nodes are selectable** — parent groups are for grouping only, not submittable
- **category_group is cosmetic** — it is NOT sent to the server. Only `category_id` (leaf) is submitted
- **Do NOT add VAT mode toggle** — that is T5's job
- **Do NOT add customer_type or document_flow** — that is T6's job
- **Direction change resets categories** — when user switches cash_in ↔ cash_out, both dropdowns must reset and show the correct parent groups

---

## Allowed Files

```text
app/routes/transactions.py
app/templates/transactions/create.html
static/form.js
app/i18n/en.py
app/i18n/pl.py
iterations/p1-i8/tasks.md
```

---

## Acceptance Criteria

- [ ] Create form shows two-level category picker (parent group → subcategory)
- [ ] Selecting a parent group populates subcategory dropdown with its children
- [ ] Selecting a subcategory auto-fills VAT defaults
- [ ] Only leaf category_id is submitted to the server
- [ ] Direction change resets and repopulates category groups
- [ ] Correct form pre-selects both parent group and subcategory from stored values
- [ ] Hierarchy data is embedded as JSON — no API calls
- [ ] i18n labels added for category picker elements (EN + PL)
- [ ] `ruff check .` passes
- [ ] Form submits successfully with new category picker

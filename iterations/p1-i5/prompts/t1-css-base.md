# I5-T1 — CSS System + Base Template

**Branch:** `feature/p1-i5/t1-css-base` (from `feature/phase-1/iteration-5`)
**PR target:** `feature/phase-1/iteration-5`

---

## Goal

Establish the visual foundation for the entire app. Create the CSS system and update the base template. Every subsequent I5 task builds on this.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i5/prompt.md               (full iteration context + design reference)
app/templates/base.html
Minimal Transaction Entry Form/src/styles/theme.css
```

---

## Allowed Files

```
static/style.css             ← create new
app/templates/base.html      ← modify
```

Do NOT modify any other file.

---

## What to Implement

### 1. Create `static/style.css`

**CSS custom properties (top of file):**

```css
:root {
  /* Colors — derived from design reference */
  --color-primary: #030213;
  --color-primary-fg: #ffffff;
  --color-muted: #ececf0;
  --color-muted-fg: #717182;
  --color-input-bg: #f3f3f5;
  --color-destructive: #d4183d;
  --color-destructive-fg: #ffffff;
  --color-success: #16a34a;
  --color-success-fg: #ffffff;
  --color-border: rgba(0, 0, 0, 0.1);
  --color-border-strong: rgba(0, 0, 0, 0.2);
  --color-hover: #f9fafb;
  --color-body-bg: #ffffff;
  --color-card-bg: #ffffff;

  /* Spacing */
  --radius: 10px;
  --radius-sm: 6px;
  --radius-md: 8px;

  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-size-base: 16px;
  --font-size-sm: 14px;
  --font-size-xs: 12px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
}
```

**Base element styles:**
- `body`: font-family, font-size, line-height, color, background
- `h1–h4`: font-weight 500, appropriate sizes, margin
- `a`: color primary, underline on hover
- `table`: border-collapse, full width, border
- `th`: muted background, font-weight 500, text-align left, padding
- `td`: padding, border-bottom
- `tr:hover`: hover background
- `input, select, textarea`: border, border-radius, padding (px-3 py-2), background input-bg, font-size base, full width
- `input:focus, select:focus, textarea:focus`: border-color primary, outline ring
- `button`: cursor pointer, font-size base, font-weight 500

**Component classes:**

```css
/* Layout */
.container { max-width: 1152px; margin: 0 auto; padding: 0 16px; }
.container-narrow { max-width: 672px; margin: 0 auto; padding: 0 16px; }

/* Cards */
.card { background: var(--color-card-bg); border: 1px solid var(--color-border); border-radius: var(--radius); padding: 24px; }

/* Buttons */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 8px 16px; border-radius: var(--radius-sm); font-weight: 500; font-size: var(--font-size-base); border: 1px solid var(--color-border); background: var(--color-body-bg); color: var(--color-primary); cursor: pointer; transition: background-color 0.15s; text-decoration: none; }
.btn:hover { background: var(--color-hover); }
.btn-primary { background: var(--color-primary); color: var(--color-primary-fg); border-color: var(--color-primary); }
.btn-primary:hover { opacity: 0.9; }
.btn-secondary { background: var(--color-body-bg); color: var(--color-primary); border-color: var(--color-border-strong); }
.btn-destructive { background: var(--color-destructive); color: var(--color-destructive-fg); border-color: var(--color-destructive); }
.btn-destructive:hover { opacity: 0.9; }
.btn-lg { padding: 12px 24px; }
.btn-sm { padding: 6px 12px; font-size: var(--font-size-sm); }

/* Toggle buttons (direction selector) */
.toggle-group { display: flex; gap: 12px; }
.toggle-btn { flex: 1; padding: 10px 16px; border: 1px solid var(--color-border-strong); border-radius: var(--radius-sm); background: var(--color-body-bg); color: #374151; font-weight: 500; text-align: center; cursor: pointer; transition: all 0.15s; }
.toggle-btn:hover { background: var(--color-hover); }
.toggle-btn.active { background: var(--color-primary); color: var(--color-primary-fg); border-color: var(--color-primary); }

/* Badges */
.badge { display: inline-block; padding: 2px 8px; border-radius: 9999px; font-size: var(--font-size-xs); font-weight: 500; }
.badge-active { background: #dcfce7; color: #166534; }
.badge-voided { background: #fee2e2; color: #991b1b; }

/* Flash messages */
.flash { padding: 12px 16px; border-radius: var(--radius-sm); margin-bottom: 16px; border: 1px solid; }
.flash-success { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.flash-error { background: #fef2f2; border-color: #fecaca; color: #991b1b; }

/* Form sections */
.form-section { border: 1px solid var(--color-border); border-radius: var(--radius); padding: 24px; margin-bottom: 16px; }
.form-section-alt { background: var(--color-hover); }
.form-group { margin-bottom: 16px; }
.form-group:last-child { margin-bottom: 0; }
.form-label { display: block; font-weight: 500; margin-bottom: 6px; font-size: var(--font-size-base); }
.form-helper { font-size: var(--font-size-sm); color: var(--color-muted-fg); margin-top: 4px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-error { font-size: var(--font-size-sm); color: var(--color-destructive); margin-top: 4px; }

/* Error summary */
.error-summary { padding: 16px; border: 1px solid var(--color-border); background: var(--color-hover); border-radius: var(--radius-sm); margin-bottom: 16px; }
.error-summary ul { margin: 8px 0 0 0; padding-left: 20px; }
.error-summary li { color: var(--color-destructive); margin-bottom: 4px; }

/* Info callout (card reminder etc.) */
.callout { padding: 12px 16px; border-radius: var(--radius-sm); border: 1px solid; font-size: var(--font-size-sm); }
.callout-info { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }
.callout-warning { background: #fffbeb; border-color: #fed7aa; color: #92400e; }

/* Utility */
.text-muted { color: var(--color-muted-fg); }
.text-sm { font-size: var(--font-size-sm); }
.text-right { text-align: right; }
.text-center { text-align: center; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.mb-4 { margin-bottom: 16px; }
.mb-6 { margin-bottom: 24px; }
.gap-3 { gap: 12px; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.hidden { display: none; }

/* Table responsive wrapper */
.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }

/* Voided row styling */
.row-voided { opacity: 0.5; }
.row-voided .amount { text-decoration: line-through; }

/* Empty state */
.empty-state { text-align: center; padding: 48px 16px; color: var(--color-muted-fg); }
```

**SANDBOX banner:**
```css
.sandbox-banner { background: #fef3c7; color: #92400e; text-align: center; padding: 8px; font-weight: 500; font-size: var(--font-size-sm); border-bottom: 1px solid #fed7aa; }
```

**Navigation:**
```css
.nav { display: flex; align-items: center; gap: 24px; padding: 12px 16px; border-bottom: 1px solid var(--color-border); background: var(--color-body-bg); }
.nav-brand { font-weight: 500; font-size: var(--font-size-lg); color: var(--color-primary); text-decoration: none; }
.nav-links { display: flex; gap: 16px; }
.nav-links a { color: var(--color-muted-fg); text-decoration: none; font-size: var(--font-size-sm); font-weight: 500; }
.nav-links a:hover, .nav-links a.active { color: var(--color-primary); }
.nav-right { margin-left: auto; }
```

**Responsive breakpoints:**
```css
@media (max-width: 767px) {
  .form-row { grid-template-columns: 1fr; }
  .container { padding: 0 12px; }
}
```

### 2. Update `app/templates/base.html`

- Add in `<head>`:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="/static/style.css">
  ```
- Restructure nav using `.nav`, `.nav-brand`, `.nav-links` classes
- Add flash message rendering after nav, before content. The flash must be popped from the session **in Python** (middleware or context processor), not in the Jinja2 template. The template just renders if present:
  ```html
  {% if flash %}
  <div class="flash flash-{{ flash.type }}">{{ flash.message }}</div>
  {% endif %}
  ```
  The middleware/context processor should `request.session.pop("flash", None)` and inject it into the template context. This ensures the clearing contract is in Python, not in Jinja2. Implementation can be a simple ASGI middleware that sets `request.state.flash` before the route handler runs, or a helper function called in each route — either is acceptable as long as the pop happens in Python.
- Keep SANDBOX banner with improved `.sandbox-banner` class
- Wrap content block in `.container`

---

## Acceptance Check

```bash
python -c "
import os
assert os.path.exists('static/style.css'), 'style.css missing'
print('style.css exists')
"
ruff check .
pytest -v   # all 94 existing tests must pass — template changes must not break anything
```

- [ ] `style.css` loads when app runs (check browser dev tools)
- [ ] Viewport meta tag present
- [ ] Nav renders with brand + links
- [ ] Flash message block present (renders nothing when no flash)
- [ ] SANDBOX banner visible
- [ ] Content wrapped in container
- [ ] Mobile breakpoint active at < 768px

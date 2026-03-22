# Review — I5-T1: CSS System + Base Template
**Branch:** `feature/p1-i5/t1-css-base`
**PR target:** `feature/phase-1/iteration-5`

---

## Reviewer Role

Review only the changes in this task branch. Report precise problems with file references and why they matter. Do not fix.

**Verdict options:** `PASS` | `CHANGES REQUIRED` | `BLOCKED`

---

## What was supposed to be built

- New file: `static/style.css` — CSS custom properties, base element styles, component classes
- Modified: `app/templates/base.html` — viewport meta, CSS link, nav, flash rendering, SANDBOX banner

---

## Review steps

1. Confirm diff scope is only `static/style.css` and `app/templates/base.html`.
2. Verify `style.css` has CSS custom properties for colors, spacing, radius, typography.
3. Verify base element styles: body, headings, tables, forms, buttons, inputs.
4. Verify component classes exist: `.container`, `.card`, `.btn*`, `.flash*`, `.badge*`, `.toggle-group`, `.toggle-btn`, `.form-section`, `.form-group`, `.form-row`, `.error-summary`, `.callout*`.
5. Verify responsive breakpoints (mobile-first, 768px/1024px).
6. Verify `base.html` has viewport meta tag, CSS link, improved nav, flash rendering block.
7. Verify flash mechanism: pop happens in Python (middleware/context processor), not in Jinja2 template.
8. Verify SANDBOX banner still present.
9. Run:

```bash
pytest -v   # all 94 tests must pass
ruff check .
```

---

## Required output format

### 1. Verdict

```
PASS | CHANGES REQUIRED | BLOCKED
```

### 2. What's Correct

List every correct item with file references.

### 3. Problems Found

```
- severity: critical | major | minor
  file: path/to/file:LINE
  exact problem: ...
  why it matters: ...
```

If none: `None.`

### 4. Scope Violations

Files modified outside `static/style.css` and `app/templates/base.html`.

### 5. Acceptance Criteria Check

- [PASS|FAIL] diff scope limited to allowed files
- [PASS|FAIL] CSS custom properties defined (colors, spacing, radius, typography)
- [PASS|FAIL] base element styles present
- [PASS|FAIL] component classes present (btn, card, flash, badge, toggle, form-section, etc.)
- [PASS|FAIL] responsive breakpoints (mobile-first)
- [PASS|FAIL] viewport meta tag in base.html
- [PASS|FAIL] CSS link in base.html head
- [PASS|FAIL] nav improved with consistent styling
- [PASS|FAIL] flash rendering block present (pop in Python, render in Jinja2)
- [PASS|FAIL] SANDBOX banner present
- [PASS|FAIL] system font stack (no external fonts)
- [PASS|FAIL] all 94 tests pass
- [PASS|FAIL] ruff clean

### 6. Exact Fixes Required

Numbered list. If PASS: `None.`

# I4-T3 — Void/Correct Templates

**Owner:** Claude Code  
**Branch:** `feature/p1-i4/t3-templates` (from `feature/phase-1/iteration-4`)  
**PR target:** `feature/phase-1/iteration-4`  
**Depends on:** I4-T2 ✅ DONE

---

## Goal

Add the transaction detail and void templates, plus the two minimal template edits required for the correct/detail flow.

---

## Read Before Starting

```
CLAUDE.md
iterations/p1-i4/prompt.md
iterations/p1-i4/prompts/t2-routes.md
app/templates/transactions/create.html
app/templates/transactions/list.html
```

---

## Allowed Files

```
app/templates/transactions/detail.html
app/templates/transactions/void.html
app/templates/transactions/create.html
app/templates/transactions/list.html
```

Do NOT modify any other file.

---

## What to Implement

- Create `detail.html` per the iteration spec:
  - back link to list
  - display-only fields
  - conditional income/expense sections
  - void metadata when inactive
  - active rows show `Void this transaction` and `Correct this transaction` links
- Create `void.html` per the iteration spec:
  - cancel link back to detail
  - short transaction summary
  - inline errors list
  - `void_reason` input
  - submit button
- In `create.html`, change the form action to:

```html
<form method="post" action="{{ form_action | default('/transactions/new') }}">
```

- In `list.html`, change the date cell to:

```html
<td><a href="/transactions/{{ t.id }}">{{ t.date }}</a></td>
```

---

## Acceptance Check

```bash
python -c "from fastapi.templating import Jinja2Templates; Jinja2Templates(directory='app/templates'); print('templates loadable ok')"
```

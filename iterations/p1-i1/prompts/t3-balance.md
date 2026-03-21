# I1-T3 — Opening Balance Route
**Agent:** Codex
**Branch:** `feature/p1-i1/t3-balance`
**PR target:** `feature/phase-1/iteration-1`

---

## Context

cashflow-tracker is a private cash flow notebook for a 3-person Polish service business. This task implements one FastAPI route file: `GET` and `POST /settings/opening-balance`.

**This task has no file navigation.** Everything you need is in this prompt.

---

## What already exists (do not recreate)

### Database tables (created by I1-T1)

```sql
-- settings table
CREATE TABLE IF NOT EXISTS settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- settings_audit table — receives a row on every write to settings
CREATE TABLE IF NOT EXISTS settings_audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    key        TEXT NOT NULL,
    old_value  TEXT,        -- NULL on first write, not empty string
    new_value  TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `get_db` dependency (created by I1-T2)

```python
# From app/main.py — import exactly like this
from app.main import get_db

# Signature
def get_db() -> sqlite3.Connection:
    """Yields a sqlite3.Connection with row_factory = sqlite3.Row."""
    ...
```

---

## What to build

### One file only

```
app/routes/settings.py
```

Do not create any other file.

---

## app/routes/settings.py — implement this exactly

```python
import sqlite3
from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.main import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/settings/opening-balance", response_class=HTMLResponse)
async def get_opening_balance(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> HTMLResponse:
    """Render the opening balance setup form.

    Pre-populates the form with current values if already set.
    """
    row = db.execute(
        "SELECT value FROM settings WHERE key = 'opening_balance'"
    ).fetchone()
    current_balance = row["value"] if row else None

    row_date = db.execute(
        "SELECT value FROM settings WHERE key = 'as_of_date'"
    ).fetchone()
    current_date = row_date["value"] if row_date else str(date.today())

    return templates.TemplateResponse(
        "settings/opening_balance.html",
        {
            "request": request,
            "current_balance": current_balance,
            "current_date": current_date,
            "error": None,
        },
    )


@router.post("/settings/opening-balance")
async def post_opening_balance(
    request: Request,
    opening_balance: float = Form(...),
    as_of_date: str = Form(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """Save opening balance and as_of_date to settings table.

    Validates inputs. Writes an audit row to settings_audit for every change,
    including the first (old_value = NULL on first write).
    Redirects to / on success.

    Raises:
        HTTPException(400): if opening_balance <= 0 or as_of_date is invalid ISO 8601.
    """
    errors = []

    # Validate opening_balance
    if opening_balance <= 0:
        errors.append("Opening balance must be greater than zero.")

    # Validate as_of_date — must be valid ISO 8601 (YYYY-MM-DD)
    try:
        date.fromisoformat(as_of_date)
    except ValueError:
        errors.append("Date must be in YYYY-MM-DD format (e.g. 2026-01-01).")

    if errors:
        return templates.TemplateResponse(
            "settings/opening_balance.html",
            {
                "request": request,
                "current_balance": opening_balance,
                "current_date": as_of_date,
                "error": " ".join(errors),
            },
            status_code=400,
        )

    # Save each key with audit row
    for key, new_value in [
        ("opening_balance", str(opening_balance)),
        ("as_of_date", as_of_date),
    ]:
        old_row = db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        old_value = old_row["value"] if old_row else None

        db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
            (key, new_value),
        )
        db.execute(
            "INSERT INTO settings_audit (key, old_value, new_value) VALUES (?, ?, ?)",
            (key, old_value, new_value),
        )

    db.commit()
    return RedirectResponse(url="/", status_code=302)
```

---

## Rules

- **Validation errors** → return the template with `status_code=400` and inline `error` message. Do **not** raise `HTTPException`. The form must not reset — preserve user input.
- **`old_value`** → must be `None` (Python) / `NULL` (SQL) on first write, not an empty string.
- **`as_of_date`** → store only valid ISO 8601 strings. Reject anything that fails `date.fromisoformat()`.
- **`opening_balance = 0`** → rejected. Must be strictly greater than zero.
- **`opening_balance < 0`** → rejected.
- **Both keys** (`opening_balance` and `as_of_date`) are saved and audited in one request.
- **No validation logic** outside this route file — do not add validation to `app/main.py`.
- **No `except: pass`** — let exceptions propagate unless you explicitly handle them.

---

## Worktree setup

```bash
git fetch origin
git checkout feature/phase-1/iteration-1

# Confirm I1-T1 is merged: db/ and seed/ must exist
ls db/schema.sql

# Create worktree
git worktree add -b feature/p1-i1/t3-balance ../cashflow-tracker-t3 feature/phase-1/iteration-1
cd ../cashflow-tracker-t3

# Confirm I1-T2 is merged: app/main.py must exist and export get_db
python -c "from app.main import get_db; print('get_db OK')"
```

If either check fails, I1-T1 or I1-T2 is not yet merged. Wait.

---

## PR

```bash
git add app/routes/settings.py
git commit -m "feat: opening balance GET/POST route with settings_audit trail (I1-T3)"
git push -u origin feature/p1-i1/t3-balance
gh pr create \
  --base feature/phase-1/iteration-1 \
  --head feature/p1-i1/t3-balance \
  --title "I1-T3: Opening balance route" \
  --body "GET/POST /settings/opening-balance. Saves to settings table, writes audit row to settings_audit (old_value=NULL on first write). Rejects balance <= 0 and malformed dates. Errors shown inline."
```

Update `iterations/p1-i1/tasks.md` — set I1-T3 to ✅ DONE.

---

## Acceptance checklist

- [ ] GET `/settings/opening-balance` renders form with pre-populated values if already set
- [ ] POST with valid data saves to settings table (both keys) and writes 2 audit rows to settings_audit
- [ ] First write: `old_value` is NULL in settings_audit, not empty string
- [ ] POST with `opening_balance = 0` → 400, error message shown inline, form not reset
- [ ] POST with `opening_balance = -100` → 400
- [ ] POST with `as_of_date = "21-03-2026"` → 400 (wrong format)
- [ ] POST with `as_of_date = "2026-01-01"` → accepted
- [ ] No hard-coded strings for error routing — redirect to `/` on success only
- [ ] No `except: pass`

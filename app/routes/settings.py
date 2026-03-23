import sqlite3
from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.i18n import translate_error
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
        request,
        "settings/opening_balance.html",
        {
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
        locale = request.state.locale
        errors = [translate_error(e, locale) for e in errors]
        return templates.TemplateResponse(
            request,
            "settings/opening_balance.html",
            {
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

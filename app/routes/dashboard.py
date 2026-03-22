import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.main import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> HTMLResponse:
    """Dashboard with summary cards, quick actions, and recent transactions."""
    # Opening balance from settings key-value table
    opening_balance_row = db.execute(
        "SELECT value FROM settings WHERE key = 'opening_balance'"
    ).fetchone()
    as_of_date_row = db.execute(
        "SELECT value FROM settings WHERE key = 'as_of_date'"
    ).fetchone()
    opening_balance = opening_balance_row["value"] if opening_balance_row else None
    as_of_date = as_of_date_row["value"] if as_of_date_row else None

    # Transaction counts
    active_count = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE is_active = 1"
    ).fetchone()[0]
    voided_count = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE is_active = 0"
    ).fetchone()[0]

    # Totals (active only)
    total_income = db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions "
        "WHERE is_active = 1 AND direction = 'income'"
    ).fetchone()[0]
    total_expense = db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions "
        "WHERE is_active = 1 AND direction = 'expense'"
    ).fetchone()[0]

    # Recent 5 active transactions with category label
    recent = db.execute(
        "SELECT t.id, t.date, t.amount, t.direction, c.label AS category_label, "
        "t.payment_method "
        "FROM transactions t JOIN categories c ON t.category_id = c.category_id "
        "WHERE t.is_active = 1 ORDER BY t.created_at DESC LIMIT 5"
    ).fetchall()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "opening_balance": opening_balance,
            "as_of_date": as_of_date,
            "active_count": active_count,
            "voided_count": voided_count,
            "total_income": total_income,
            "total_expense": total_expense,
            "recent": recent,
        },
    )

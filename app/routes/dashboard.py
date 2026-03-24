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
    company_id: str | None = None,
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
    companies = db.execute(
        "SELECT id, name, slug FROM companies WHERE is_active = TRUE ORDER BY id"
    ).fetchall()
    selected_company_id = int(company_id) if company_id and company_id.isdigit() else None
    company_filter = ""
    company_params: list[int] = []
    if selected_company_id is not None:
        company_filter = " AND company_id = ?"
        company_params = [selected_company_id]

    # Transaction counts
    active_count = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE is_active = 1" + company_filter,
        company_params,
    ).fetchone()[0]
    voided_count = db.execute(
        "SELECT COUNT(*) FROM transactions WHERE is_active = 0" + company_filter,
        company_params,
    ).fetchone()[0]

    # Totals (active only)
    total_cash_in = db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions "
        "WHERE is_active = 1 AND direction = 'cash_in'" + company_filter,
        company_params,
    ).fetchone()[0]
    total_cash_out = db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions "
        "WHERE is_active = 1 AND direction = 'cash_out'" + company_filter,
        company_params,
    ).fetchone()[0]

    # Recent 5 active transactions with category label
    recent = db.execute(
        "SELECT t.id, t.date, t.amount, t.direction, c.label AS category_label, "
        "c.name AS category_name, co.name AS company_name, t.payment_method "
        "FROM transactions t "
        "JOIN categories c ON t.category_id = c.category_id "
        "LEFT JOIN companies co ON t.company_id = co.id "
        "WHERE t.is_active = 1" + company_filter + " ORDER BY t.created_at DESC LIMIT 5",
        company_params,
    ).fetchall()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "opening_balance": opening_balance,
            "as_of_date": as_of_date,
            "active_count": active_count,
            "voided_count": voided_count,
            "total_cash_in": total_cash_in,
            "total_cash_out": total_cash_out,
            "recent": recent,
            "companies": companies,
            "selected_company_id": selected_company_id,
        },
    )

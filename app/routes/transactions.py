import sqlite3
from datetime import date
from decimal import Decimal
from typing import Generator

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.i18n import translate_error
from app.services.auth_service import require_auth
from app.services.calculations import effective_cost, vat_amount
from app.services.transaction_service import get_transaction, void_transaction
from app.services.validation import validate_transaction

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _get_db() -> Generator[sqlite3.Connection, None, None]:
    """Lazy wrapper around app.main.get_db to avoid circular import at module load."""
    from app.main import get_db

    yield from get_db()


def _normalize_for_accountant_flag(data: dict) -> str:
    if data["direction"] == "cash_in" and data["cash_in_type"] == "internal":
        return ""
    return data["for_accountant"]


@router.get("/transactions/new", response_class=HTMLResponse)
async def get_create_transaction(
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    user = require_auth(request)  # noqa: F841
    cats = db.execute(
        "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
        "FROM categories ORDER BY direction, label"
    ).fetchall()
    companies = db.execute(
        "SELECT id, name, slug FROM companies WHERE is_active = TRUE ORDER BY id"
    ).fetchall()
    return templates.TemplateResponse(
        request,
        "transactions/create.html",
        {
            "categories": cats,
            "companies": companies,
            "errors": [],
            "form_data": {},
            "today": str(date.today()),
        },
    )


@router.post("/transactions/new")
async def post_create_transaction(
    request: Request,
    date_field: str = Form(default="", alias="date"),
    direction: str = Form(default=""),
    amount: str = Form(default=""),
    category_id: str = Form(default=""),
    company_id: str = Form(default=""),
    payment_method: str = Form(default=""),
    vat_rate: str = Form(default=""),
    cash_in_type: str = Form(default=""),
    vat_deductible_pct: str = Form(default=""),
    description: str = Form(default=""),
    for_accountant: str = Form(default=""),
    db: sqlite3.Connection = Depends(_get_db),
):
    user = require_auth(request)

    # Normalise: strip whitespace; empty string → None for optional fields
    def _s(v: str) -> str:
        return v.strip()

    def _opt(v: str):
        v = v.strip()
        return v if v else None

    data = {
        "date": _s(date_field),
        "direction": _s(direction),
        "amount": _s(amount),
        "category_id": _s(category_id),
        "company_id": _s(company_id),
        "payment_method": _s(payment_method),
        "vat_rate": _s(vat_rate),
        "cash_in_type": _opt(cash_in_type),
        "vat_deductible_pct": _opt(vat_deductible_pct),
        "description": _opt(description),
        "for_accountant": "1" if _s(for_accountant) else "",
        "logged_by": user["id"],
        "is_active": True,
    }
    data["for_accountant"] = _normalize_for_accountant_flag(data)

    errors = validate_transaction(data, db)

    if errors:
        locale = request.state.locale
        errors = [translate_error(e, locale) for e in errors]
        cats = db.execute(
            "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
            "FROM categories ORDER BY direction, label"
        ).fetchall()
        companies = db.execute(
            "SELECT id, name, slug FROM companies WHERE is_active = TRUE ORDER BY id"
        ).fetchall()
        return templates.TemplateResponse(
            request,
            "transactions/create.html",
            {
                "categories": cats,
                "companies": companies,
                "errors": errors,
                "form_data": data,
                "today": str(date.today()),
            },
            status_code=422,
        )

    # Cast safely after validation passed
    gross = Decimal(str(data["amount"]))
    vat_rate_val = float(data["vat_rate"])
    vat_deductible_val = (
        float(data["vat_deductible_pct"])
        if data["vat_deductible_pct"] is not None
        else None
    )
    cat_id = int(data["category_id"])
    comp_id = int(data["company_id"])

    db.execute(
        "INSERT INTO transactions "
        "(date, amount, direction, category_id, company_id, payment_method, "
        "vat_rate, cash_in_type, vat_deductible_pct, description, for_accountant, logged_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            str(gross),
            data["direction"],
            cat_id,
            comp_id,
            data["payment_method"],
            vat_rate_val,
            data["cash_in_type"],
            vat_deductible_val,
            data["description"],
            1 if data["for_accountant"] else 0,
            data["logged_by"],
        ),
    )
    db.commit()
    request.session["flash"] = {
        "type": "success",
        "message": "flash_transaction_saved",
    }
    return RedirectResponse(url="/transactions/", status_code=302)


@router.get("/transactions/", response_class=HTMLResponse)
async def get_transaction_list(
    request: Request,
    show_all: bool = False,
    company_id: str | None = None,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    user = require_auth(request)  # noqa: F841
    companies = db.execute(
        "SELECT id, name, slug FROM companies WHERE is_active = TRUE ORDER BY id"
    ).fetchall()
    selected_company_id = int(company_id) if company_id and company_id.isdigit() else None
    conditions = []
    params: list[int] = []
    if not show_all:
        conditions.append("t.is_active = TRUE")
    if selected_company_id is not None:
        conditions.append("t.company_id = ?")
        params.append(selected_company_id)
    where = f"WHERE {' AND '.join(conditions)} " if conditions else ""
    rows = db.execute(
        "SELECT t.*, c.label AS category_label, c.name AS category_name, "
        "co.name AS company_name, "
        "u.username AS logged_by_username, "
        "vb.username AS voided_by_username "
        "FROM transactions t "
        "JOIN categories c ON t.category_id = c.category_id "
        "LEFT JOIN companies co ON t.company_id = co.id "
        "JOIN users u ON t.logged_by = u.id "
        "LEFT JOIN users vb ON t.voided_by = vb.id "
        f"{where}"
        "ORDER BY t.created_at DESC "
        "LIMIT 100",
        params,
    ).fetchall()

    transactions = []
    for row in rows:
        gross = Decimal(str(row["amount"]))
        va = vat_amount(gross, row["vat_rate"])
        ec = (
            effective_cost(gross, row["vat_rate"], row["vat_deductible_pct"])
            if row["direction"] == "cash_out"
            else None
        )
        t = dict(row)
        t["va"] = va
        t["ec"] = ec
        transactions.append(t)

    return templates.TemplateResponse(
        request,
        "transactions/list.html",
        {
            "transactions": transactions,
            "show_all": show_all,
            "companies": companies,
            "selected_company_id": selected_company_id,
        },
    )


@router.get("/transactions/{transaction_id}", response_class=HTMLResponse)
async def get_transaction_detail(
    transaction_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    require_auth(request)
    txn = get_transaction(transaction_id, db)
    if txn is None:
        raise HTTPException(status_code=404)
    # Check if this transaction is a correction of another
    original = db.execute(
        "SELECT id FROM transactions WHERE replacement_transaction_id = ? AND is_active = 0",
        (transaction_id,),
    ).fetchone()
    original_id = original["id"] if original else None
    return templates.TemplateResponse(
        request, "transactions/detail.html", {"txn": txn, "original_id": original_id}
    )


@router.get("/transactions/{transaction_id}/void", response_class=HTMLResponse)
async def get_void_transaction(
    transaction_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    require_auth(request)
    txn = get_transaction(transaction_id, db)
    if txn is None or not txn["is_active"]:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "transactions/void.html",
        {"txn": txn, "errors": [], "form_data": {}},
    )


@router.post("/transactions/{transaction_id}/void")
async def post_void_transaction(
    transaction_id: int,
    request: Request,
    void_reason: str = Form(default=""),
    db: sqlite3.Connection = Depends(_get_db),
):
    user = require_auth(request)
    txn = get_transaction(transaction_id, db)
    if txn is None:
        raise HTTPException(status_code=404)
    try:
        void_transaction(transaction_id, void_reason, user["id"], db)
    except ValueError as e:
        locale = request.state.locale
        return templates.TemplateResponse(
            request,
            "transactions/void.html",
            {
                "txn": txn,
                "errors": [translate_error(str(e), locale)],
                "form_data": {"void_reason": void_reason},
            },
            status_code=422,
        )
    db.commit()
    request.session["flash"] = {"type": "success", "message": "flash_transaction_voided"}
    return RedirectResponse(url="/transactions/", status_code=302)


@router.get("/transactions/{transaction_id}/correct", response_class=HTMLResponse)
async def get_correct_transaction(
    transaction_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    require_auth(request)
    txn = get_transaction(transaction_id, db)
    if txn is None or not txn["is_active"]:
        raise HTTPException(status_code=404)
    cats = db.execute(
        "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
        "FROM categories ORDER BY direction, label"
    ).fetchall()
    companies = db.execute(
        "SELECT id, name, slug FROM companies WHERE is_active = TRUE ORDER BY id"
    ).fetchall()
    form_data = {
        "date": txn["date"],
        "direction": txn["direction"],
        "amount": txn["amount"],
        "category_id": str(txn["category_id"]),
        "company_id": str(txn["company_id"]),
        "payment_method": txn["payment_method"],
        "vat_rate": str(int(txn["vat_rate"])),
        "cash_in_type": txn["cash_in_type"] or "",
        "vat_deductible_pct": str(int(txn["vat_deductible_pct"])) if txn["vat_deductible_pct"] is not None else "",
        "description": txn["description"] or "",
        "for_accountant": "1" if txn["for_accountant"] else "",
        "correction_reason": "",
    }
    return templates.TemplateResponse(
        request,
        "transactions/create.html",
        {
            "categories": cats,
            "companies": companies,
            "errors": [],
            "form_data": form_data,
            "today": str(date.today()),
            "form_action": f"/transactions/{transaction_id}/correct",
            "is_correction": True,
        },
    )


@router.post("/transactions/{transaction_id}/correct")
async def post_correct_transaction(
    transaction_id: int,
    request: Request,
    date_field: str = Form(default="", alias="date"),
    direction: str = Form(default=""),
    amount: str = Form(default=""),
    category_id: str = Form(default=""),
    company_id: str = Form(default=""),
    payment_method: str = Form(default=""),
    vat_rate: str = Form(default=""),
    cash_in_type: str = Form(default=""),
    vat_deductible_pct: str = Form(default=""),
    description: str = Form(default=""),
    for_accountant: str = Form(default=""),
    correction_reason: str = Form(default=""),
    db: sqlite3.Connection = Depends(_get_db),
):
    user = require_auth(request)
    txn = get_transaction(transaction_id, db)
    if txn is None or not txn["is_active"]:
        raise HTTPException(status_code=404)

    def _s(v: str) -> str:
        return v.strip()

    def _opt(v: str):
        v = v.strip()
        return v if v else None

    data = {
        "date": _s(date_field),
        "direction": _s(direction),
        "amount": _s(amount),
        "category_id": _s(category_id),
        "company_id": _s(company_id),
        "payment_method": _s(payment_method),
        "vat_rate": _s(vat_rate),
        "cash_in_type": _opt(cash_in_type),
        "vat_deductible_pct": _opt(vat_deductible_pct),
        "description": _opt(description),
        "for_accountant": "1" if _s(for_accountant) else "",
        "logged_by": user["id"],
        "is_active": True,
        "correction_reason": _s(correction_reason),
    }
    data["for_accountant"] = _normalize_for_accountant_flag(data)

    errors = validate_transaction(data, db)

    # Validate correction reason (route-level, not in validation.py)
    if not data["correction_reason"]:
        errors.append("Correction reason is required.")

    if errors:
        locale = request.state.locale
        errors = [translate_error(e, locale) for e in errors]
        cats = db.execute(
            "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
            "FROM categories ORDER BY direction, label"
        ).fetchall()
        companies = db.execute(
            "SELECT id, name, slug FROM companies WHERE is_active = TRUE ORDER BY id"
        ).fetchall()
        return templates.TemplateResponse(
            request,
            "transactions/create.html",
            {
                "categories": cats,
                "companies": companies,
                "errors": errors,
                "form_data": data,
                "today": str(date.today()),
                "form_action": f"/transactions/{transaction_id}/correct",
                "is_correction": True,
            },
            status_code=422,
        )

    gross = Decimal(str(data["amount"]))
    vat_rate_val = float(data["vat_rate"])
    vat_deductible_val = (
        float(data["vat_deductible_pct"])
        if data["vat_deductible_pct"] is not None
        else None
    )
    cat_id = int(data["category_id"])
    comp_id = int(data["company_id"])

    db.execute(
        "INSERT INTO transactions "
        "(date, amount, direction, category_id, company_id, payment_method, "
        "vat_rate, cash_in_type, vat_deductible_pct, description, for_accountant, logged_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            str(gross),
            data["direction"],
            cat_id,
            comp_id,
            data["payment_method"],
            vat_rate_val,
            data["cash_in_type"],
            vat_deductible_val,
            data["description"],
            1 if data["for_accountant"] else 0,
            data["logged_by"],
        ),
    )
    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute(
        "UPDATE transactions "
        "SET is_active = 0, void_reason = ?, voided_by = ?, "
        "voided_at = CURRENT_TIMESTAMP, replacement_transaction_id = ? "
        "WHERE id = ?",
        (data["correction_reason"], user["id"], new_id, transaction_id),
    )
    db.commit()
    request.session["flash"] = {
        "type": "success",
        "message": "flash_transaction_corrected",
    }
    return RedirectResponse(url="/transactions/", status_code=302)


@router.get("/categories")
async def get_categories(
    request: Request,  # noqa: ARG001
    db: sqlite3.Connection = Depends(_get_db),
):
    # AuthGate already protects this route — no special auth handling needed here
    rows = db.execute(
        "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
        "FROM categories ORDER BY direction, label"
    ).fetchall()
    return JSONResponse(
        [
            {
                "category_id": row["category_id"],
                "name": row["name"],
                "label": row["label"],
                "direction": row["direction"],
                "default_vat_rate": row["default_vat_rate"],
                "default_vat_deductible_pct": row["default_vat_deductible_pct"],
            }
            for row in rows
        ]
    )

import sqlite3
from datetime import date
from decimal import Decimal
from typing import Generator

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

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
    return templates.TemplateResponse(
        request,
        "transactions/create.html",
        {
            "categories": cats,
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
    payment_method: str = Form(default=""),
    vat_rate: str = Form(default=""),
    income_type: str = Form(default=""),
    vat_deductible_pct: str = Form(default=""),
    description: str = Form(default=""),
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
        "payment_method": _s(payment_method),
        "vat_rate": _s(vat_rate),
        "income_type": _opt(income_type),
        "vat_deductible_pct": _opt(vat_deductible_pct),
        "description": _opt(description),
        "logged_by": user["id"],
        "is_active": True,
    }

    errors = validate_transaction(data, db)

    if errors:
        cats = db.execute(
            "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
            "FROM categories ORDER BY direction, label"
        ).fetchall()
        return templates.TemplateResponse(
            request,
            "transactions/create.html",
            {
                "categories": cats,
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

    db.execute(
        "INSERT INTO transactions "
        "(date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, vat_deductible_pct, description, logged_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            str(gross),
            data["direction"],
            cat_id,
            data["payment_method"],
            vat_rate_val,
            data["income_type"],
            vat_deductible_val,
            data["description"],
            data["logged_by"],
        ),
    )
    db.commit()
    request.session["flash"] = {
        "type": "success",
        "message": "Transaction saved successfully.",
    }
    return RedirectResponse(url="/transactions/", status_code=302)


@router.get("/transactions/", response_class=HTMLResponse)
async def get_transaction_list(
    request: Request,
    show_all: bool = False,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    user = require_auth(request)  # noqa: F841
    where = "" if show_all else "WHERE t.is_active = TRUE "
    rows = db.execute(
        "SELECT t.*, c.label AS category_label, u.username AS logged_by_username, "
        "vb.username AS voided_by_username "
        "FROM transactions t "
        "JOIN categories c ON t.category_id = c.category_id "
        "JOIN users u ON t.logged_by = u.id "
        "LEFT JOIN users vb ON t.voided_by = vb.id "
        f"{where}"
        "ORDER BY t.created_at DESC "
        "LIMIT 100"
    ).fetchall()

    transactions = []
    for row in rows:
        gross = Decimal(str(row["amount"]))
        va = vat_amount(gross, row["vat_rate"])
        ec = (
            effective_cost(gross, row["vat_rate"], row["vat_deductible_pct"])
            if row["direction"] == "expense"
            else None
        )
        t = dict(row)
        t["va"] = va
        t["ec"] = ec
        transactions.append(t)

    return templates.TemplateResponse(
        request,
        "transactions/list.html",
        {"transactions": transactions, "show_all": show_all},
    )


@router.get("/transactions/{transaction_id}", response_class=HTMLResponse)
async def get_transaction_detail(
    transaction_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    require_auth(request)
    t = get_transaction(transaction_id, db)
    if t is None:
        raise HTTPException(status_code=404)
    # Check if this transaction is a correction of another
    original = db.execute(
        "SELECT id FROM transactions WHERE replacement_transaction_id = ? AND is_active = 0",
        (transaction_id,),
    ).fetchone()
    original_id = original["id"] if original else None
    return templates.TemplateResponse(
        request, "transactions/detail.html", {"t": t, "original_id": original_id}
    )


@router.get("/transactions/{transaction_id}/void", response_class=HTMLResponse)
async def get_void_transaction(
    transaction_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    require_auth(request)
    t = get_transaction(transaction_id, db)
    if t is None or not t["is_active"]:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "transactions/void.html",
        {"t": t, "errors": [], "form_data": {}},
    )


@router.post("/transactions/{transaction_id}/void")
async def post_void_transaction(
    transaction_id: int,
    request: Request,
    void_reason: str = Form(default=""),
    db: sqlite3.Connection = Depends(_get_db),
):
    user = require_auth(request)
    t = get_transaction(transaction_id, db)
    if t is None:
        raise HTTPException(status_code=404)
    try:
        void_transaction(transaction_id, void_reason, user["id"], db)
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "transactions/void.html",
            {"t": t, "errors": [str(e)], "form_data": {"void_reason": void_reason}},
            status_code=422,
        )
    db.commit()
    request.session["flash"] = {"type": "success", "message": "Transaction voided."}
    return RedirectResponse(url="/transactions/", status_code=302)


@router.get("/transactions/{transaction_id}/correct", response_class=HTMLResponse)
async def get_correct_transaction(
    transaction_id: int,
    request: Request,
    db: sqlite3.Connection = Depends(_get_db),
) -> HTMLResponse:
    require_auth(request)
    t = get_transaction(transaction_id, db)
    if t is None or not t["is_active"]:
        raise HTTPException(status_code=404)
    cats = db.execute(
        "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
        "FROM categories ORDER BY direction, label"
    ).fetchall()
    form_data = {
        "date": t["date"],
        "direction": t["direction"],
        "amount": t["amount"],
        "category_id": str(t["category_id"]),
        "payment_method": t["payment_method"],
        "vat_rate": str(int(t["vat_rate"])),
        "income_type": t["income_type"] or "",
        "vat_deductible_pct": str(int(t["vat_deductible_pct"])) if t["vat_deductible_pct"] is not None else "",
        "description": t["description"] or "",
    }
    return templates.TemplateResponse(
        request,
        "transactions/create.html",
        {
            "categories": cats,
            "errors": [],
            "form_data": form_data,
            "today": str(date.today()),
            "form_action": f"/transactions/{transaction_id}/correct",
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
    payment_method: str = Form(default=""),
    vat_rate: str = Form(default=""),
    income_type: str = Form(default=""),
    vat_deductible_pct: str = Form(default=""),
    description: str = Form(default=""),
    db: sqlite3.Connection = Depends(_get_db),
):
    user = require_auth(request)
    t = get_transaction(transaction_id, db)
    if t is None or not t["is_active"]:
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
        "payment_method": _s(payment_method),
        "vat_rate": _s(vat_rate),
        "income_type": _opt(income_type),
        "vat_deductible_pct": _opt(vat_deductible_pct),
        "description": _opt(description),
        "logged_by": user["id"],
        "is_active": True,
    }

    errors = validate_transaction(data, db)

    if errors:
        cats = db.execute(
            "SELECT category_id, name, label, direction, default_vat_rate, default_vat_deductible_pct "
            "FROM categories ORDER BY direction, label"
        ).fetchall()
        return templates.TemplateResponse(
            request,
            "transactions/create.html",
            {
                "categories": cats,
                "errors": errors,
                "form_data": data,
                "today": str(date.today()),
                "form_action": f"/transactions/{transaction_id}/correct",
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

    db.execute(
        "INSERT INTO transactions "
        "(date, amount, direction, category_id, payment_method, "
        "vat_rate, income_type, vat_deductible_pct, description, logged_by) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            data["date"],
            str(gross),
            data["direction"],
            cat_id,
            data["payment_method"],
            vat_rate_val,
            data["income_type"],
            vat_deductible_val,
            data["description"],
            data["logged_by"],
        ),
    )
    new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute(
        "UPDATE transactions "
        "SET is_active = 0, void_reason = 'Corrected', voided_by = ?, replacement_transaction_id = ? "
        "WHERE id = ?",
        (user["id"], new_id, transaction_id),
    )
    db.commit()
    request.session["flash"] = {
        "type": "success",
        "message": "Transaction corrected. Original has been voided.",
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

import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.main import get_db
from app.services.auth_service import get_current_user, get_user_by_username, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/auth/login", response_class=HTMLResponse)
async def get_login(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> HTMLResponse:
    """Render login form. Redirect to / if already authenticated."""
    user = get_current_user(request, db)
    if user is not None:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html", {"error": None})


@router.post("/auth/login")
async def post_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """Validate credentials, create session, redirect to /."""

    def render_error(msg: str) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": msg, "username": username},
            status_code=401,
        )

    # Step 1 — empty field check (exact error message required)
    if not username or not password:
        return render_error("Username and password are required")

    # Step 2 — user lookup
    user = get_user_by_username(db, username)
    if user is None:
        return render_error("Invalid credentials")

    # Step 3 — password check
    if not verify_password(password, user["password_hash"]):
        return render_error("Invalid credentials")

    # Step 4 — session fixation prevention: clear before setting
    request.session.clear()
    request.session["user_id"] = user["id"]  # integer, never username string

    return RedirectResponse(url="/", status_code=302)


@router.post("/auth/logout")
async def post_logout(request: Request):
    """Clear session and redirect to login. Must be POST — GET logout is a security issue."""
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)

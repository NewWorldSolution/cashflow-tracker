from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request) -> HTMLResponse:
    """Placeholder dashboard — confirms authenticated access.

    AuthGate middleware guarantees request.state.user is set before this
    handler is called. No DB queries needed for this placeholder.
    Full dashboard content is out of scope for P1-I2.
    """
    return templates.TemplateResponse(request, "dashboard.html", {})

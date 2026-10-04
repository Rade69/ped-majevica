from pathlib import Path
from flask import Blueprint, send_from_directory
from flask_login import current_user, login_required
from app.utils.responses import error_response

admin_bp = Blueprint("admin", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_PAGES = BASE_DIR.parent / "frontend" / "pages"


@admin_bp.get("/admin/dashboard")
@login_required  # neprijavljen korisnik se preusmjerava na prijavu (stranica, ne API)
def admin_page():
    if current_user.role not in ("admin", "editor"):
        return error_response("Nemate dozvolu za ovu operaciju.", status_code=403)
    return send_from_directory(FRONTEND_PAGES, "admin.html")

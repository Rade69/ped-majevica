from pathlib import Path
from flask import Blueprint, send_from_directory
from flask_login import login_required

admin_bp = Blueprint("admin", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_PAGES = BASE_DIR.parent / "frontend" / "pages"


@admin_bp.get("/admin/dashboard")
@login_required
def admin_page():
    return send_from_directory(FRONTEND_PAGES, "admin.html")

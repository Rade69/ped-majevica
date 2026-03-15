from flask import Blueprint, send_from_directory
from pathlib import Path

frontend_bp = Blueprint("frontend", __name__)

# root projekta (ped-majevica)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

FRONTEND_DIR = PROJECT_ROOT / "frontend"
PAGES_DIR = FRONTEND_DIR / "pages"
ASSETS_DIR = FRONTEND_DIR / "assets"
JS_DIR = FRONTEND_DIR / "js"


# ======================
# JAVNE STRANICE
# ======================


@frontend_bp.route("/")
def index():
    return send_from_directory(PAGES_DIR, "index.html")


@frontend_bp.route("/login")
@frontend_bp.route("/login.html")
def login():
    return send_from_directory(PAGES_DIR, "login.html")


# ======================
# ADMIN HTML (BEZ AUTH)
# ⚠️ NEMA /admin !
# ======================


@frontend_bp.route("/admin.html")
def admin_html():
    return send_from_directory(PAGES_DIR, "admin.html")


@frontend_bp.route("/admin")
def admin_redirect():
    from flask import redirect, url_for

    return redirect(url_for("frontend.admin_html"))


@frontend_bp.route("/galerija")
@frontend_bp.route("/galerija.html")
def galerija():
    return send_from_directory(PAGES_DIR, "galerija.html")


# ======================
# STATIC FILES
# ======================


@frontend_bp.route("/assets/<path:path>")
def assets(path):
    return send_from_directory(ASSETS_DIR, path)


@frontend_bp.route("/js/<path:path>")
def js(path):
    return send_from_directory(JS_DIR, path)


@frontend_bp.route("/uclanite-se")
@frontend_bp.route("/uclanite-se.html")
def uclanite_se():
    return send_from_directory(PAGES_DIR, "uclanite-se.html")

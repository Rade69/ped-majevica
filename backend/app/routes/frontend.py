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
# ADMIN STRANICA
# Samo za prijavljene admine/urednike; ostali idu na prijavu.
# ======================


def _admin_shell():
    from flask import redirect
    from flask_login import current_user

    if not current_user.is_authenticated or current_user.role not in ("admin", "editor"):
        return redirect("/login")
    return send_from_directory(PAGES_DIR, "admin.html")


@frontend_bp.route("/admin.html")
def admin_html():
    return _admin_shell()


@frontend_bp.route("/admin")
def admin_redirect():
    from flask import redirect

    if not _admin_allowed():
        return redirect("/login")
    return redirect("/admin.html")


def _admin_allowed():
    from flask_login import current_user

    return current_user.is_authenticated and current_user.role in ("admin", "editor")


@frontend_bp.route("/galerija")
@frontend_bp.route("/galerija.html")
def galerija():
    return send_from_directory(PAGES_DIR, "galerija.html")


# ======================
# STATIC FILES
# ======================


@frontend_bp.route("/robots.txt")
def robots():
    return send_from_directory(FRONTEND_DIR, "robots.txt", mimetype="text/plain")


@frontend_bp.route("/sitemap.xml")
def sitemap():
    return send_from_directory(FRONTEND_DIR, "sitemap.xml", mimetype="application/xml")


@frontend_bp.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(FRONTEND_DIR, "manifest.webmanifest", mimetype="application/manifest+json")


@frontend_bp.route("/favicon.png")
@frontend_bp.route("/favicon.ico")
def favicon():
    return send_from_directory(FRONTEND_DIR, "favicon.png", mimetype="image/png")


@frontend_bp.route("/assets/<path:path>")
def assets(path):
    return send_from_directory(ASSETS_DIR, path)


@frontend_bp.route("/js/<path:path>")
def js(path):
    return send_from_directory(JS_DIR, path)


@frontend_bp.route("/privatnost")
@frontend_bp.route("/privatnost.html")
def privatnost():
    return send_from_directory(PAGES_DIR, "privatnost.html")


@frontend_bp.route("/uslovi")
@frontend_bp.route("/uslovi.html")
def uslovi():
    return send_from_directory(PAGES_DIR, "uslovi.html")


@frontend_bp.route("/uclanite-se")
@frontend_bp.route("/uclanite-se.html")
def uclanite_se():
    return send_from_directory(PAGES_DIR, "uclanite-se.html")

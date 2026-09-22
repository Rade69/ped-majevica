# backend/app/routes/errors.py
from flask import Blueprint
from app.utils.responses import error_response

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(400)
def bad_request(error):
    return error_response("Neispravan zahtev", status_code=400)


@errors_bp.app_errorhandler(404)
def not_found(error):
    return error_response("Resurs nije pronađen", status_code=404)


@errors_bp.app_errorhandler(405)
def method_not_allowed(error):
    return error_response("Metod nije dozvoljen", status_code=405)


@errors_bp.app_errorhandler(500)
def server_error(error):
    return error_response("Interna greška servera", status_code=500)

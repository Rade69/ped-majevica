# backend/app/routes/errors.py
from flask import Blueprint, jsonify

errors_bp = Blueprint("errors", __name__)


@errors_bp.app_errorhandler(404)
def not_found(error):
    # API greške vraćamo kao JSON
    return jsonify({"error": "Page not found"}), 404


@errors_bp.app_errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

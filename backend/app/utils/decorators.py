# backend/app/utils/decorators.py
"""
Role-Based Access Control (RBAC) decorators
"""
from functools import wraps
from flask import jsonify
from flask_login import current_user
from app.utils.responses import error_response
import logging

logger = logging.getLogger(__name__)


def role_required(*allowed_roles):
    """
    Decorator that restricts access to users with specific roles.

    Usage:
        @role_required('admin')
        @role_required('admin', 'editor')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Provera da li je korisnik autentifikovan
            if not current_user.is_authenticated:
                logger.warning(
                    f"🔒 ACCESS DENIED: User not authenticated for {f.__name__}"
                )
                return error_response(
                    "Morate biti prijavljeni da pristupite ovom resursu.",
                    status_code=401,
                )

            # Provera da li je korisnik aktivan
            if not current_user.is_active:
                logger.warning(
                    f"🔒 ACCESS DENIED: User {current_user.username} is inactive"
                )
                return error_response(
                    "Vaš nalog je deaktiviran. Kontaktirajte administratora.",
                    status_code=403,
                )

            # Provera role
            if current_user.role not in allowed_roles:
                logger.warning(
                    f"🔒 ACCESS DENIED: User {current_user.username} with role "
                    f"'{current_user.role}' tried to access {f.__name__} "
                    f"(allowed: {allowed_roles})"
                )
                return error_response(
                    "Nemate dozvolu za ovu operaciju.", status_code=403
                )

            logger.info(
                f"✅ ACCESS GRANTED: {current_user.username} ({current_user.role}) -> {f.__name__}"
            )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    """
    Decorator that restricts access to admin users only.

    Usage:
        @admin_required
        def my_function():
            ...
    """
    return role_required("admin")(f)


def editor_required(f):
    """
    Decorator that restricts access to editors and admins.

    Usage:
        @editor_required
        def my_function():
            ...
    """
    return role_required("admin", "editor")(f)


def json_required(f):
    """
    Decorator that ensures request contains JSON data.

    Usage:
        @json_required
        def my_function():
            ...
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request

        if not request.is_json:
            return error_response(
                "Content-Type must be application/json", status_code=400
            )
        return f(*args, **kwargs)

    return decorated_function

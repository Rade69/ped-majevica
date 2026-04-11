"""
CSRF Protection utilities for Flask
"""

from flask import session, request, jsonify
from functools import wraps
import secrets
import logging

logger = logging.getLogger(__name__)

# Secret key for CSRF tokens (should be set in config)
CSRF_TOKEN_LENGTH = 32


def generate_csrf_token():
    """Generate a new CSRF token"""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(CSRF_TOKEN_LENGTH)
    return session["csrf_token"]


def get_csrf_token():
    """Get current CSRF token from session"""
    return session.get("csrf_token")


def validate_csrf_token(token):
    """Validate a CSRF token against session token"""
    if not token:
        return False

    session_token = session.get("csrf_token")
    if not session_token:
        return False

    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(token, session_token)


def rotate_csrf_token():
    """Generate a new CSRF token and replace the old one"""
    new_token = secrets.token_hex(CSRF_TOKEN_LENGTH)
    session["csrf_token"] = new_token
    logger.debug("CSRF token rotated")
    return new_token


def csrf_required(f):
    """
    Decorator to require valid CSRF token for POST/PUT/DELETE requests
    Use for API endpoints that modify data
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF check for GET requests
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return f(*args, **kwargs)

        # Get token from header or form
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            # Also check form data
            csrf_token = request.form.get("csrf_token")

        # Validate token
        if not validate_csrf_token(csrf_token):
            logger.warning(
                f"CSRF validation failed for {request.method} {request.path}"
            )
            return (
                jsonify(
                    {
                        "error": "CSRF token missing or invalid",
                        "message": "Molimo osvežite stranicu i pokušajte ponovo",
                    }
                ),
                403,
            )
        
        # Rotate token after successful validation (prevents token reuse)
        rotate_csrf_token()

        return f(*args, **kwargs)

    return decorated_function


def csrf_protected(f):
    """
    Decorator that adds CSRF token to response headers
    Use for GET requests that will be followed by POST
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)

        # Add CSRF token to response headers
        if hasattr(response, "headers"):
            response.headers["X-CSRF-Token"] = get_csrf_token()

        return response

    return decorated_function


def init_csrf(app):
    """
    Initialize CSRF protection for Flask app
    Call this in your application factory
    """

    # Generate token for each request
    @app.before_request
    def csrf_protect():
        # Skip for static files and certain paths
        if request.path.startswith("/static"):
            return

        # Generate token if not exists
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(CSRF_TOKEN_LENGTH)

    # Make token available in templates
    @app.context_processor
    def csrf_token_context():
        return dict(csrf_token=get_csrf_token())

    logger.info("✅ CSRF protection initialized")

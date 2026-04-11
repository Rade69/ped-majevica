# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify, redirect, make_response, session
from flask_login import login_user, logout_user, current_user, login_required
from app.services.user_service import get_user_by_username
from app.services.password_reset_service import (
    request_password_reset,
    reset_password_with_token,
    change_password as change_password_service
)
from app.extensions import db, bcrypt, limiter
from app.models.user import User
from app.utils.responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


# --------------------
# API LOGIN
# --------------------
@auth_bp.post("/api/login")
@limiter.limit("5 per minute")  # Maksimalno 5 pokušaja u minutu
@limiter.limit("20 per hour")  # Maksimalno 20 pokušaja u satu
def api_login():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    logger.info(f"🔐 LOGIN ATTEMPT: username={username}")

    # Validacija inputa
    if not username or not password:
        logger.warning(f"❌ LOGIN FAILED: Missing username or password")
        return error_response("Korisničko ime i lozinka su obavezni", status_code=400)

    user = get_user_by_username(username)

    # Provera da li korisnik postoji
    if not user:
        logger.warning(f"❌ LOGIN FAILED: User not found: {username}")
        return error_response("Neispravno korisničko ime ili lozinka", status_code=401)

    # Provera da li je korisnik aktivan
    if not user.is_active:
        logger.warning(f"❌ LOGIN FAILED: User inactive: {username}")
        return error_response(
            "Nalog je deaktiviran. Kontaktirajte administratora.", status_code=403
        )

    if bcrypt.check_password_hash(user.password_hash, password):
        logger.info(
            f"✅ LOGIN SUCCESS: user_id={user.id}, username={username}, role={user.role}"
        )

        # Ažuriraj last_login timestamp
        user.update_last_login()
        db.session.commit()

        # CRITICAL: Explicitly set session data to force Flask to send Set-Cookie header
        session["user_id"] = user.id
        session["username"] = username
        session["role"] = user.role
        session.permanent = True  # Make session persistent

        # Login user with Flask-Login (this also sets session)
        login_user(user, remember=True)

        # Create response - vraćamo i rolu korisnika
        response = make_response(
            success_response(
                data={
                    "username": username,
                    "role": user.role,
                    "is_admin": user.is_admin(),
                    "is_editor": user.is_editor(),
                },
                message="Prijava uspešna",
            )
        )

        logger.info(
            f"🍪 Session data set: user_id={user.id}, username={username}, role={user.role}"
        )
        logger.info(f"🍪 Session keys: {list(session.keys())}")
        logger.info(
            f"🍪 Flask should now send Set-Cookie header with SameSite=None; Secure"
        )

        return response

    logger.warning(f"❌ LOGIN FAILED: Invalid credentials for {username}")
    return error_response("Neispravno korisničko ime ili lozinka", status_code=401)


# --------------------
# LOGOUT
# --------------------
@auth_bp.get("/logout")
def logout():
    logout_user()
    # Redirect to Netlify login page (frontend)
    return redirect("https://pedmajevica.org/pages/login.html")


# --------------------
# PASSWORD RESET - REQUEST
# --------------------
@auth_bp.post("/api/password-reset-request")
@limiter.limit("3 per hour")  # Maksimalno 3 zahteva po satu
def password_reset_request():
    """
    Request password reset - sends email with reset link
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return error_response("Email adresa je obavezna", status_code=400)

    # Use password reset service
    result = request_password_reset(email)
    
    if result["success"]:
        return success_response(message=result["message"])
    else:
        return error_response(result["error"], status_code=result.get("status_code", 400))


# --------------------
# PASSWORD RESET - CONFIRM
# --------------------
@auth_bp.post("/api/password-reset-confirm")
@limiter.limit("5 per hour")  # Maksimalno 5 pokušaja po satu
def password_reset_confirm():
    """
    Confirm password reset - set new password using secure token
    """
    data = request.get_json(silent=True) or {}

    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    # Validacija
    if not token or not new_password:
        return error_response("Token i nova lozinka su obavezni", status_code=400)
    
    # Confirm password validation (frontend should do this, but we double-check)
    if confirm_password and new_password != confirm_password:
        return error_response("Lozinke se ne poklapaju", status_code=400)

    if len(new_password) < 8:
        return error_response(
            "Lozinka mora imati najmanje 8 karaktera", status_code=400
        )

    # Use password reset service with secure token validation
    result = reset_password_with_token(token, new_password)
    
    if result["success"]:
        return success_response(message=result["message"])
    else:
        return error_response(result["error"], status_code=result.get("status_code", 400))


# --------------------
# CHANGE PASSWORD (AUTHENTICATED)
# --------------------
@auth_bp.post("/api/change-password")
@limiter.limit("5 per hour")
@login_required
def change_password():
    """
    Change password for authenticated user
    """
    data = request.get_json(silent=True) or {}

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    # Validacija
    if not current_password or not new_password:
        return error_response("Trenutna i nova lozinka su obavezne", status_code=400)
    
    # Confirm password validation (frontend should do this, but we double-check)
    if confirm_password and new_password != confirm_password:
        return error_response("Nove lozinke se ne poklapaju", status_code=400)

    if len(new_password) < 8:
        return error_response(
            "Nova lozinka mora imati najmanje 8 karaktera", status_code=400
        )

    # Use password reset service for authenticated password change
    result = change_password_service(current_user, current_password, new_password)
    
    if result["success"]:
        return success_response(message=result["message"])
    else:
        return error_response(result["error"], status_code=result.get("status_code", 400))

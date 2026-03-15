# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify, redirect, make_response, session
from flask_login import login_user, logout_user
from app.services.user_service import get_user_by_username
from app.extensions import bcrypt, limiter
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
@limiter.limit("20 per hour")   # Maksimalno 20 pokušaja u satu
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

    if user and bcrypt.check_password_hash(user.password_hash, password):
        logger.info(f"✅ LOGIN SUCCESS: user_id={user.id}, username={username}")

        # CRITICAL: Explicitly set session data to force Flask to send Set-Cookie header
        session['user_id'] = user.id
        session['username'] = username
        session.permanent = True  # Make session persistent

        # Login user with Flask-Login (this also sets session)
        login_user(user, remember=True)

        # Create response
        response = make_response(success_response(
            data={'username': username},
            message="Prijava uspešna"
        ))

        logger.info(f"🍪 Session data set: user_id={user.id}, username={username}")
        logger.info(f"🍪 Session keys: {list(session.keys())}")
        logger.info(f"🍪 Flask should now send Set-Cookie header with SameSite=None; Secure")

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

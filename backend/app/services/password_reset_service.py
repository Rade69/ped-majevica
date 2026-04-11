"""
Password reset service with secure token generation and validation
Uses itsdangerous for cryptographically signed tokens with expiration
"""

import os
import logging
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from app.models.user import User
from app.extensions import db

logger = logging.getLogger(__name__)


class PasswordResetService:
    """Service for password reset token generation and validation"""
    
    # Token expiration time (1 hour)
    TOKEN_EXPIRATION = 3600  # seconds
    
    # Salt for password reset tokens (different from general app salt)
    RESET_SALT = "password-reset-salt"
    
    @staticmethod
    def get_serializer():
        """Get configured URLSafeTimedSerializer instance"""
        secret_key = current_app.config.get("SECRET_KEY")
        if not secret_key or secret_key == "dev-secret-key-change-in-production":
            logger.error("SECRET_KEY not properly configured for password reset tokens")
            raise ValueError("SECRET_KEY must be properly configured")
        
        return URLSafeTimedSerializer(secret_key, salt=PasswordResetService.RESET_SALT)
    
    @staticmethod
    def generate_reset_token(user):
        """
        Generate a secure password reset token for user
        
        Args:
            user: User model instance
            
        Returns:
            str: URL-safe token
        """
        serializer = PasswordResetService.get_serializer()
        
        # Token payload includes user_id and timestamp
        payload = {
            "user_id": user.id,
            "email": user.email or "",
            "created_at": datetime.utcnow().isoformat()
        }
        
        token = serializer.dumps(payload)
        logger.info(f"Generated password reset token for user_id={user.id}, email={user.email}")
        return token
    
    @staticmethod
    def validate_reset_token(token, max_age=None):
        """
        Validate a password reset token and return user if valid
        
        Args:
            token: Token string to validate
            max_age: Maximum age in seconds (defaults to TOKEN_EXPIRATION)
            
        Returns:
            User: User instance if token is valid, None otherwise
        """
        if not token:
            return None
            
        if max_age is None:
            max_age = PasswordResetService.TOKEN_EXPIRATION
            
        serializer = PasswordResetService.get_serializer()
        
        try:
            payload = serializer.loads(token, max_age=max_age)
            user_id = payload.get("user_id")
            
            if not user_id:
                logger.warning("Password reset token missing user_id")
                return None
                
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"Password reset token references non-existent user_id={user_id}")
                return None
                
            # Optional: Check if email matches (additional security)
            token_email = payload.get("email", "")
            if token_email and user.email and token_email != user.email:
                logger.warning(
                    f"Password reset token email mismatch: "
                    f"token_email={token_email}, user_email={user.email}"
                )
                return None
                
            logger.info(f"Valid password reset token for user_id={user_id}")
            return user
            
        except SignatureExpired:
            logger.warning("Password reset token expired")
            return None
        except BadSignature:
            logger.warning("Invalid password reset token signature")
            return None
        except Exception as e:
            logger.error(f"Error validating password reset token: {e}")
            return None
    
    @staticmethod
    def send_reset_email(user, reset_url):
        """
        Send password reset email to user (placeholder implementation)
        
        In production, integrate with email service (SMTP, SendGrid, etc.)
        
        Args:
            user: User model instance
            reset_url: Full reset URL with token
            
        Returns:
            bool: True if email would be sent (logged), False on error
        """
        try:
            # TODO: Implement actual email sending
            # For now, log the reset link for development
            logger.info(
                f"PASSWORD RESET EMAIL for {user.email}:\n"
                f"  User: {user.username} ({user.email})\n"
                f"  Reset URL: {reset_url}\n"
                f"  (In production, this would be sent via email)"
            )
            
            # Return True to indicate "email sent" for testing
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    @staticmethod
    def create_reset_url(token, frontend_base_url=None):
        """
        Create full password reset URL for frontend
        
        Args:
            token: Password reset token
            frontend_base_url: Frontend base URL (defaults to config or env)
            
        Returns:
            str: Complete reset URL
        """
        if not frontend_base_url:
            frontend_base_url = os.getenv(
                "FRONTEND_BASE_URL", 
                "https://pedmajevica.org"
            )
        
        # Frontend reset page (adjust path as needed)
        reset_path = "/pages/reset-password.html"
        
        # Create URL with token as query parameter
        reset_url = f"{frontend_base_url.rstrip('/')}{reset_path}?token={token}"
        
        return reset_url


def request_password_reset(email):
    """
    Request password reset for user with given email
    
    Args:
        email: User's email address
        
    Returns:
        dict: Result with success status and message
    """
    email = email.strip().lower() if email else ""
    
    if not email:
        return {
            "success": False,
            "error": "Email address is required",
            "status_code": 400
        }
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    # Security: Don't reveal if email exists or not
    # Always return success message even if user not found
    if not user:
        logger.info(f"Password reset requested for non-existent email: {email}")
        # Still return "success" to avoid email enumeration
        return {
            "success": True,
            "message": "If the email exists in our system, a reset link has been sent.",
            "email_sent": False  # Internal flag
        }
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Password reset requested for inactive user: {user.id}")
        # Still return generic success message
        return {
            "success": True,
            "message": "If the email exists in our system, a reset link has been sent.",
            "email_sent": False
        }
    
    try:
        # Generate reset token
        token = PasswordResetService.generate_reset_token(user)
        
        # Create reset URL
        reset_url = PasswordResetService.create_reset_url(token)
        
        # Send reset email (logs for now)
        email_sent = PasswordResetService.send_reset_email(user, reset_url)
        
        # Log the token for development/testing (remove in production!)
        if current_app.config.get("FLASK_ENV") == "development":
            logger.info(f"DEV: Password reset token for {email}: {token}")
        
        return {
            "success": True,
            "message": "If the email exists in our system, a reset link has been sent.",
            "email_sent": email_sent,
            "token": token if current_app.config.get("FLASK_ENV") == "development" else None
        }
        
    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        return {
            "success": False,
            "error": "Failed to process password reset request",
            "status_code": 500
        }


def reset_password_with_token(token, new_password):
    """
    Reset password using valid token
    
    Args:
        token: Password reset token
        new_password: New password to set
        
    Returns:
        dict: Result with success status and message
    """
    if not token or not new_password:
        return {
            "success": False,
            "error": "Token and new password are required",
            "status_code": 400
        }
    
    # Validate password strength
    if len(new_password) < 8:
        return {
            "success": False,
            "error": "Password must be at least 8 characters",
            "status_code": 400
        }
    
    # Validate token and get user
    user = PasswordResetService.validate_reset_token(token)
    
    if not user:
        return {
            "success": False,
            "error": "Invalid or expired reset token",
            "status_code": 400
        }
    
    try:
        # Update user password
        from app.extensions import bcrypt
        user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()
        
        logger.info(f"Password reset successful for user_id={user.id}")
        
        # Invalidate any existing sessions for security
        # (Flask-Login doesn't have built-in session invalidation,
        # but we can track password change timestamp)
        
        return {
            "success": True,
            "message": "Password has been reset successfully. You can now log in.",
            "user_id": user.id
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset failed for user_id={user.id}: {e}")
        return {
            "success": False,
            "error": "Failed to reset password",
            "status_code": 500
        }


def change_password(user, current_password, new_password):
    """
    Change password for authenticated user
    
    Args:
        user: User model instance
        current_password: Current password for verification
        new_password: New password to set
        
    Returns:
        dict: Result with success status and message
    """
    if not current_password or not new_password:
        return {
            "success": False,
            "error": "Current and new password are required",
            "status_code": 400
        }
    
    # Validate password strength
    if len(new_password) < 8:
        return {
            "success": False,
            "error": "New password must be at least 8 characters",
            "status_code": 400
        }
    
    # Verify current password
    from app.extensions import bcrypt
    if not bcrypt.check_password_hash(user.password_hash, current_password):
        logger.warning(f"Password change failed: wrong current password for user_id={user.id}")
        return {
            "success": False,
            "error": "Current password is incorrect",
            "status_code": 401
        }
    
    try:
        # Update password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()
        
        logger.info(f"Password changed successfully for user_id={user.id}")
        
        return {
            "success": True,
            "message": "Password has been changed successfully."
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change failed for user_id={user.id}: {e}")
        return {
            "success": False,
            "error": "Failed to change password",
            "status_code": 500
        }
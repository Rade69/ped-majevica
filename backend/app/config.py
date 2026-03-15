import os
import logging


class Config:
    # -----------------------------
    # SECURITY
    # -----------------------------
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Warn if SECRET_KEY is not set (critical for production)
    if not SECRET_KEY:
        SECRET_KEY = "dev-secret-key-change-in-production"
        # In production, this should be a hard error
        if os.getenv("FLASK_ENV") == "production":
            raise ValueError(
                "CRITICAL: SECRET_KEY must be set in production environment! "
                "Generate a random key with at least 32 characters."
            )

    # -----------------------------
    # DATABASE
    # -----------------------------
    # Support both SQLite (dev) and PostgreSQL (production)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Fix for Render.com PostgreSQL URL (postgres:// -> postgresql://)
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Fallback to SQLite for local development
    # Use absolute path for SQLite database based on app root
    if not DATABASE_URL:
        # Get the absolute path to the backend root (parent of app folder)
        backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        instance_path = os.path.join(backend_root, 'instance')
        os.makedirs(instance_path, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'ped.db')}"
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # PRODUCTION SETTINGS
    # -----------------------------
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # Session security - CROSS-ORIGIN SETTINGS
    # Frontend (Netlify) on different domain than backend (Render)

    # CRITICAL: For SameSite=None to work, browser MUST receive Set-Cookie header
    # Flask must send session cookie with these exact settings:
    SESSION_COOKIE_SECURE = True  # Required for SameSite=None
    SESSION_COOKIE_HTTPONLY = True  # Security
    SESSION_COOKIE_SAMESITE = "None"  # Allow cross-origin
    SESSION_COOKIE_NAME = "session"  # Explicit session cookie name
    SESSION_COOKIE_PATH = "/"  # Available for all paths

    # Remember me cookie settings (Flask-Login)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "None"
    REMEMBER_COOKIE_DURATION = 2592000  # 30 days in seconds

    # -----------------------------
    # LOGGING
    # -----------------------------
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # -----------------------------
    # RATE LIMITER STORAGE
    # -----------------------------
    # Use Redis in production, memory for development
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"

    @staticmethod
    def init_logging(app):
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

        # attach Flask logger
        app.logger.setLevel(Config.LOG_LEVEL)

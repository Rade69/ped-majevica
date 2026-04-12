from flask import Flask, jsonify, redirect, url_for, request
from app.config import Config
from app.extensions import db, migrate, login_manager, bcrypt, limiter, cors, csrf
from app.models.user import User
from app.services.email_service import init_mail


def create_app(test_config=None):
    app = Flask(__name__)

    # -----------------------------
    # CONFIG
    # -----------------------------
    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_object(Config)
        Config.init_logging(app)

    # -----------------------------
    # EXTENSIONS
    # -----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)
    init_mail(app)

    # CORS - Allow Netlify frontend to access API
    # Environment-based CORS origins
    if app.config.get("FLASK_ENV") == "production":
        cors_origins = [
            "https://pedmajevica.org",
            "https://www.pedmajevica.org",
        ]
    else:
        # Development origins
        cors_origins = [
            "http://localhost:*",
            "http://127.0.0.1:*",
            "https://ped-majevica.netlify.app",
            "http://127.0.0.1:5500",  # VS Code Live Server (dev only)
            "http://localhost:5500",  # VS Code Live Server (dev only)
            "http://127.0.0.1:8080",  # Python HTTP Server (dev only)
            "http://localhost:8080",  # Python HTTP Server (dev only)
        ]
    
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": cors_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
                "supports_credentials": True,
            }
        },
    )

    login_manager.login_view = "frontend.login"

    # Custom unauthorized handler for API endpoints
    @login_manager.unauthorized_handler
    def unauthorized():
        """Return JSON error for API, redirect for HTML pages"""
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Authentication required. Please log in.",
                        "authenticated": False,
                    }
                ),
                401,
            )
        # For non-API routes, redirect to login page
        return redirect("/login")

    # -----------------------------
    # USER LOADER
    # -----------------------------
    @login_manager.user_loader
    def load_user(user_id):
        from app.services.user_service import get_user_by_id

        return get_user_by_id(int(user_id))

    # -----------------------------
    # BLUEPRINTS
    # -----------------------------
    # IMPORTANT: frontend_bp MUST be registered FIRST to avoid conflicts!
    from app.routes.frontend import frontend_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.posts import posts_bp
    from app.routes.errors import errors_bp
    from app.routes.api import api_bp
    from app.routes.events import events_bp
    from app.routes.trails import trails_bp
    from app.routes.plan_aktivnosti import plan_bp
    from app.routes.gallery import gallery_bp

    app.register_blueprint(frontend_bp)  # ← MUST BE FIRST!
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(posts_bp)  # ← /admin/posts (database CRUD)
    app.register_blueprint(errors_bp)
    app.register_blueprint(api_bp)  # ← /api/posts (database CRUD)
    app.register_blueprint(events_bp)  # ← /api/events
    app.register_blueprint(trails_bp)  # ← /api/trails
    app.register_blueprint(plan_bp)  # ← /api/plan-aktivnosti
    app.register_blueprint(gallery_bp)  # ← /api/gallery

    # -----------------------------
    # CLI COMMANDS
    # -----------------------------
    from app.commands import (
        migrate_json_command,
        reset_admin_password_command,
        list_admins_command
    )

    app.cli.add_command(migrate_json_command)
    app.cli.add_command(reset_admin_password_command)
    app.cli.add_command(list_admins_command)

    # -----------------------------
    # INIT ADMIN USER
    # -----------------------------
    with app.app_context():
        from app.services.user_service import init_admin

        init_admin()

    # Note: Auto-migration removed for safety. Use Alembic migrations instead.
    # If trail table is missing columns, create a proper migration:
    # flask db migrate -m "Add columns to trail table"
    # flask db upgrade

    return app

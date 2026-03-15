from flask import Flask, jsonify, redirect, url_for, request
from app.config import Config
from app.extensions import db, migrate, login_manager, bcrypt, limiter, cors
from app.models.user import User


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

    # CORS - Allow Netlify frontend to access API
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:*",
                    "http://127.0.0.1:*",
                    "https://ped-majevica.netlify.app",
                    "http://pedmajevica.org",  # Temporary: HTTP until SSL is active
                    "https://pedmajevica.org",
                    "http://www.pedmajevica.org",  # Temporary: HTTP until SSL is active
                    "https://www.pedmajevica.org",
                    "http://127.0.0.1:5500",  # VS Code Live Server
                    "http://localhost:5500",  # VS Code Live Server
                    "http://127.0.0.1:8080",  # Python HTTP Server
                    "http://localhost:8080",  # Python HTTP Server
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
            }
        },
    )

    login_manager.login_view = "auth.login_page"

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
        # For non-API routes, redirect to login
        return redirect(url_for("auth.login_page"))

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
    from app.commands import migrate_json_command

    app.cli.add_command(migrate_json_command)

    # -----------------------------
    # INIT ADMIN USER
    # -----------------------------
    with app.app_context():
        from app.services.user_service import init_admin

        init_admin()

    # -----------------------------
    # AUTO-MIGRATE: Add missing columns
    # -----------------------------
    with app.app_context():
        try:
            from sqlalchemy import text, inspect

            inspector = inspect(db.engine)

            # Check if trail table exists
            if "trail" in inspector.get_table_names():
                existing_columns = [
                    col["name"] for col in inspector.get_columns("trail")
                ]

                columns_to_add = {
                    "features": "JSON",
                    "equipment": "JSON",
                    "warning": "TEXT",
                    "contact": "VARCHAR(100)",
                }

                with db.engine.connect() as conn:
                    for col_name, col_type in columns_to_add.items():
                        if col_name not in existing_columns:
                            conn.execute(
                                text(
                                    f"ALTER TABLE trail ADD COLUMN {col_name} {col_type}"
                                )
                            )
                            conn.commit()
                            app.logger.info(
                                f"✅ Auto-migrated: Added column '{col_name}' to trail table"
                            )
        except Exception as e:
            app.logger.warning(f"⚠️ Auto-migration check failed (non-critical): {e}")

    return app

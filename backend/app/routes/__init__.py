from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.posts import posts_bp
from app.routes.frontend import frontend_bp
from app.routes.errors import errors_bp
from app.routes.api import api_bp

__all__ = ['auth_bp', 'admin_bp', 'posts_bp', 'frontend_bp', 'errors_bp', 'api_bp']

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
cors = CORS()

# Rate limiter (default: by IP)
# Storage will be configured in app factory
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # nema globalnih limita, samo po-ruti
    storage_uri=os.getenv("RATELIMIT_STORAGE_URL", "memory://"),
    enabled=os.getenv("RATELIMIT_ENABLED", "true").lower() == "true",
)

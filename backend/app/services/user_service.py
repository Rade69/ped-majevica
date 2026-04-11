import os
import logging
from app.models.user import User
from app.extensions import bcrypt, db

logger = logging.getLogger(__name__)

# Admin users to create on startup - loaded from environment variables
# NO DEFAULT PASSWORDS - must be set in environment variables
ADMIN_USERS = {
    "radovan": os.getenv("ADMIN_RADOVAN_PASSWORD"),
    "aleksandar": os.getenv("ADMIN_ALEKSANDAR_PASSWORD"),
    "srecko": os.getenv("ADMIN_SRECKO_PASSWORD"),
    "milojko": os.getenv("ADMIN_MILOJKO_PASSWORD"),
}


def init_admin():
    """Create or update admin users in database on startup"""
    try:
        # Check if tables exist before trying to query them
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # If user table doesn't exist yet, skip - migrations will handle it
        if "user" not in inspector.get_table_names():
            return

        created_or_updated = 0
        skipped = 0
        
        # Create/update each admin user
        for username, password in ADMIN_USERS.items():
            if not password:
                logger.warning(
                    f"Admin user '{username}' skipped: ADMIN_{username.upper()}_PASSWORD "
                    f"environment variable not set"
                )
                skipped += 1
                continue
                
            user = User.query.filter_by(username=username).first()

            if user:
                # Update existing user password
                user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                logger.info(f"Updated admin user: {username}")
            else:
                # Create new user
                password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                user = User(
                    username=username,
                    password_hash=password_hash,
                    role='admin'
                )
                db.session.add(user)
                logger.info(f"Created admin user: {username}")
            
            created_or_updated += 1

        db.session.commit()
        
        if created_or_updated > 0:
            logger.info(f"Successfully initialized {created_or_updated} admin users")
        if skipped > 0:
            logger.warning(
                f"Skipped {skipped} admin users due to missing environment variables. "
                f"Set ADMIN_*_PASSWORD environment variables to create them."
            )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing admin users: {e}")


def get_user_by_username(username):
    """Get user from database by username"""
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    """Get user from database by ID"""
    return User.query.get(user_id)

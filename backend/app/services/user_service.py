import os
from app.models.user import User
from app.extensions import bcrypt, db

# Admin users to create on startup - loaded from environment variables
# Fallback to default values for backward compatibility (development only)
ADMIN_USERS = {
    "radovan": os.getenv("ADMIN_RADOVAN_PASSWORD", "radovan-!sofija#22$jelena%25&"),
    "aleksandar": os.getenv("ADMIN_ALEKSANDAR_PASSWORD", "Aleksandar$2026!Ped#Majevica"),
    "srecko": os.getenv("ADMIN_SRECKO_PASSWORD", "Srecko#PedMajevica!2026$"),
    "milojko": os.getenv("ADMIN_MILOJKO_PASSWORD", "Milojko&Majevica2026!Strong#"),
}


def init_admin():
    """Create or update admin users in database on startup"""
    try:
        # Check if tables exist before trying to query them
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        
        # If user table doesn't exist yet, skip - migrations will handle it
        if "user" not in inspector.get_table_names():
            return

        # Create/update each admin user
        for username, password in ADMIN_USERS.items():
            user = User.query.filter_by(username=username).first()

            if user:
                # Update existing user password
                user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                print(f"✅ Updated admin user: {username}", flush=True)
            else:
                # Create new user
                password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                user = User(
                    username=username,
                    password_hash=password_hash,
                    role='admin'
                )
                db.session.add(user)
                print(f"✅ Created admin user: {username}", flush=True)

        db.session.commit()
        print(f"🔐 Successfully initialized {len(ADMIN_USERS)} admin users", flush=True)

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error initializing admin users: {e}", flush=True)


def get_user_by_username(username):
    """Get user from database by username"""
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    """Get user from database by ID"""
    return User.query.get(user_id)

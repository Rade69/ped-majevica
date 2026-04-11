from datetime import datetime
from app.extensions import db, bcrypt
from flask_login import UserMixin
import enum


class UserRole(enum.Enum):
    """Role-based access control roles"""

    ADMIN = "admin"  # Pun pristup - sve operacije
    EDITOR = "editor"  # Uređivanje sadržaja
    USER = "user"  # Samo čitanje
    GUEST = "guest"  # Gost - ograničen pristup


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Role-based access control
    role = db.Column(
        db.String(20), default=UserRole.USER.value, nullable=False, index=True
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Additional fields
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<User {self.id} {self.username!r}>"

    def has_role(self, role):
        """Check if user has specific role"""
        if isinstance(role, str):
            return self.role == role
        return self.role == role.value

    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN.value

    def is_editor(self):
        """Check if user is editor or admin"""
        return self.role in [UserRole.EDITOR.value, UserRole.ADMIN.value]

    def update_last_login(self):
        """Update last login timestamp (caller must commit session)"""
        self.last_login = datetime.utcnow()

    def set_password(self, password):
        """Set password hash for user"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

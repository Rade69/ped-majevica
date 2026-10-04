from datetime import datetime
from app.extensions import db


class ContactMessage(db.Model):
    """Poruka poslata kroz kontakt formu na javnoj stranici (vidljiva u admin tabu "Poruke")."""
    __tablename__ = "contact_message"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    membership_interest = db.Column(db.Boolean, nullable=False, default=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ContactMessage {self.id} from {self.email}>"

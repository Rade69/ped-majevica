from datetime import datetime
from app.extensions import db


class Event(db.Model):
    """Model za kalendar akcije/događaje"""
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Date & Time
    event_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(10), nullable=True)  # "07:00"
    end_time = db.Column(db.String(10), nullable=True)    # "18:00"

    # Details
    max_participants = db.Column(db.Integer, nullable=True)
    activity_type = db.Column(db.String(50), nullable=True)  # "Izlet", "Radionica", "Uspon", itd.
    difficulty = db.Column(db.String(20), nullable=True)      # "Lagano", "Srednje", "Teško"
    location = db.Column(db.String(200), nullable=True)

    # Status
    published = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Event {self.id} {self.title}>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'max_participants': self.max_participants,
            'activity_type': self.activity_type,
            'difficulty': self.difficulty,
            'location': self.location,
            'published': self.published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

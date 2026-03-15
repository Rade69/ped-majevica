from datetime import datetime
from app.extensions import db


class PlanAktivnosti(db.Model):
    """Model za godišnji plan aktivnosti (iz JSON fajla)"""
    __tablename__ = "plan_aktivnosti"

    id = db.Column(db.Integer, primary_key=True)

    # Mjesec (JANUAR, FEBRUAR, itd.)
    month = db.Column(db.String(20), nullable=False, index=True)

    # Datum kao tekst (npr. "03/04.01.2026", "17/18.01.2026.")
    date = db.Column(db.String(50), nullable=True)

    # Naziv aktivnosti
    activity = db.Column(db.String(500), nullable=False)

    # Organizator/Vodič
    organizer_guide = db.Column(db.String(300), nullable=True)

    # Redoslijed za sortiranje unutar mjeseca
    sort_order = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PlanAktivnosti {self.id} {self.activity[:30]}>"

    def to_dict(self):
        return {
            'id': self.id,
            'month': self.month,
            'date': self.date,
            'activity': self.activity,
            'organizer_guide': self.organizer_guide,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

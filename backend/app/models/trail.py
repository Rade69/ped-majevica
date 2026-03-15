from datetime import datetime
from app.extensions import db


class Trail(db.Model):
    """Model za planinarske staze"""
    __tablename__ = "trail"

    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Trail details
    difficulty = db.Column(db.String(20), nullable=False, index=True)  # "Lagana", "Srednja", "Teška"
    distance_km = db.Column(db.Float, nullable=True)     # Dužina u km
    duration_hours = db.Column(db.Float, nullable=True)  # Trajanje u satima
    elevation_gain_m = db.Column(db.Integer, nullable=True)  # Uspona u metrima

    # Location
    start_point = db.Column(db.String(200), nullable=True)
    end_point = db.Column(db.String(200), nullable=True)
    region = db.Column(db.String(100), nullable=True)

    # Media
    images = db.Column(db.JSON, nullable=True)  # Lista putanja do slika
    gpx_file = db.Column(db.String(500), nullable=True)  # Putanja do GPX fajla

    # Features (boolean checkboxes)
    water_sources = db.Column(db.Boolean, default=False)
    shelters = db.Column(db.Boolean, default=False)
    scenic_views = db.Column(db.Boolean, default=False)

    # Modal content (editable text fields)
    features = db.Column(db.JSON, nullable=True)  # Lista karakteristika za modal
    equipment = db.Column(db.JSON, nullable=True)  # Lista potrebne opreme
    warning = db.Column(db.Text, nullable=True)  # Upozorenje
    contact = db.Column(db.String(100), nullable=True)  # Kontakt telefon

    # Status
    published = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Trail {self.id} {self.name}>"

    def to_dict(self):
        images_list = self.images or []
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'difficulty': self.difficulty,
            'distance_km': self.distance_km,
            'duration_hours': self.duration_hours,
            'elevation_gain_m': self.elevation_gain_m,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'region': self.region,
            'images': images_list,
            'image_url': images_list[0] if images_list else None,  # Prva slika za karticu
            'gpx_file': self.gpx_file,
            'gpx_file_url': self.gpx_file,  # Alias za frontend
            'water_sources': self.water_sources,
            'shelters': self.shelters,
            'scenic_views': self.scenic_views,
            'features': self.features or [],
            'equipment': self.equipment or [],
            'warning': self.warning or '',
            'contact': self.contact or '+387 65 581 354',
            'published': self.published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

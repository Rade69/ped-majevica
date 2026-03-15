from datetime import datetime
from app.extensions import db


class GalleryImage(db.Model):
    """Model za slike u galeriji - slike se čuvaju u bazi kao BLOB"""
    __tablename__ = "gallery_image"

    id = db.Column(db.Integer, primary_key=True)
    
    # Basic info
    title = db.Column(db.String(200), nullable=False)           # Naslov slike
    description = db.Column(db.Text, nullable=True)              # Opis
    
    # File info - ČUVANJE U BAZI
    image_data = db.Column(db.LargeBinary, nullable=False)       # BLOB - binary podaci slike
    image_mime = db.Column(db.String(50), nullable=False)        # MIME tip (image/jpeg, image/png)
    image_size = db.Column(db.Integer, nullable=True)            # Veličina fajla (bytes)
    image_width = db.Column(db.Integer, nullable=True)           # Širina slike (px)
    image_height = db.Column(db.Integer, nullable=True)          # Visina slike (px)
    
    # Thumbnail (manja verzija za brži prikaz)
    thumbnail_data = db.Column(db.LargeBinary, nullable=True)    # BLOB - thumbnail
    thumbnail_mime = db.Column(db.String(50), nullable=True)
    
    # Categorization
    category = db.Column(db.String(50), nullable=True, index=True)  # Kategorija
    tags = db.Column(db.String(500), nullable=True)              # Tagovi (zarezom odvojeni)
    
    # Ordering
    order = db.Column(db.Integer, default=0, nullable=False)     # Redosled prikazivanja
    
    # Status
    published = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<GalleryImage {self.id} {self.title}>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_size': self.image_size,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'image_mime': self.image_mime,
            'category': self.category,
            'tags': self.tags,
            'order': self.order,
            'published': self.published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Napomena: image_data se ne šalje u listi, samo u pojedinačnom zahtevu
        }

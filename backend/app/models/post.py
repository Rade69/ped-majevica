from datetime import datetime
from app.extensions import db


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)

    # Content fields
    content = db.Column(db.Text, nullable=False)  # Markdown content
    content_html = db.Column(db.Text, nullable=True)  # HTML rendered
    content_text = db.Column(db.Text, nullable=True)  # Plain text for search
    preview = db.Column(db.String(500), nullable=True)  # Short preview

    # Metadata
    category = db.Column(db.String(50), nullable=False, default='ostalo', index=True)
    word_count = db.Column(db.Integer, nullable=True)
    image_count = db.Column(db.Integer, default=0)
    images = db.Column(db.JSON, nullable=True)  # List of image paths

    # Author (FK to User)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_post_author_id'), nullable=True)
    author = db.relationship('User', backref='posts')

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Status
    published = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Reactions
    likes_count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Post {self.id} {self.title!r}>"

    def to_dict(self):
        """Convert Post to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'content_html': self.content_html,
            'content_text': self.content_text,
            'preview': self.preview,
            'category': self.category,
            'word_count': self.word_count,
            'image_count': self.image_count,
            'images': self.images or [],
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published': self.published,
            'likes_count': self.likes_count,
            'date': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }

from datetime import datetime
from app.extensions import db


class Like(db.Model):
    """
    Like/Reaction model - Many-to-Many relationship between User and Post
    """
    __tablename__ = "like"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_like_user_id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', name='fk_like_post_id'), nullable=False)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='likes')
    post = db.relationship('Post', backref='post_likes')

    # Unique constraint - jedan user može lajkovati post samo jednom
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),
    )

    def __repr__(self):
        return f"<Like user_id={self.user_id} post_id={self.post_id}>"

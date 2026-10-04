from datetime import datetime
from app.extensions import db


class ContentBlock(db.Model):
    """Uređivani blok sadržaja na javnoj stranici (npr. index / hero_subtitle).

    html=None znači "koristi originalni sadržaj iz HTML fajla".
    """
    __tablename__ = "content_block"
    __table_args__ = (db.UniqueConstraint("page", "key", name="uq_content_block_page_key"),)

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(40), nullable=False, index=True)
    key = db.Column(db.String(64), nullable=False)
    html = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("user.id", name="fk_content_block_user_id"), nullable=True)

    revisions = db.relationship(
        "ContentRevision",
        backref="block",
        cascade="all, delete-orphan",
        order_by="ContentRevision.id.desc()",
    )

    def __repr__(self):
        return f"<ContentBlock {self.page}/{self.key}>"


class ContentRevision(db.Model):
    """Historija izmjena bloka (za vraćanje na raniju verziju)."""
    __tablename__ = "content_revision"

    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(
        db.Integer,
        db.ForeignKey("content_block.id", name="fk_content_revision_block_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    html = db.Column(db.Text, nullable=True)  # None = vraćeno na original
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id", name="fk_content_revision_user_id"), nullable=True)

"""
Validation schemas for Post model.
Koristi Marshmallow za validaciju input podataka.
"""
import re
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


def generate_slug(title):
    """Generiše slug iz naslova"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip()[:250]
    return slug


class PostSchema(Schema):
    """Schema za validaciju kreiranja i ažuriranja blog postova"""
    
    id = fields.Integer(dump_only=True)
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    slug = fields.String(
        validate=validate.Length(max=250)
    )
    content = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )
    content_html = fields.String(dump_only=True)
    content_text = fields.String(dump_only=True)
    preview = fields.String(
        validate=validate.Length(max=500)
    )
    category = fields.String(
        validate=validate.OneOf([
            'vesti',
            'izvestaji',
            'saveti',
            'ostalo'
        ])
    )
    word_count = fields.Integer(dump_only=True)
    image_count = fields.Integer(dump_only=True)
    images = fields.List(fields.String(), load_default=list)
    author_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    published = fields.Boolean(load_default=True)
    likes_count = fields.Integer(dump_only=True)
    
    @pre_load
    def generate_slug_if_missing(self, data, **kwargs):
        """Automatski generiše slug iz naslova ako nije prosleđen"""
        if 'title' in data and 'slug' not in data:
            data['slug'] = generate_slug(data['title'])
        return data
    
    @validates('title')
    def validate_title(self, value):
        """Provera da naslov nije prazan ili samo whitespace"""
        if not value or not value.strip():
            raise ValidationError('Naslov ne može biti prazan')
    
    @validates('content')
    def validate_content(self, value):
        """Provera da sadržaj nije prazan"""
        if not value or not value.strip():
            raise ValidationError('Sadržaj ne može biti prazan')

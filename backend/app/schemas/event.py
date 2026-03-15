"""
Validation schemas for Event model.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class EventSchema(Schema):
    """Schema za validaciju kreiranja i ažuriranja događaja"""
    
    id = fields.Integer(dump_only=True)
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.String()
    event_date = fields.Date(
        required=True,
        error_messages={'invalid': 'Nevalidan format datuma. Koristite YYYY-MM-DD.'}
    )
    start_time = fields.String(validate=validate.Length(max=10))
    end_time = fields.String(validate=validate.Length(max=10))
    max_participants = fields.Integer()
    activity_type = fields.String(validate=validate.Length(max=50))
    difficulty = fields.String(
        validate=validate.OneOf(['lak', 'srednji', 'težak'])
    )
    location = fields.String(validate=validate.Length(max=200))
    published = fields.Boolean(load_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('title')
    def validate_title(self, value):
        """Provera da naslov nije prazan"""
        if not value or not value.strip():
            raise ValidationError('Naslov događaja ne može biti prazan')
    
    @validates('event_date')
    def validate_event_date(self, value):
        """Provera da datum nije u prošlosti (opciono)"""
        # Ovo je opciona validacija - možete je ukloniti ako želite
        # da dozvolite događaje iz prošlosti
        pass

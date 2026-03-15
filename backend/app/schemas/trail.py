"""
Validation schemas for Trail model.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class TrailSchema(Schema):
    """Schema za validaciju kreiranja i ažuriranja planinarskih staza"""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.String()
    difficulty = fields.String(
        required=True,
        validate=validate.OneOf(['lak', 'srednji', 'težak'])
    )
    distance_km = fields.Float()
    duration_hours = fields.Float()
    elevation_gain_m = fields.Integer()
    start_point = fields.String(validate=validate.Length(max=200))
    end_point = fields.String(validate=validate.Length(max=200))
    region = fields.String(validate=validate.Length(max=100))
    images = fields.List(fields.String(), load_default=list)
    gpx_file = fields.String(validate=validate.Length(max=500))
    water_sources = fields.Boolean()
    shelters = fields.Boolean()
    scenic_views = fields.Boolean()
    features = fields.Dict(load_default=dict)
    equipment = fields.Dict(load_default=dict)
    warning = fields.String()
    contact = fields.String(validate=validate.Length(max=100))
    published = fields.Boolean(load_default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('name')
    def validate_name(self, value):
        """Provera da naziv staze nije prazan"""
        if not value or not value.strip():
            raise ValidationError('Naziv staze ne može biti prazan')
    
    @validates('difficulty')
    def validate_difficulty(self, value):
        """Provera da težina bude jedna od dozvoljenih vrednosti"""
        if value and value not in ['lak', 'srednji', 'težak']:
            raise ValidationError(
                'Težina mora biti jedna od: lak, srednji, težak'
            )

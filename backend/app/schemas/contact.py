"""Schemas for the public contact form and the admin inbox."""
import re

from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(value):
    """Ukloni kontrolne znakove i višak razmaka na krajevima."""
    return _CONTROL.sub("", value).strip() if isinstance(value, str) else value


class ContactSchema(Schema):
    """Validacija poruke iz kontakt forme."""

    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    subject = fields.String(load_default="", validate=validate.Length(max=100))
    message = fields.String(required=True, validate=validate.Length(min=10, max=3000))
    membership_interest = fields.Boolean(load_default=False)

    @pre_load
    def strip_values(self, data, **kwargs):
        return {k: _clean(v) for k, v in data.items()}

    @validates("name")
    def no_newlines_in_name(self, value, **kwargs):
        if "\n" in value or "\r" in value:
            raise ValidationError("Ime ne smije imati novi red.")

    @validates("subject")
    def no_newlines_in_subject(self, value, **kwargs):
        if "\n" in value or "\r" in value:
            raise ValidationError("Tema ne smije imati novi red.")


class ContactMessageSchema(Schema):
    """Prikaz poruke u adminu."""

    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    subject = fields.String(dump_only=True)
    message = fields.String(dump_only=True)
    membership_interest = fields.Boolean(dump_only=True)
    is_read = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

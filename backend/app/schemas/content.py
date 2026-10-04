"""Schemas for content blocks."""
from marshmallow import Schema, fields


class ContentBlockSchema(Schema):
    page = fields.String(dump_only=True)
    key = fields.String(dump_only=True)
    html = fields.String(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class ContentRevisionSchema(Schema):
    id = fields.Integer(dump_only=True)
    html = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    created_by_id = fields.Integer(dump_only=True, allow_none=True)


class ContentSaveSchema(Schema):
    html = fields.String(required=True)

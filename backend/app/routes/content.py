from flask import Blueprint, request
from flask_login import current_user
from marshmallow import ValidationError

from app.schemas.content import ContentBlockSchema, ContentRevisionSchema, ContentSaveSchema
from app.services import content_service
from app.services.content_service import ContentError
from app.utils.decorators import admin_required
from app.utils.responses import error_response, success_response

content_bp = Blueprint("content", __name__, url_prefix="/api/content")


def _user_id():
    return current_user.id if current_user.is_authenticated else None


@content_bp.get("/<page>")
def get_page_content(page):
    """Javno: sadržaj blokova koje je admin izmijenio ({key: html})."""
    try:
        return success_response({"blocks": content_service.get_page_blocks(page)})
    except ContentError as e:
        return error_response(str(e), status_code=404)


@content_bp.put("/<page>/<key>")
@admin_required
def save_block(page, key):
    try:
        data = ContentSaveSchema().load(request.get_json(silent=True) or {})
        block = content_service.save_block(page, key, data["html"], _user_id())
    except ValidationError as e:
        return error_response("Neispravan zahtjev", status_code=400, errors=e.messages)
    except ContentError as e:
        return error_response(str(e), status_code=400)
    return success_response(ContentBlockSchema().dump(block), message="Sačuvano")


@content_bp.delete("/<page>/<key>")
@admin_required
def reset_block(page, key):
    """Vrati blok na originalni sadržaj."""
    try:
        block = content_service.reset_block(page, key, _user_id())
    except ContentError as e:
        return error_response(str(e), status_code=400)
    return success_response(ContentBlockSchema().dump(block), message="Vraćeno na original")


@content_bp.get("/<page>/<key>/history")
@admin_required
def block_history(page, key):
    try:
        revisions = content_service.get_history(page, key)
    except ContentError as e:
        return error_response(str(e), status_code=400)
    return success_response({"revisions": ContentRevisionSchema(many=True).dump(revisions)})


@content_bp.post("/<page>/<key>/restore/<int:revision_id>")
@admin_required
def restore(page, key, revision_id):
    try:
        block = content_service.restore_revision(page, key, revision_id, _user_id())
    except ContentError as e:
        return error_response(str(e), status_code=404)
    return success_response(ContentBlockSchema().dump(block), message="Verzija vraćena")

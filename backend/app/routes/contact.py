import logging

from flask import Blueprint, request
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.models.contact_message import ContactMessage
from app.schemas.contact import ContactMessageSchema, ContactSchema
from app.services import contact_service
from app.utils.decorators import admin_required
from app.utils.responses import error_response, success_response

logger = logging.getLogger(__name__)

contact_bp = Blueprint("contact", __name__, url_prefix="/api/contact")

SUCCESS_TEXT = "Hvala! Vaša poruka je primljena. Odgovaramo u najkraćem roku."


@contact_bp.post("")
@contact_bp.post("/")
@limiter.limit("5 per hour")
@limiter.limit("20 per day")
def send_message():
    """Javno: poruka iz kontakt forme. Čuva se u bazi, a društvo dobija i e-mail ako je pošta podešena."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("Neispravan zahtjev", status_code=400)

    # "Med" za robote: nevidljivo polje koje čovjek ne popunjava. Robotu glumimo uspjeh.
    if str(payload.get("website", "")).strip():
        logger.info("Contact form honeypot triggered; message discarded")
        return success_response(message=SUCCESS_TEXT, status_code=201)

    try:
        data = ContactSchema().load(payload, unknown="exclude")
    except ValidationError as e:
        return error_response("Provjerite unesene podatke.", status_code=400, errors=e.messages)

    contact_service.create_message(data)
    return success_response(message=SUCCESS_TEXT, status_code=201)


@contact_bp.get("")
@contact_bp.get("/")
@admin_required
def list_messages():
    """Admin: poruke, najnovije prve. ?unread=1 vraća samo nepročitane."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 50)
    query = ContactMessage.query
    if request.args.get("unread") in ("1", "true"):
        query = query.filter_by(is_read=False)
    pagination = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    unread = ContactMessage.query.filter_by(is_read=False).count()
    return success_response({
        "messages": ContactMessageSchema(many=True).dump(pagination.items),
        "unread": unread,
        "pagination": {"page": page, "pages": pagination.pages, "total": pagination.total},
    })


@contact_bp.put("/<int:message_id>/read")
@admin_required
def mark_read(message_id):
    message = db.session.get(ContactMessage, message_id)
    if message is None:
        return error_response("Poruka nije pronađena", status_code=404)
    desired = request.get_json(silent=True) or {}
    message.is_read = bool(desired.get("is_read", True))
    db.session.commit()
    return success_response(ContactMessageSchema().dump(message))


@contact_bp.delete("/<int:message_id>")
@admin_required
def delete_message(message_id):
    message = db.session.get(ContactMessage, message_id)
    if message is None:
        return error_response("Poruka nije pronađena", status_code=404)
    db.session.delete(message)
    db.session.commit()
    return success_response(message="Poruka obrisana")

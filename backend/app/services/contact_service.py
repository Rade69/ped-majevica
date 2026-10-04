"""Poslovna logika kontakt forme: čuvanje poruke i obavještenje društvu e-mailom."""
import html
import logging
import os

from app.extensions import db
from app.models.contact_message import ContactMessage
from app.services.email_service import send_email_async

logger = logging.getLogger(__name__)

DEFAULT_NOTIFY_EMAIL = "pedmajevica88@gmail.com"


def create_message(data):
    """Sačuvaj poruku u bazi (uvijek), pa pokušaj poslati obavještenje (greška e-maila ne smije izgubiti poruku)."""
    message = ContactMessage(
        name=data["name"],
        email=data["email"],
        subject=data.get("subject") or None,
        message=data["message"],
        membership_interest=bool(data.get("membership_interest")),
    )
    db.session.add(message)
    db.session.commit()

    try:
        notify_by_email(message)
    except Exception:
        logger.exception("Contact notification failed for message %s", message.id)
    return message


def notify_by_email(message):
    """Pošalji obavještenje društvu; Reply-To je e-mail posjetioca. Bez SMTP podešavanja samo se zapiše u log."""
    recipient = os.getenv("CONTACT_NOTIFY_EMAIL", DEFAULT_NOTIFY_EMAIL)
    subject_part = message.subject or "Poruka sa sajta"
    subject = f"[PED Majevica] {subject_part} - {message.name}"[:150]
    subject = " ".join(subject.split())  # bez novih redova u zaglavlju

    text = (
        f"Nova poruka sa kontakt forme pedmajevica.org\n\n"
        f"Ime: {message.name}\n"
        f"E-mail: {message.email}\n"
        f"Tema: {message.subject or '-'}\n"
        f"Zanima ga članstvo: {'da' if message.membership_interest else 'ne'}\n\n"
        f"{message.message}\n"
    )
    body = (
        "<p>Nova poruka sa kontakt forme <strong>pedmajevica.org</strong></p>"
        f"<p><strong>Ime:</strong> {html.escape(message.name)}<br>"
        f"<strong>E-mail:</strong> {html.escape(message.email)}<br>"
        f"<strong>Tema:</strong> {html.escape(message.subject or '-')}<br>"
        f"<strong>Zanima ga članstvo:</strong> {'da' if message.membership_interest else 'ne'}</p>"
        f"<p style=\"white-space:pre-wrap\">{html.escape(message.message)}</p>"
    )
    return send_email_async(subject, [recipient], body, text, reply_to=message.email)

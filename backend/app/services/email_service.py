"""
Email service using Flask-Mail for SMTP delivery.
Supports HTML templates, graceful fallback to logging when SMTP is not configured.
"""

import logging
from threading import Thread
from flask import current_app, render_template_string
from flask_mail import Message, Mail

logger = logging.getLogger(__name__)

# Global Mail instance, initialised lazily
_mail = None


def get_mail():
    """Lazy-initialise Flask-Mail singleton."""
    global _mail
    if _mail is None:
        _mail = Mail()
    return _mail


def init_mail(app):
    """Initialise Flask-Mail with app config (called from create_app)."""
    mail = Mail(app)
    return mail


def _is_smtp_configured():
    """Check if SMTP is properly configured."""
    server = current_app.config.get("MAIL_SERVER", "")
    username = current_app.config.get("MAIL_USERNAME", "")
    password = current_app.config.get("MAIL_PASSWORD", "")
    return bool(server and username and password)


def send_email_sync(subject, recipients, html_body, text_body=None):
    """Send email synchronously via Flask-Mail."""
    try:
        from flask_mail import Message

        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            body=text_body or html_body,
            sender=current_app.config.get(
                "MAIL_DEFAULT_SENDER", "noreply@pedmajevica.org"
            ),
        )
        mail = get_mail()
        mail.send(msg)
        logger.info(f"Email sent to {recipients}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
        return False


def send_email_async(subject, recipients, html_body, text_body=None):
    """Send email in a background thread (non-blocking)."""
    if not _is_smtp_configured():
        logger.warning(
            f"SMTP not configured, logging email instead of sending: {subject} -> {recipients}"
        )
        logger.info(f"[EMAIL LOG] To: {recipients} | Subject: {subject} | Body: {text_body or html_body}")
        return False

    thread = Thread(
        target=send_email_sync,
        args=(subject, recipients, html_body, text_body),
    )
    thread.start()
    return True


# ─────────────────────────────────────────────
#  Email templates
# ─────────────────────────────────────────────

PASSWORD_RESET_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: #D62828; color: #fff; padding: 24px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 22px; }}
        .body {{ padding: 32px 24px; color: #333; line-height: 1.6; }}
        .body p {{ margin: 0 0 16px; }}
        .btn {{ display: inline-block; padding: 14px 32px; background: #D62828; color: #fff; text-decoration: none; border-radius: 6px; font-size: 16px; margin: 16px 0; }}
        .btn:hover {{ background: #b01f1f; }}
        .footer {{ background: #f9f9f9; padding: 16px 24px; text-align: center; font-size: 12px; color: #888; }}
        .expiry {{ color: #888; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏔️ PED Majevica 1988</h1>
        </div>
        <div class="body">
            <p>Zdravo <strong>{{ username }}</strong>,</p>
            <p>Primili smo zahtjev za resetovanje lozinke za vaš nalog.</p>
            <p>Kliknite na dugme ispod da postavite novu lozinku:</p>
            <p style="text-align: center;">
                <a href="{{ reset_url }}" class="btn">Resetuj lozinku</a>
            </p>
            <p class="expiry">⏰ Link važi 1 sat od generisanja.</p>
            <p>Ako niste tražili resetovanje lozinke, ignorišite ovaj email.</p>
        </div>
        <div class="footer">
            <p>© 2026 Planinarsko ekološko društvo Majevica 1988</p>
            <p>https://pedmajevica.ba</p>
        </div>
    </div>
</body>
</html>
"""

PASSWORD_RESET_TEXT = """
Zdravo {username},

Primili smo zahtjev za resetovanje lozinke za vaš nalog.

Kliknite na link ispod da postavite novu lozinku:
{reset_url}

Link važi 1 sat od generisanja.

Ako niste tražili resetovanje lozinke, ignorišite ovaj email.

--
© 2026 Planinarsko ekološko društvo Majevica 1988
https://pedmajevica.ba
"""


# ─────────────────────────────────────────────
#  High-level helpers
# ─────────────────────────────────────────────

def send_password_reset_email(user, reset_url):
    """
    Send password reset email to a user.
    Falls back to logging if SMTP is not configured.
    """
    username = user.username
    email = user.email or ""

    html_body = render_template_string(
        PASSWORD_RESET_HTML, username=username, reset_url=reset_url
    )
    text_body = PASSWORD_RESET_TEXT.format(username=username, reset_url=reset_url)

    subject = "PED Majevica - Resetovanje lozinke"

    if not _is_smtp_configured():
        logger.warning(
            f"SMTP not configured — logging password reset token instead of sending email.\n"
            f"  User: {username} ({email})\n"
            f"  Token/URL: {reset_url}\n"
            f"  CLI alternative: flask reset-admin-password --username {username}"
        )
        if current_app.config.get("FLASK_ENV") == "development":
            print(f"\n🔐 PASSWORD RESET TOKEN for {username}:")
            print(f"   URL: {reset_url}")
            print(f"   CLI: flask reset-admin-password --username {username}\n")
        return False

    return send_email_async(subject, [email], html_body, text_body)

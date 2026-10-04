"""Probni e-mail (poziva ga setup-mail.sh): provjerava da su podaci za slanje ispravni."""
import os

from app import create_app
from app.services.email_service import send_email_sync

app = create_app()
with app.app_context():
    ok = send_email_sync(
        "PED Majevica: probna poruka",
        [os.environ["CONTACT_NOTIFY_EMAIL"]],
        "<p>Slanje obavještenja sa kontakt forme je podešeno i radi.</p>",
        "Slanje obavještenja sa kontakt forme je podešeno i radi.",
    )

if ok:
    print("USPJEH: probni e-mail je poslat (provjerite sanduče i neželjenu poštu).")
else:
    print("GREŠKA: e-mail nije poslat. Provjerite adresu i lozinku za aplikacije: journalctl -u pedmajevica -n 30")

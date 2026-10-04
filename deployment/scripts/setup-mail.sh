#!/bin/bash
# ========================================
# PED Majevica - podesavanje slanja e-maila (obavjestenja o porukama iz kontakt forme)
#
# Pokrenuti na serveru kao root:
#   sudo bash /var/www/ped-majevica/deployment/scripts/setup-mail.sh
#
# Trazi Gmail adresu i "lozinku za aplikacije" (NE obicnu lozinku). Lozinka se unosi skriveno,
# upisuje samo u backend/.env (chmod 600) i ne prikazuje se nigdje.
#
# Lozinka za aplikacije: Google nalog -> Sigurnost -> Potvrda u 2 koraka (ukljuciti) ->
# Lozinke za aplikacije -> napraviti novu (16 znakova).
# ========================================
set -euo pipefail

APP_DIR="/var/www/ped-majevica"
ENV_FILE="$APP_DIR/backend/.env"
APP_USER="pedmajevica"

[ "$EUID" -eq 0 ] || { echo "Pokrenite kao root: sudo bash $0"; exit 1; }
[ -f "$ENV_FILE" ] || { echo "Ne postoji $ENV_FILE"; exit 1; }

read -r -p "Gmail adresa koja salje obavjestenja: " MAIL_USER
read -r -s -p "Lozinka za aplikacije (unos se ne vidi): " MAIL_PASS
echo
read -r -p "Na koju adresu stizu obavjestenja [pedmajevica88@gmail.com]: " NOTIFY
NOTIFY="${NOTIFY:-pedmajevica88@gmail.com}"
MAIL_PASS="${MAIL_PASS// /}"   # Google prikazuje lozinku sa razmacima; razmaci se uklanjaju

[ -n "$MAIL_USER" ] && [ -n "$MAIL_PASS" ] || { echo "Adresa i lozinka su obavezni."; exit 1; }

# upisi/zamijeni kljuceve u .env (ostalo ostaje netaknuto); vrijednost se ne tumaci kao regex ni kao shell
set_key() {
    python3 - "$ENV_FILE" "$1" "$2" <<'PYEOF'
import sys
path, key, value = sys.argv[1:4]
lines = open(path, encoding="utf-8").read().splitlines()
found = False
for i, line in enumerate(lines):
    if line.startswith(key + "="):
        lines[i] = f"{key}={value}"
        found = True
if not found:
    lines.append(f"{key}={value}")
open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
PYEOF
}

cp "$ENV_FILE" "$ENV_FILE.bak-$(date +%F-%H%M)"
set_key MAIL_SERVER "smtp.gmail.com"
set_key MAIL_PORT "587"
set_key MAIL_USE_TLS "true"
set_key MAIL_USERNAME "$MAIL_USER"
set_key MAIL_PASSWORD "$MAIL_PASS"
set_key MAIL_DEFAULT_SENDER "$MAIL_USER"
set_key CONTACT_NOTIFY_EMAIL "$NOTIFY"
chown "$APP_USER":"$APP_USER" "$ENV_FILE"
chmod 600 "$ENV_FILE"

systemctl restart pedmajevica
sleep 3

echo "Saljem probni e-mail na $NOTIFY ..."
TEST_PY="$(mktemp /tmp/ped-mail-test.XXXXXX)"
cp "$APP_DIR/deployment/scripts/mail_test.py" "$TEST_PY"
chmod 644 "$TEST_PY"
cd "$APP_DIR/backend"
sudo -u "$APP_USER" bash -c "set -a; . ./.env; set +a; PYTHONPATH=. venv/bin/python '$TEST_PY'" || true
rm -f "$TEST_PY"

#!/bin/bash
# ========================================
# PED Majevica - jednokratno podesavanje servera (Ubuntu 22.04 / 24.04)
# ========================================
# Pokrenuti kao root na serveru:
#   sudo bash server-setup.sh
#
# Idempotentno: moze se pokrenuti ponovo; postojeci .env i baza se NE diraju.
# ========================================
set -euo pipefail

REPO_URL="https://github.com/Rade69/ped-majevica.git"
BRANCH="${BRANCH:-main}"
APP_DIR="/var/www/ped-majevica"
APP_USER="pedmajevica"
DB_NAME="ped_majevica"
DB_USER="peduser"

[ "$EUID" -eq 0 ] || { echo "Pokrenite kao root: sudo bash $0"; exit 1; }

echo "==> Paketi"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-venv python3-pip postgresql postgresql-contrib \
    nginx git certbot python3-certbot-nginx ufw fail2ban curl ca-certificates openssl

# Node >= 18 je potreban za build Tailwind CSS-a
NODE_MAJOR="$(node -v 2>/dev/null | sed 's/v\([0-9]*\).*/\1/' || echo 0)"
if [ "${NODE_MAJOR:-0}" -lt 18 ]; then
    echo "==> Instalacija Node.js 20 (NodeSource)"
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

echo "==> Korisnik i direktorijumi"
id "$APP_USER" >/dev/null 2>&1 || useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
mkdir -p /var/log/pedmajevica "$(dirname "$APP_DIR")"
chown "$APP_USER":"$APP_USER" /var/log/pedmajevica

echo "==> Kod"
if [ ! -d "$APP_DIR/.git" ]; then
    git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
git config --global --add safe.directory "$APP_DIR" || true

echo "==> Baza"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    DB_PASS="$(openssl rand -hex 24)"
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    NEW_DB=1
else
    NEW_DB=0
    echo "Korisnik $DB_USER vec postoji - baza se ne dira."
fi

echo "==> .env"
ENV_FILE="$APP_DIR/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
    [ "$NEW_DB" -eq 1 ] || { echo "Baza postoji ali nema .env - kreirajte $ENV_FILE rucno."; exit 1; }
    umask 077
    ADMIN_PASSWORDS=""
    {
        echo "FLASK_ENV=production"
        echo "SECRET_KEY=$(openssl rand -hex 32)"
        echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
        echo "LOG_LEVEL=INFO"
        for u in RADOVAN ALEKSANDAR SRECKO MILOJKO; do
            p="$(openssl rand -base64 18 | tr -d '/+=' | cut -c1-16)"
            echo "ADMIN_${u}_PASSWORD=$p"
            ADMIN_PASSWORDS="$ADMIN_PASSWORDS\n  $u: $p"
        done
    } > "$ENV_FILE"
    chown "$APP_USER":"$APP_USER" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo "Generisane admin lozinke (prikazane samo sada, sacuvajte ih):"
    echo -e "$ADMIN_PASSWORDS"
else
    echo ".env vec postoji - ne diram ga."
fi

echo "==> Python venv"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/backend/venv"
sudo -u "$APP_USER" "$APP_DIR/backend/venv/bin/pip" install --upgrade pip -q
sudo -u "$APP_USER" "$APP_DIR/backend/venv/bin/pip" install -r "$APP_DIR/backend/requirements.txt" -q

echo "==> systemd i nginx"
cp "$APP_DIR/deployment/configs/pedmajevica.service" /etc/systemd/system/pedmajevica.service
cp "$APP_DIR/deployment/configs/pedmajevica.nginx.conf" /etc/nginx/sites-available/pedmajevica
ln -sf /etc/nginx/sites-available/pedmajevica /etc/nginx/sites-enabled/pedmajevica
rm -f /etc/nginx/sites-enabled/default
systemctl daemon-reload
systemctl enable pedmajevica

echo "==> Firewall"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo
echo "Podesavanje gotovo. Sljedece: sudo bash $APP_DIR/deployment/scripts/deploy.sh"

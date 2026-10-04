#!/bin/bash
# ========================================
# PED Majevica - deploy/update (pokrenuti na serveru kao root)
#   sudo bash /var/www/ped-majevica/deployment/scripts/deploy.sh
# ========================================
set -euo pipefail

APP_DIR="/var/www/ped-majevica"
APP_USER="pedmajevica"
BRANCH="${BRANCH:-main}"
run() { sudo -u "$APP_USER" "$@"; }

cd "$APP_DIR"
echo "==> git pull ($BRANCH)"
run git fetch origin "$BRANCH"
run git checkout "$BRANCH"
run git merge --ff-only "origin/$BRANCH"

echo "==> Python zavisnosti"
run backend/venv/bin/pip install -r backend/requirements.txt -q

echo "==> Frontend CSS"
( cd frontend && run npm ci --silent && run npm run build )

echo "==> Migracije baze"
( cd backend && FLASK_APP=wsgi.py run venv/bin/flask db upgrade )

echo "==> Restart"
cp deployment/configs/pedmajevica.service /etc/systemd/system/pedmajevica.service
cp deployment/configs/pedmajevica-backup.service deployment/configs/pedmajevica-backup.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now pedmajevica-backup.timer
systemctl restart pedmajevica
nginx -t && systemctl reload nginx

sleep 3
systemctl is-active pedmajevica
curl -fsS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/ || echo "UPOZORENJE: aplikacija ne odgovara"

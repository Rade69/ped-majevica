#!/bin/bash
# ========================================
# PED Majevica - deploy/update (pokrenuti na serveru kao root)
#   sudo bash /var/www/ped-majevica/deployment/scripts/deploy.sh
#
# Poziva se i automatski iz GitHub Actions (SSH kljuc sa ogranicenjem
# "samo ova skripta"). Ako aplikacija poslije deploya ne odgovara,
# kod se vraca na prethodnu verziju i skripta zavrsava sa greskom.
# ========================================
set -euo pipefail

APP_DIR="/var/www/ped-majevica"
APP_USER="pedmajevica"
BRANCH="${BRANCH:-main}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/}"
run() { sudo -u "$APP_USER" "$@"; }

health_check() {
    for _ in $(seq 1 10); do
        if curl -fsS -o /dev/null -m 5 "$HEALTH_URL"; then
            return 0
        fi
        sleep 3
    done
    return 1
}

build_and_restart() {
    ( cd frontend && run npm ci --silent && run npm run build )
    cp deployment/configs/pedmajevica.service /etc/systemd/system/pedmajevica.service
    cp deployment/configs/pedmajevica-backup.service deployment/configs/pedmajevica-backup.timer /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable --now pedmajevica-backup.timer
    systemctl restart pedmajevica
    nginx -t && systemctl reload nginx
}

main() {
    # samo jedan deploy istovremeno
    exec 9>/var/lock/pedmajevica-deploy.lock
    flock -n 9 || { echo "Deploy vec radi, pokusajte kasnije."; exit 1; }

    cd "$APP_DIR"
    PREV="$(run git rev-parse HEAD)"

    echo "==> git pull ($BRANCH), trenutno: ${PREV:0:7}"
    run git fetch origin "$BRANCH"
    run git checkout "$BRANCH"
    run git merge --ff-only "origin/$BRANCH"
    NEW="$(run git rev-parse HEAD)"
    echo "    novo: ${NEW:0:7}"

    echo "==> Python zavisnosti"
    run backend/venv/bin/pip install -r backend/requirements.txt -q

    echo "==> Migracije baze"
    ( cd backend && FLASK_APP=wsgi.py run venv/bin/flask db upgrade )

    echo "==> Frontend CSS i restart"
    build_and_restart

    echo "==> Provjera da aplikacija odgovara"
    if health_check; then
        systemctl is-active pedmajevica
        echo "OK: deploy gotov (${NEW:0:7})"
        return 0
    fi

    echo "GRESKA: aplikacija ne odgovara. Vracam kod na ${PREV:0:7}." >&2
    run git reset --hard "$PREV"
    run backend/venv/bin/pip install -r backend/requirements.txt -q || true
    build_and_restart || true
    if health_check; then
        echo "Vraceno na staru verziju, stranica radi. Izmjena ${NEW:0:7} NIJE objavljena." >&2
    else
        echo "KRITICNO: ni stara verzija ne odgovara. Provjerite: journalctl -u pedmajevica -n 50" >&2
    fi
    return 1
}

# Cijela skripta se mora procitati prije izvrsavanja: git pull moze izmijeniti
# ovaj fajl dok se izvrsava.
main "$@"
exit $?

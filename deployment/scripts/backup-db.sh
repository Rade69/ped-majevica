#!/bin/bash
# ========================================
# PED Majevica - sedmicni backup PostgreSQL baze
# Pokrece ga systemd timer (pedmajevica-backup.timer) kao root.
# Rucno:  sudo bash /var/www/ped-majevica/deployment/scripts/backup-db.sh
# Vracanje: gunzip -c FAJL.sql.gz | sudo -u postgres psql ped_majevica   (u praznu bazu)
# ========================================
set -euo pipefail

DB_NAME="ped_majevica"
BACKUP_DIR="/var/backups/pedmajevica"
KEEP=8   # broj zadnjih kopija koje se cuvaju

umask 077
mkdir -p "$BACKUP_DIR"

FILE="$BACKUP_DIR/${DB_NAME}-$(date +%F-%H%M).sql.gz"
TMP="$FILE.tmp"

sudo -u postgres pg_dump "$DB_NAME" | gzip > "$TMP"
gzip -t "$TMP"                      # provjera da arhiva nije ostecena
[ "$(stat -c %s "$TMP")" -gt 1000 ] # prazna/sumnjivo mala kopija = greska
mv "$TMP" "$FILE"

# obrisi najstarije, zadrzi zadnjih $KEEP
ls -1t "$BACKUP_DIR"/${DB_NAME}-*.sql.gz | tail -n +$((KEEP + 1)) | xargs -r rm --

echo "Backup gotov: $FILE ($(du -h "$FILE" | cut -f1))"

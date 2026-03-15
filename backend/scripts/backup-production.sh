#!/bin/bash
# ========================================
# PED Majevica 1988 - Backup Script
# ========================================
# Automated backup script for production
#
# Setup:
#   1. Copy to /usr/local/bin/pedmajevica-backup.sh
#   2. Make executable: chmod +x /usr/local/bin/pedmajevica-backup.sh
#   3. Add to cron: 0 2 * * * /usr/local/bin/pedmajevica-backup.sh
#
# ========================================

set -e  # Exit on error

# -----------------------------
# Configuration
# -----------------------------
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/pedmajevica"
APP_DIR="/var/www/ped-majevica"
DB_NAME="pedmajevica"
DB_USER="pedadmin"
DB_HOST="localhost"
DB_PASS=""  # Will be read from .env or set manually
RETENTION_DAYS=7
LOG_FILE="/var/log/pedmajevica/backup.log"

# -----------------------------
# Functions
# -----------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
    exit 1
}

# -----------------------------
# Pre-backup Checks
# -----------------------------
log "=========================================="
log "Starting PED Majevica Backup"
log "=========================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    error "Please run as root or with sudo"
fi

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    log "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    chmod 750 "$BACKUP_DIR"
fi

# Create log directory if it doesn't exist
if [ ! -d "/var/log/pedmajevica" ]; then
    mkdir -p "/var/log/pedmajevica"
fi

# -----------------------------
# Database Backup
# -----------------------------
log "Backing up database: $DB_NAME"

# Try to read password from .env file
if [ -f "$APP_DIR/backend/.env" ]; then
    DB_PASS=$(grep "^DATABASE_URL=" "$APP_DIR/backend/.env" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
fi

# If password is still empty, try PGPASSWORD from environment
if [ -z "$DB_PASS" ]; then
    DB_PASS="${PGPASSWORD:-}"
fi

# Create database backup
if [ -n "$DB_PASS" ]; then
    PGPASSWORD="$DB_PASS" pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/db_$DATE.sql" 2>/dev/null
else
    # Try without password (peer authentication)
    sudo -u postgres pg_dump "$DB_NAME" > "$BACKUP_DIR/db_$DATE.sql" 2>/dev/null || true
fi

# Check if backup was successful
if [ ! -s "$BACKUP_DIR/db_$DATE.sql" ]; then
    error "Database backup failed or is empty"
fi

# Compress database backup
log "Compressing database backup..."
gzip "$BACKUP_DIR/db_$DATE.sql"
log "Database backup created: ${BACKUP_DIR}/db_$DATE.sql.gz"

# -----------------------------
# Application Files Backup
# -----------------------------
log "Backing up application files..."

# Create tarball of application files (excluding unnecessary directories)
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='instance' \
    --exclude='logs' \
    --exclude='.git' \
    --exclude='*.log' \
    -C "$APP_DIR" . 2>/dev/null || true

if [ -f "$BACKUP_DIR/files_$DATE.tar.gz" ]; then
    log "Application files backup created: ${BACKUP_DIR}/files_$DATE.tar.gz"
else
    error "Application files backup failed"
fi

# -----------------------------
# Uploads Backup (Critical!)
# -----------------------------
log "Backing up uploads..."

if [ -d "$APP_DIR/backend/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$APP_DIR/backend" uploads/ 2>/dev/null || true
    
    if [ -f "$BACKUP_DIR/uploads_$DATE.tar.gz" ]; then
        log "Uploads backup created: ${BACKUP_DIR}/uploads_$DATE.tar.gz"
    else
        log "WARNING: Uploads backup failed or uploads directory is empty"
    fi
else
    log "WARNING: Uploads directory not found"
fi

# -----------------------------
# Frontend Assets Backup
# -----------------------------
log "Backing up frontend assets..."

if [ -d "$APP_DIR/frontend" ]; then
    tar -czf "$BACKUP_DIR/frontend_$DATE.tar.gz" \
        --exclude='node_modules' \
        --exclude='package-lock.json' \
        -C "$APP_DIR" frontend/ 2>/dev/null || true
    
    if [ -f "$BACKUP_DIR/frontend_$DATE.tar.gz" ]; then
        log "Frontend backup created: ${BACKUP_DIR}/frontend_$DATE.tar.gz"
    fi
fi

# -----------------------------
# Cleanup Old Backups
# -----------------------------
log "Cleaning up backups older than $RETENTION_DAYS days..."

find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

log "Old backups cleaned up"

# -----------------------------
# Backup Summary
# -----------------------------
log "=========================================="
log "Backup Completed Successfully"
log "=========================================="
log "Backup files:"
ls -lh "$BACKUP_DIR"/*$DATE* 2>/dev/null | tee -a "$LOG_FILE"
log ""
log "Total backup size:"
du -sh "$BACKUP_DIR" | tee -a "$LOG_FILE"
log "=========================================="

# -----------------------------
# Optional: Upload to Remote Storage
# -----------------------------
# Uncomment and configure if you want to upload backups to S3, Dropbox, etc.

# Example for AWS S3:
# aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" s3://your-bucket/pedmajevica/db/
# aws s3 cp "$BACKUP_DIR/files_$DATE.tar.gz" s3://your-bucket/pedmajevica/files/
# aws s3 cp "$BACKUP_DIR/uploads_$DATE.tar.gz" s3://your-bucket/pedmajevica/uploads/

# Example for rsync to remote server:
# rsync -avz "$BACKUP_DIR/" user@remote-server:/backups/pedmajevica/

exit 0

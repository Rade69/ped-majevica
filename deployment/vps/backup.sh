#!/bin/bash
#
# Database Backup Script
# Kreira backup PostgreSQL baze i arhivira fajlove
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="/var/backups/pedmajevica"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
DB_NAME="ped_majevica"
DB_USER="peduser"

echo -e "${YELLOW}💾 Creating backup...${NC}"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo -e "${YELLOW}🗄️  Backing up database...${NC}"
sudo -u postgres pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup uploaded files (if any)
# tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/pedmajevica/uploads 2>/dev/null || true

# Keep only last 7 days of backups
echo -e "${YELLOW}🗑️  Cleaning old backups (keeping last 7 days)...${NC}"
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
# find $BACKUP_DIR -name "files_*.tar.gz" -mtime +7 -delete

echo ""
echo -e "${GREEN}✅ Backup complete: $BACKUP_DIR/db_$DATE.sql.gz${NC}"
echo ""

# List recent backups
echo "Recent backups:"
ls -lh $BACKUP_DIR | tail -5

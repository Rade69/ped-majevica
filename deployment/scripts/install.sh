#!/bin/bash
#
# PED Majevica VPS Installation Script
# Automatski instalira sve dependencies i postavlja server
#
# Usage: bash install.sh
#

set -e  # Exit on error

echo "============================================="
echo "  PED Majevica - VPS Setup"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Molimo pokrenite kao root: sudo bash install.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Running as root${NC}"
echo ""

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install essential packages
echo -e "${YELLOW}📦 Installing essential packages...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    htop \
    curl \
    wget

# Configure PostgreSQL
echo -e "${YELLOW}🗄️  Configuring PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE DATABASE ped_majevica;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER peduser WITH PASSWORD 'changeme123';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ped_majevica TO peduser;"

# Configure firewall
echo -e "${YELLOW}🔒 Configuring firewall...${NC}"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create app directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
mkdir -p /var/www/pedmajevica
chown -R $SUDO_USER:$SUDO_USER /var/www/pedmajevica

# Clone repository (will be done manually or via deploy script)
echo -e "${YELLOW}📥 Repository will be cloned via deploy.sh${NC}"

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  ✅ Installation Complete!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Clone your repository to /var/www/pedmajevica"
echo -e "  2. Run ${YELLOW}bash setup-app.sh${NC}"
echo -e "  3. Configure Nginx with ${YELLOW}bash setup-nginx.sh${NC}"
echo -e "  4. Setup SSL with ${YELLOW}bash setup-ssl.sh${NC}"
echo ""

#!/bin/bash
#
# Setup Nginx and Systemd Service
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root: sudo bash setup-nginx.sh${NC}"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${YELLOW}🔧 Setting up Nginx and Systemd...${NC}"

# Create log directories
echo -e "${YELLOW}📁 Creating log directories...${NC}"
mkdir -p /var/log/pedmajevica
chown www-data:www-data /var/log/pedmajevica

# Set correct permissions
echo -e "${YELLOW}🔒 Setting permissions...${NC}"
chown -R www-data:www-data /var/www/pedmajevica

# Copy systemd service
echo -e "${YELLOW}⚙️  Installing systemd service...${NC}"
cp $SCRIPT_DIR/pedmajevica.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pedmajevica
systemctl start pedmajevica
systemctl status pedmajevica --no-pager

# Copy Nginx configuration
echo -e "${YELLOW}🌐 Installing Nginx configuration...${NC}"
cp $SCRIPT_DIR/nginx-pedmajevica.conf /etc/nginx/sites-available/pedmajevica
ln -sf /etc/nginx/sites-available/pedmajevica /etc/nginx/sites-enabled/

# Remove default Nginx site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${YELLOW}🧪 Testing Nginx configuration...${NC}"
nginx -t

# Restart Nginx
echo -e "${YELLOW}🔄 Restarting Nginx...${NC}"
systemctl restart nginx

echo ""
echo -e "${GREEN}✅ Nginx and Systemd setup complete!${NC}"
echo ""
echo "Next step: Setup SSL with 'sudo bash setup-ssl.sh'"
echo ""

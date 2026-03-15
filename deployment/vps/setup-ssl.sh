#!/bin/bash
#
# Setup SSL Certificate with Let's Encrypt
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root: sudo bash setup-ssl.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
echo ""

# Prompt for email
read -p "Enter your email for Let's Encrypt notifications: " EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${RED}❌ Email is required${NC}"
    exit 1
fi

# Obtain SSL certificate
echo -e "${YELLOW}📜 Obtaining SSL certificate...${NC}"
certbot --nginx -d pedmajevica.org -d www.pedmajevica.org --non-interactive --agree-tos -m $EMAIL

# Test auto-renewal
echo -e "${YELLOW}🧪 Testing auto-renewal...${NC}"
certbot renew --dry-run

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  ✅ SSL Certificate Installed!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo "Your site is now available at:"
echo -e "${GREEN}  https://pedmajevica.org${NC}"
echo ""
echo "Certificate will auto-renew via cron job."
echo ""

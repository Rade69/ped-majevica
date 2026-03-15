#!/bin/bash
#
# Deploy/Update Application
# Povlači najnoviji kod sa GitHub-a i restartuje aplikaciju
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/var/www/pedmajevica"

echo -e "${YELLOW}🚀 Deploying application update...${NC}"

# Navigate to app directory
cd $APP_DIR

# Pull latest code
echo -e "${YELLOW}📥 Pulling latest code from GitHub...${NC}"
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Update Python dependencies
echo -e "${YELLOW}📦 Updating Python dependencies...${NC}"
cd backend
pip install -r requirements.txt --upgrade

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
export FLASK_APP=wsgi.py
flask db upgrade

# Build frontend
echo -e "${YELLOW}🎨 Building frontend CSS...${NC}"
cd $APP_DIR
npm install
npm run build

# Restart application
echo -e "${YELLOW}🔄 Restarting application...${NC}"
sudo systemctl restart pedmajevica

# Check status
echo -e "${YELLOW}📊 Checking application status...${NC}"
sudo systemctl status pedmajevica --no-pager

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

#!/bin/bash
#
# Setup Flask Application
# Instalira Python dependencies i konfiguruje aplikaciju
#
# Usage: bash setup-app.sh
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/var/www/pedmajevica"
VENV_DIR="$APP_DIR/venv"

echo -e "${YELLOW}🚀 Setting up Flask application...${NC}"

# Navigate to app directory
cd $APP_DIR

# Create virtual environment
echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
python3 -m venv $VENV_DIR

# Activate virtual environment
source $VENV_DIR/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt

# Create .env file
echo -e "${YELLOW}⚙️  Creating .env configuration...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
# Production Environment Variables
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=postgresql://peduser:changeme123@localhost:5432/ped_majevica
LOG_LEVEL=INFO
ENVEOF
    
    # Generate random SECRET_KEY
    SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env
    
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}⚠️  .env already exists, skipping...${NC}"
fi

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
export FLASK_APP=wsgi.py
flask db upgrade

# Import initial data (optional)
read -p "Do you want to import initial data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python migrate_json_to_db.py || echo "No initial data script found"
fi

# Build frontend CSS
echo -e "${YELLOW}🎨 Building frontend CSS...${NC}"
cd $APP_DIR
npm install
npm run build

echo ""
echo -e "${GREEN}✅ Application setup complete!${NC}"
echo ""

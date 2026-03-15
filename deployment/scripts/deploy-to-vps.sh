#!/bin/bash
# ========================================
# PED Majevica 1988 - Deploy Script
# ========================================
# Automated deployment script for VPS
#
# Usage:
#   ./deploy-to-vps.sh <VPS_IP> <USERNAME>
#
# Example:
#   ./deploy-to-vps.sh 123.45.67.89 pedadmin
#
# ========================================

set -e  # Exit on error

# -----------------------------
# Configuration
# -----------------------------
VPS_IP="${1:-}"
VPS_USER="${2:-pedadmin}"
APP_DIR="/var/www/ped-majevica"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------
# Functions
# -----------------------------
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if VPS IP is provided
    if [ -z "$VPS_IP" ]; then
        print_error "VPS IP address is required"
        echo "Usage: $0 <VPS_IP> <USERNAME>"
        exit 1
    fi
    
    # Check if SSH is available
    if ! command -v ssh &> /dev/null; then
        print_error "SSH is not installed"
        exit 1
    fi
    
    # Check if rsync is available
    if ! command -v rsync &> /dev/null; then
        print_error "rsync is not installed"
        exit 1
    fi
    
    # Test SSH connection
    print_warning "Testing SSH connection to $VPS_IP..."
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$VPS_USER@$VPS_IP" "echo 'Connection successful'" &> /dev/null; then
        print_error "Cannot connect to VPS via SSH"
        print_warning "Make sure:"
        echo "  1. VPS is running"
        echo "  2. SSH key is configured"
        echo "  3. User '$VPS_USER' exists on VPS"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

deploy_backend() {
    print_header "Deploying Backend"
    
    # Create remote directory
    ssh "$VPS_USER@$VPS_IP" "mkdir -p $APP_DIR/backend"
    
    # Sync backend files
    print_warning "Syncing backend files..."
    rsync -avz --delete \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='instance' \
        --exclude='logs' \
        --exclude='.env' \
        --exclude='.git' \
        "$PROJECT_ROOT/backend/" "$VPS_USER@$VPS_IP:$APP_DIR/backend/"
    
    print_success "Backend files deployed"
}

deploy_frontend() {
    print_header "Deploying Frontend"
    
    # Create remote directory
    ssh "$VPS_USER@$VPS_IP" "mkdir -p $APP_DIR/frontend"
    
    # Build frontend first
    print_warning "Building frontend..."
    cd "$PROJECT_ROOT/frontend"
    npm install --production
    npm run build
    
    # Sync frontend files
    print_warning "Syncing frontend files..."
    rsync -avz --delete \
        --exclude='node_modules' \
        --exclude='package-lock.json' \
        "$PROJECT_ROOT/frontend/" "$VPS_USER@$VPS_IP:$APP_DIR/frontend/"
    
    print_success "Frontend files deployed"
}

setup_remote_permissions() {
    print_header "Setting Remote Permissions"
    
    ssh "$VPS_USER@$VPS_IP" << 'ENDSSH'
# Set ownership
sudo chown -R pedadmin:pedadmin /var/www/ped-majevica

# Set permissions
chmod -R 755 /var/www/ped-majevica
chmod 600 /var/www/ped-majevica/backend/.env 2>/dev/null || true

# Create necessary directories
sudo mkdir -p /var/log/pedmajevica
sudo chown pedadmin:pedadmin /var/log/pedmajevica

sudo mkdir -p /var/www/ped-majevica/backend/uploads
sudo chown pedadmin:pedadmin /var/www/ped-majevica/backend/uploads

echo "Permissions set successfully"
ENDSSH
    
    print_success "Remote permissions configured"
}

restart_services() {
    print_header "Restarting Services"
    
    ssh "$VPS_USER@$VPS_IP" << 'ENDSSH'
cd /var/www/ped-majevica/backend

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt --quiet

# Run database migrations
flask db upgrade --quiet

# Restart Gunicorn
sudo systemctl restart pedmajevica

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx

echo "Services restarted successfully"
ENDSSH
    
    print_success "Services restarted"
}

verify_deployment() {
    print_header "Verifying Deployment"
    
    # Get VPS IP for testing
    VPS_URL="https://$VPS_IP"
    
    print_warning "Waiting for services to start (10 seconds)..."
    sleep 10
    
    # Test HTTPS connection
    print_warning "Testing HTTPS connection..."
    if curl -k -s -o /dev/null -w "%{http_code}" "https://$VPS_IP" | grep -q "200\|302"; then
        print_success "Application is responding"
    else
        print_error "Application is not responding"
        print_warning "Check logs: ssh $VPS_USER@$VPS_IP"
        echo "  sudo journalctl -u pedmajevica -n 50"
        echo "  sudo tail -f /var/log/nginx/pedmajevica-error.log"
    fi
}

# -----------------------------
# Main Deployment
# -----------------------------
main() {
    print_header "PED Majevica - VPS Deployment"
    echo "VPS IP: $VPS_IP"
    echo "User: $VPS_USER"
    echo "Project: $PROJECT_ROOT"
    echo ""
    
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    check_prerequisites
    deploy_backend
    deploy_frontend
    setup_remote_permissions
    restart_services
    verify_deployment
    
    print_header "Deployment Complete!"
    print_success "Application deployed to: https://$VPS_IP"
    print_warning "Next steps:"
    echo "  1. Configure domain DNS (pedmajevica.org -> $VPS_IP)"
    echo "  2. Install SSL certificate: certbot --nginx"
    echo "  3. Test all functionality"
    echo ""
}

# Run main function
main

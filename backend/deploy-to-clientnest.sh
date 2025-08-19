#!/bin/bash

# Deployment script for clientnest.xyz
set -e

echo "🚀 Starting deployment to clientnest.xyz..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/clientnest"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$BACKEND_DIR/venv"
SERVICE_NAME="clientnest-backend"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update code from git
print_status "Updating code from git..."
cd $BACKEND_DIR
git pull origin main

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Set production environment variables
export DJANGO_SETTINGS_MODULE=config.settings
export DJANGO_SECRET_KEY="o(6#7-g6rrr**)(e^oixs_rb$5-!#5=q63sm8@e)_)3ru4ftoq"
export DEBUG=False
export ALLOWED_HOSTS="clientnest.xyz,www.clientnest.xyz,api.clientnest.xyz"
export SECURE_SSL_REDIRECT=True
export SECURE_HSTS_SECONDS=31536000
export SECURE_HSTS_INCLUDE_SUBDOMAINS=True
export SECURE_HSTS_PRELOAD=True
export SESSION_COOKIE_SECURE=True
export CSRF_COOKIE_SECURE=True

# Run deployment checks
print_status "Running deployment checks..."
python manage.py check --deploy

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Restart the service
print_status "Restarting the service..."
sudo systemctl restart $SERVICE_NAME

# Check service status
print_status "Checking service status..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_status "Service is running successfully!"
else
    print_error "Service failed to start. Check logs with: sudo journalctl -u $SERVICE_NAME -f"
    exit 1
fi

# Test the API
print_status "Testing API health endpoint..."
if curl -f -s https://api.clientnest.xyz/api/health/ > /dev/null; then
    print_status "API is responding correctly!"
else
    print_warning "API health check failed. The service might still be starting up."
fi

print_status "Deployment completed successfully! 🎉"
print_status "Your API is now available at: https://api.clientnest.xyz" 
# ClientNest Backend Deployment Guide

This guide will help you deploy the ClientNest backend to the `clientnest.xyz` domain.

## Prerequisites

- Ubuntu 20.04+ server
- Domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL database
- Nginx web server

## Server Setup

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server
```

### 2. Create Project Directory

```bash
sudo mkdir -p /var/www/clientnest
sudo chown $USER:$USER /var/www/clientnest
```

### 3. Clone Repository

```bash
cd /var/www/clientnest
git clone <your-repo-url> .
```

### 4. Setup Python Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure Database

```bash
sudo -u postgres createdb clientnest
sudo -u postgres createuser clientnest_user
sudo -u postgres psql -c "ALTER USER clientnest_user PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE clientnest TO clientnest_user;"
```

### 6. Setup Environment Variables

Copy the production environment file:
```bash
cp env.production .env
```

Edit `.env` with your actual values:
- Database credentials
- Email settings
- API keys
- Domain settings

### 7. Run Initial Setup

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## SSL Certificate Setup

### Using Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d clientnest.xyz -d www.clientnest.xyz -d api.clientnest.xyz
```

## Nginx Configuration

### 1. Copy Nginx Config

```bash
sudo cp nginx-clientnest.conf /etc/nginx/sites-available/clientnest
sudo ln -s /etc/nginx/sites-available/clientnest /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
```

### 2. Test and Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Systemd Service Setup

### 1. Copy Service File

```bash
sudo cp clientnest-backend.service /etc/systemd/system/
```

### 2. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable clientnest-backend
sudo systemctl start clientnest-backend
```

## Deployment

### Using the Deployment Script

```bash
chmod +x deploy-to-clientnest.sh
./deploy-to-clientnest.sh
```

### Manual Deployment

```bash
cd /var/www/clientnest/backend
source venv/bin/activate

# Set production environment
export DJANGO_SETTINGS_MODULE=config.settings
export DEBUG=False
export ALLOWED_HOSTS="clientnest.xyz,www.clientnest.xyz,api.clientnest.xyz"

# Run deployment tasks
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart clientnest-backend
```

## API Endpoints

Once deployed, your API will be available at:

- **Health Check**: `https://api.clientnest.xyz/api/health/`
- **Authentication**: `https://api.clientnest.xyz/api/auth/`
- **User Management**: `https://api.clientnest.xyz/api/users/`
- **Content Management**: `https://api.clientnest.xyz/api/content/`
- **Social Media**: `https://api.clientnest.xyz/api/social/`
- **Admin Interface**: `https://api.clientnest.xyz/admin/`

## Monitoring

### Check Service Status

```bash
sudo systemctl status clientnest-backend
```

### View Logs

```bash
sudo journalctl -u clientnest-backend -f
```

### Check Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Security Checklist

- [ ] SSL certificate installed and working
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY set
- [ ] Database credentials secured
- [ ] Firewall configured
- [ ] Regular backups scheduled
- [ ] Security updates enabled

## Troubleshooting

### Common Issues

1. **Service won't start**: Check logs with `sudo journalctl -u clientnest-backend -f`
2. **Database connection errors**: Verify PostgreSQL is running and credentials are correct
3. **Static files not loading**: Run `python manage.py collectstatic --noinput`
4. **SSL certificate issues**: Check with `sudo certbot certificates`

### Health Check

Test your deployment:
```bash
curl -f https://api.clientnest.xyz/api/health/
```

Expected response:
```json
{"status": "healthy", "service": "clientnest-backend"}
```

## Backup Strategy

### Database Backup

```bash
pg_dump clientnest > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Code Backup

```bash
tar -czf clientnest_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/clientnest
```

## Updates

To update the application:

1. Pull latest code: `git pull origin main`
2. Update dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic --noinput`
5. Restart service: `sudo systemctl restart clientnest-backend`

Or simply run the deployment script: `./deploy-to-clientnest.sh`

## SSH into your server
ssh -i your-key.pem ubuntu@13.247.190.204

# Then follow the deployment steps:
cd /var/www/clientnest/backend
./deploy-to-clientnest.sh 
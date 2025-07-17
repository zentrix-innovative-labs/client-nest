#!/usr/bin/env python
"""
Deployment script for clientnest.xyz
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_production_environment():
    """Setup production environment variables"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Production environment variables
    production_env = {
        'DJANGO_SECRET_KEY': 'o(6#7-g6rrr**)(e^oixs_rb$5-!#5=q63sm8@e)_)3ru4ftoq',
        'DEBUG': 'False',
        'ALLOWED_HOSTS': 'clientnest.xyz,www.clientnest.xyz,api.clientnest.xyz',
        'SECURE_SSL_REDIRECT': 'True',
        'SECURE_HSTS_SECONDS': '31536000',
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': 'True',
        'SECURE_HSTS_PRELOAD': 'True',
        'SESSION_COOKIE_SECURE': 'True',
        'CSRF_COOKIE_SECURE': 'True',
    }
    
    for key, value in production_env.items():
        os.environ[key] = value

def run_deployment_checks():
    """Run deployment checks"""
    print("Running deployment checks...")
    
    # Check for deployment issues
    execute_from_command_line(['manage.py', 'check', '--deploy'])
    
    # Collect static files
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Run migrations
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])

if __name__ == '__main__':
    setup_production_environment()
    run_deployment_checks() 
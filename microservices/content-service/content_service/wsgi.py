import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the 'content-service' microservice
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_service.settings')

# Get the WSGI application for the content service
application = get_wsgi_application()
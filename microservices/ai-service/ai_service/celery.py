import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')
 
app = Celery('ai_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 
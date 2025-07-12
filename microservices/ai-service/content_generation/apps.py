# microservices/ai-service/content_generation/apps.py
from django.apps import AppConfig

class ContentGenerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content_generation'

    def ready(self):
        # Import signal handlers to ensure they are connected
        from . import signals 
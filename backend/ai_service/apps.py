from django.apps import AppConfig


class AIServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_service'
    label = 'ai_integration'

    def ready(self):
        # Import signal handlers to ensure they are connected
        from . import signals

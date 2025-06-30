from django.apps import AppConfig


class AiIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.ai_integration'
    label = 'backend_ai_integration'

    def ready(self):
        # Import signal handlers to ensure they are connected
        from . import signals

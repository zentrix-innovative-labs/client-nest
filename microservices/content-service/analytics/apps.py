from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """Analytics app configuration.
    
    Handles analytics data collection, processing, and reporting
    for content performance across social media platforms.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Analytics'
    
    def ready(self):
        """Import signals when the app is ready."""
        import analytics.signals
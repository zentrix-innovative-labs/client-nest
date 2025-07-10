from django.apps import AppConfig

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'
    verbose_name = 'Posts Management'
    
    def ready(self):
        """Import signals when the app is ready"""
        import posts.signals
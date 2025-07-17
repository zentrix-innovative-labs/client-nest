import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set the default Django settings module for the 'content-service' microservice
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_service.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import routing after Django is set up
# from . import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket routing can be added here when needed
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(
    #         URLRouter([
    #             # WebSocket URL patterns will go here
    #         ])
    #     )
    # ),
})
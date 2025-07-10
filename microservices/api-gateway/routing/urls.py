from django.urls import path, re_path
from . import views

app_name = 'routing'

urlpatterns = [
    # Service discovery endpoint
    path('discovery/', views.service_discovery, name='service_discovery'),
    
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
    # Admin endpoints
    path('reload/', views.reload_routes, name='reload_routes'),
    
    # Catch-all route for forwarding requests to microservices
    # This should be the last pattern as it catches everything
    re_path(r'^(?P<path>.*)$', views.route_request, name='route_request'),
]
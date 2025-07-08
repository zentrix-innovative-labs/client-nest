from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Client Nest User Service API",
        default_version='v1',
        description="User Management Microservice for Client Nest Platform",
        terms_of_service="https://www.clientnest.xyz/terms/",
        contact=openapi.Contact(email="api@clientnest.xyz"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

@api_view(['GET'])
def health_check(request):
    """Health check endpoint for the user service"""
    return Response({
        'status': 'healthy',
        'service': 'user-service',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected',
        'cache': 'connected'
    })

def service_info(request):
    """Service information endpoint"""
    return JsonResponse({
        'name': 'user-service',
        'version': '1.0.0',
        'description': 'User Management Microservice',
        'endpoints': {
            'health': '/health/',
            'docs': '/swagger/',
            'api': '/api/v1/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    path('', service_info, name='service_info'),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API endpoints
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/profiles/', include('profiles.urls')),
    
    # Password reset
    path('api/v1/password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
    # Social authentication
    path('auth/', include('social_django.urls', namespace='social')),
    
    # Health checks
    path('health-check/', include('health_check.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
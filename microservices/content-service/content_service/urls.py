from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import HealthCheckView, ServiceInfoView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('info/', ServiceInfoView.as_view(), name='service-info'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 Endpoints
    path('api/v1/posts/', include('posts.urls')),
    path('api/v1/media/', include('media.urls')),
    path('api/v1/templates/', include('templates.urls')),
    path('api/v1/scheduling/', include('scheduling.urls')),
    path('api/v1/analytics/', include('content_analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'ClientNest Content Service Admin'
admin.site.site_title = 'Content Service Admin'
admin.site.index_title = 'Content Management Administration'
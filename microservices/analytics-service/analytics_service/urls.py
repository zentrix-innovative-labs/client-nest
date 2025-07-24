from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from .views import DashboardView, EngagementView, AudienceView, CustomReportView, InsightsView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os
from pathlib import Path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

BASE_DIR = Path(__file__).resolve().parent.parent

schema_view = get_schema_view(
   openapi.Info(
      title="Analytics Service API",
      default_version='v1',
      description="API documentation for Analytics Service",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

def health_check(request):
    """Health check endpoint for service monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'analytics-service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('dashboard/', DashboardView.as_view(), name='analytics-dashboard'),
    path('engagement/', EngagementView.as_view(), name='analytics-engagement'),
    path('audience/', AudienceView.as_view(), name='analytics-audience'),
    path('custom-report/', CustomReportView.as_view(), name='analytics-custom-report'),
    path('insights/', InsightsView.as_view(), name='analytics-insights'),
    path('api/v1/analytics/performance/', include('performance.urls')),
    path('api/v1/analytics/ai-usage/', include('ai_usage.urls')),
    path('api/v1/analytics/reports/', include('reports.urls')),
    path('api/v1/analytics/metrics/', include('metrics.urls')),
]

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
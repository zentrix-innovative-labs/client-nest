from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

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
    path('api/v1/analytics/performance/', include('performance.urls')),
    path('api/v1/analytics/ai-usage/', include('ai_usage.urls')),
    path('api/v1/analytics/reports/', include('reports.urls')),
    path('api/v1/analytics/metrics/', include('metrics.urls')),
]
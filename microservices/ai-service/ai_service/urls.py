from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for service monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'ai-service',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/v1/ai/content-generation/', include('content_generation.urls')),
    path('api/v1/ai/sentiment-analysis/', include('sentiment_analysis.urls')),
    path('api/v1/ai/content-optimization/', include('content_optimization.urls')),
    path('api/v1/ai/models/', include('ai_models.urls')),
]
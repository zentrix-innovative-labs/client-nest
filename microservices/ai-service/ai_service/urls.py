from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from .views import (
    ContentGenerationView,
    SentimentAnalysisView,
    HashtagOptimizationView,
    OptimalPostingTimeView,
    ModelHealthView,
    UsageStatsView,
    TokenUsageView,
)

def health_check(request):
    """Health check endpoint for service monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'ai-service',
        'version': '1.0.0',
        'port': settings.SERVICE_PORT
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    
    # AI Service Core Endpoints (Port 8005)
    path('api/ai/generate/content/', ContentGenerationView.as_view(), name='ai-generate-content'),
    path('api/ai/analyze/sentiment/', SentimentAnalysisView.as_view(), name='ai-analyze-sentiment'),
    path('api/ai/optimize/hashtags/', HashtagOptimizationView.as_view(), name='ai-optimize-hashtags'),
    path('api/ai/schedule/optimal/', OptimalPostingTimeView.as_view(), name='ai-optimal-posting-time'),
    path('api/ai/models/status/', ModelHealthView.as_view(), name='ai-models-status'),
    path('api/ai/usage/stats/', UsageStatsView.as_view(), name='ai-usage-stats'),
    path('api/ai/token/usage/', TokenUsageView.as_view(), name='ai-token-usage'),
    
    # Include content generation URLs for backward compatibility
    path('api/ai/', include('content_generation.urls')),
]
"""
URL patterns for AI integration functionality.
"""

from django.urls import path
from . import views

app_name = 'ai_integration'

urlpatterns = [
    # AI content generation endpoint
    path('generate/', views.AIContentGenerationView.as_view(), name='generate_content'),
    
    # AI service health check
    path('health/', views.ai_health_check, name='health_check'),
    
    # AI usage statistics
    path('usage/', views.ai_usage_stats, name='usage_stats'),
] 
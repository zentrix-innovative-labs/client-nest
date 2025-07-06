"""
URL patterns for AI analytics functionality.
"""

from django.urls import path
from . import post_optimization

app_name = 'ai_analytics'

urlpatterns = [
    # Post timing optimization endpoint
    path('post-timing/', post_optimization.post_timing_optimization, name='post_timing_optimization'),
] 
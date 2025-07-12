# microservices/ai-service/content_generation/urls.py
from django.urls import path
from .views import (
    ContentGenerationAPIView,
    ContentGenerationTestAPIView,
    GeneratedContentListView,
    GeneratedContentDetailView,
    ContentTemplateListView,
    AIUsageLogListView
)

app_name = 'content_generation'

urlpatterns = [
    # Content generation endpoints
    path('generate/', ContentGenerationAPIView.as_view(), name='generate-content'),
    path('generate/test/', ContentGenerationTestAPIView.as_view(), name='generate-content-test'),
    path('content/', GeneratedContentListView.as_view(), name='content-list'),
    path('content/<int:content_id>/', GeneratedContentDetailView.as_view(), name='content-detail'),
    
    # Template management
    path('templates/', ContentTemplateListView.as_view(), name='template-list'),
    
    # Usage tracking
    path('usage/', AIUsageLogListView.as_view(), name='usage-logs'),
] 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AITaskViewSet, ContentGenerationViewSet, SentimentAnalysisViewSet, ContentOptimizationViewSet

router = DefaultRouter()
router.register(r'tasks', AITaskViewSet, basename='ai-task')
router.register(r'content', ContentGenerationViewSet, basename='content-generation')
router.register(r'sentiment', SentimentAnalysisViewSet, basename='sentiment-analysis')
router.register(r'optimization', ContentOptimizationViewSet, basename='content-optimization')

urlpatterns = [
    path('', include(router.urls)),
]

# API Endpoints:
#
# AI Tasks:
# - GET /api/ai/tasks/ - List all AI tasks for current user
# - GET /api/ai/tasks/{id}/ - Get specific AI task details
# - GET /api/ai/tasks/usage-stats/ - Get usage statistics
#
# Content Generation:
# - POST /api/ai/content/ - Generate content (generic endpoint)
# - POST /api/ai/content/generate-post/ - Generate social media post
# - POST /api/ai/content/generate-caption/ - Generate image caption
# - POST /api/ai/content/generate-hashtags/ - Generate hashtags
#
# Sentiment Analysis:
# - POST /api/ai/sentiment/ - Analyze sentiment (generic endpoint)
# - POST /api/ai/sentiment/analyze-comment/ - Analyze comment sentiment
# - POST /api/ai/sentiment/analyze-feedback/ - Analyze feedback sentiment
# - POST /api/ai/sentiment/analyze_comment/ - Analyze comment sentiment
# - POST /api/ai/sentiment/analyze_feedback/ - Analyze feedback sentiment
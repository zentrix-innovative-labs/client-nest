from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import AITask
from .tasks import process_content_generation, process_sentiment_analysis
from .serializers import AITaskSerializer, ContentGenerationSerializer, SentimentAnalysisSerializer
from .exceptions import (
    AIRateLimitError,
    AIServiceUnavailableError,
    AIQuotaExceededError,
    AIValidationError,
    AIContentFilterError
)
from .utils import get_usage_stats
import logging

logger = logging.getLogger('ai.views')

class AITaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving AI task history"""
    serializer_class = AITaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AITask.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Get AI usage statistics for the current user"""
        stats = get_usage_stats(request.user.id)
        return Response(stats)

class ContentGenerationViewSet(viewsets.ViewSet):
    """ViewSet for content generation endpoints"""
    permission_classes = [IsAuthenticated]
    serializer_class = ContentGenerationSerializer

    async def create(self, request):
        """Generate content using AI"""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            task = await process_content_generation.delay(
                user_id=request.user.id,
                user_tier=request.user.subscription_tier,
                **serializer.validated_data
            )

            return Response({
                'task_id': task.id,
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except AIQuotaExceededError as e:
            return Response({'error': str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except AIRateLimitError as e:
            return Response({'error': str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except AIContentFilterError as e:
            return Response({'error': str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except AIServiceUnavailableError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f'Content generation error: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    async def generate_post(self, request):
        """Generate social media post"""
        request.data['content_type'] = 'post'
        return await self.create(request)

    @action(detail=False, methods=['post'])
    async def generate_caption(self, request):
        """Generate image caption"""
        request.data['content_type'] = 'caption'
        return await self.create(request)

    @action(detail=False, methods=['post'])
    async def generate_hashtags(self, request):
        """Generate relevant hashtags"""
        request.data['content_type'] = 'hashtag'
        return await self.create(request)

class SentimentAnalysisViewSet(viewsets.ViewSet):
    """ViewSet for sentiment analysis endpoints"""
    permission_classes = [IsAuthenticated]
    serializer_class = SentimentAnalysisSerializer

    async def create(self, request):
        """Analyze sentiment of text"""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            task = await process_sentiment_analysis.delay(
                user_id=request.user.id,
                user_tier=request.user.subscription_tier,
                **serializer.validated_data
            )

            return Response({
                'task_id': task.id,
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except AIQuotaExceededError as e:
            return Response({'error': str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except AIRateLimitError as e:
            return Response({'error': str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except AIServiceUnavailableError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f'Sentiment analysis error: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    async def analyze_comment(self, request):
        """Analyze comment sentiment"""
        request.data['context'] = 'comment'
        return await self.create(request)

    @action(detail=False, methods=['post'])
    async def analyze_feedback(self, request):
        """Analyze customer feedback sentiment"""
        request.data['context'] = 'feedback'
        return await self.create(request)

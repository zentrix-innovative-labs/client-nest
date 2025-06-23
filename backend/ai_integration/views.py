from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions as drf_exceptions
from django.core.exceptions import ValidationError
from .models import AITask
from .tasks import process_content_generation, process_sentiment_analysis, process_content_optimization
from .serializers import AITaskSerializer, ContentGenerationSerializer, SentimentAnalysisSerializer, ContentOptimizationSerializer
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

    @action(detail=False, methods=['get'], url_path='usage-stats')
    def usage_stats(self, request):
        """Get AI usage statistics for the current user"""
        stats = get_usage_stats(request.user.id)
        return Response(stats)

class ContentGenerationViewSet(viewsets.ViewSet):
    """ViewSet for content generation endpoints"""
    permission_classes = [IsAuthenticated]
    serializer_class = ContentGenerationSerializer

    def create(self, request):
        """Generate content using AI"""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            task = process_content_generation.delay(
                user_id=request.user.id,
                user_tier=request.user.subscription_tier,
                **serializer.validated_data
            )

            return Response({
                'task_id': task.id,
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)

        except (ValidationError, drf_exceptions.ValidationError) as e:
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

    @action(detail=False, methods=['post'], url_path='generate-post')
    def generate_post(self, request):
        request.data['content_type'] = 'post'
        return self.create(request)

    @action(detail=False, methods=['post'], url_path='generate-caption')
    def generate_caption(self, request):
        request.data['content_type'] = 'caption'
        return self.create(request)

    @action(detail=False, methods=['post'], url_path='generate-hashtags')
    def generate_hashtags(self, request):
        request.data['content_type'] = 'hashtag'
        return self.create(request)

class SentimentAnalysisViewSet(viewsets.ViewSet):
    """ViewSet for sentiment analysis endpoints"""
    permission_classes = [IsAuthenticated]
    serializer_class = SentimentAnalysisSerializer

    def create(self, request):
        """Analyze sentiment of text"""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            task = process_sentiment_analysis.delay(
                user_id=request.user.id,
                user_tier=request.user.subscription_tier,
                **serializer.validated_data
            )

            return Response({
                'task_id': task.id,
                'status': 'processing'
            }, status=status.HTTP_202_ACCEPTED)

        except (ValidationError, drf_exceptions.ValidationError) as e:
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
    def analyze_comment(self, request):
        request.data['context'] = 'comment'
        return self.create(request)

    @action(detail=False, methods=['post'])
    def analyze_feedback(self, request):
        request.data['context'] = 'feedback'
        return self.create(request)

class ContentOptimizationViewSet(viewsets.ViewSet):
    """ViewSet for content optimization endpoints"""
    permission_classes = [IsAuthenticated]
    serializer_class = ContentOptimizationSerializer

    def create(self, request):
        """Optimize content using AI"""
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            task = process_content_optimization.delay(
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
            logger.error(f'Content optimization error: {str(e)}')
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """Optimize content for engagement, reach, etc."""
        return self.create(request)

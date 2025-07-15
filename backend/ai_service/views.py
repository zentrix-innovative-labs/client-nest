"""
Django views for AI integration functionality.
Provides secure endpoints for AI content generation and management.
"""

import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json
import sys
import os

# Add the ai_services path to sys.path for imports
ai_services_path = os.path.join(settings.BASE_DIR, '..', 'ai_services')
if ai_services_path not in sys.path:
    sys.path.insert(0, ai_services_path)

from ai_services.common.deepseek_client import DeepSeekClient, AIClientError, AIAPIError, AIConnectionError
from celery.result import AsyncResult
# Removed unused imports: content_serviceGenerationRequestSerializer, ContentGenerationResponseSerializer
from .tasks import generate_content_task
from .models import UserTaskMapping
import logging
from django.db import DatabaseError

logger = logging.getLogger(__name__)


class AIContentGenerationView(APIView):
    """
    Secure API view for AI content generation.
    Requires authentication and validates input parameters.
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = None
        try:
            self.client = DeepSeekClient()
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
    
    def post(self, request):
        """
        Generate AI content with proper validation and error handling.
        """
        try:
            # Validate required fields
            required_fields = ['system_prompt', 'user_prompt']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Extract and validate parameters
            system_prompt = request.data.get('system_prompt', '').strip()
            user_prompt = request.data.get('user_prompt', '').strip()
            
            if not system_prompt or not user_prompt:
                return Response(
                    {'error': 'System prompt and user prompt cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate prompt lengths
            if len(system_prompt) > 2000:
                return Response(
                    {'error': 'System prompt too long (max 2000 characters)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(user_prompt) > 4000:
                return Response(
                    {'error': 'User prompt too long (max 4000 characters)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract optional parameters
            model = request.data.get('model', 'deepseek/deepseek-r1-0528:free')
            temperature = request.data.get('temperature', 0.8)
            max_tokens = request.data.get('max_tokens', 800)
            
            # Validate optional parameters
            if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
                return Response(
                    {'error': 'Temperature must be between 0 and 2'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(max_tokens, int) or not 1 <= max_tokens <= 4096:
                return Response(
                    {'error': 'Max tokens must be between 1 and 4096'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if client is available
            if not self.client:
                return Response(
                    {'error': 'AI service temporarily unavailable'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Generate content
            generated_content = self.client.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                user=request.user,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return Response({
                'success': True,
                'content': generated_content,
                'model': model,
                'parameters': {
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            }, status=status.HTTP_200_OK)
            
        except AIClientError as e:
            logger.error(f"AI client error: {e}")
            return Response(
                {'error': f'AI service error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except AIAPIError as e:
            logger.error(f"AI API error: {e}")
            return Response(
                {'error': f'AI API error: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY
            )
        except AIConnectionError as e:
            logger.error(f"AI connection error: {e}")
            return Response(
                {'error': f'AI connection error: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.error(f"Unexpected error in AI content generation: {e}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_health_check(request):
    """
    Health check endpoint for AI services.
    """
    try:
        client = DeepSeekClient()
        # Try a simple test request
        test_content = client.generate_content(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello, World!'",
            user=request.user,
            max_tokens=10
        )
        
        return Response({
            'status': 'healthy',
            'service': 'DeepSeek AI',
            'test_response': test_content
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return Response({
            'status': 'unhealthy',
            'service': 'DeepSeek AI',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_usage_stats(request):
    """
    Get AI usage statistics for the authenticated user.
    """
    try:
        from .models import AIUsageLog
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Get current month stats
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_stats = AIUsageLog.objects.filter(
            user=request.user,
            created_at__gte=start_of_month
        ).aggregate(
            total_requests=Count('id'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('cost'),
            avg_response_time=Sum('response_time_ms') / Count('id')
        )
        
        # Get stats by request type
        request_type_stats = AIUsageLog.objects.filter(
            user=request.user,
            created_at__gte=start_of_month
        ).values('request_type').annotate(
            count=Count('id'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('cost')
        )
        
        return Response({
            'monthly_stats': {
                'total_requests': monthly_stats['total_requests'] or 0,
                'total_tokens': monthly_stats['total_tokens'] or 0,
                'total_cost': float(monthly_stats['total_cost'] or 0),
                'avg_response_time_ms': monthly_stats['avg_response_time'] or 0
            },
            'request_types': list(request_type_stats),
            'period': {
                'start': start_of_month.isoformat(),
                'end': timezone.now().isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to get AI usage stats: {e}")
        return Response(
            {'error': 'Failed to retrieve usage statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

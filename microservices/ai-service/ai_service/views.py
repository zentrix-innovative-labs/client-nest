from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
import requests
import json
import logging
from .tasks import (
    generate_content_task,
    sentiment_analysis_task,
)
from celery.result import AsyncResult
from django_celery_results.models import TaskResult
from common.deepseek_client import DeepSeekClient
from content_generation.prompts import generate_hashtag_optimization_prompt, generate_optimal_posting_time_prompt

logger = logging.getLogger(__name__)

class ContentGenerationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        topic = request.data.get('topic')
        platform = request.data.get('platform', 'general')
        tone = request.data.get('tone', 'professional')
        batch = request.data.get('batch', False)
        if not topic:
            return Response({'error': 'Missing topic'}, status=status.HTTP_400_BAD_REQUEST)
        if batch:
            task = generate_content_task.apply_async(args=[topic, platform, tone], priority=5)
            return Response({'task_id': task.id, 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)
        try:
            result = generate_content_task(topic, platform, tone)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SentimentAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = request.data.get('text')
        batch = request.data.get('batch', False)
        if not text:
            return Response({'error': 'Missing text'}, status=status.HTTP_400_BAD_REQUEST)
        if batch:
            task = sentiment_analysis_task.apply_async(args=[text], priority=5)
            return Response({'task_id': task.id, 'status': 'queued'}, status=status.HTTP_202_ACCEPTED)
        try:
            result = sentiment_analysis_task(text)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HashtagOptimizationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Optimize hashtags for social media content
        """
        content = request.data.get('content')
        platform = request.data.get('platform', 'general')
        target_audience = request.data.get('target_audience', 'general')
        industry = request.data.get('industry', 'general')
        
        if not content:
            return Response({'error': 'Missing content'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = DeepSeekClient()
            
            # Create system and user prompts for hashtag optimization
            system_prompt = """You are a social media hashtag optimization expert. Analyze content and suggest optimal hashtags for maximum engagement."""
            
            user_prompt = generate_hashtag_optimization_prompt(content, platform, target_audience, industry)
            
            # Generate hashtag suggestions
            try:
                hashtag_data = client.generate_content(system_prompt, user_prompt)
                
                # Validate the response structure
                if not isinstance(hashtag_data, dict):
                    raise ValueError("Invalid response format")
                
                # Ensure required fields exist
                if 'hashtags' not in hashtag_data:
                    hashtag_data['hashtags'] = []
                if 'strategy' not in hashtag_data:
                    hashtag_data['strategy'] = {}
                if 'recommendations' not in hashtag_data:
                    hashtag_data['recommendations'] = []
                    
            except Exception as e:
                logger.warning(f"AI response parsing failed for hashtag optimization: {e}")
                # Fallback if response structure is unexpected
                hashtag_data = {
                    "hashtags": [
                        {"tag": "#content", "category": "general", "estimated_reach": "medium", "engagement_potential": "medium"}
                    ],
                    "strategy": {
                        "platform_specific": "Use platform-appropriate hashtags",
                        "audience_targeting": "Target relevant audience",
                        "trending_opportunities": "Monitor trending topics"
                    },
                    "recommendations": [
                        "Use a mix of popular and niche hashtags",
                        "Include industry-specific hashtags",
                        "Monitor trending hashtags regularly"
                    ]
                }
            
            # Calculate actual usage from client if available
            usage_data = getattr(client, 'last_usage', {})
            tokens_consumed = usage_data.get('total_tokens', 234)  # Fallback to estimate
            cost = (tokens_consumed / 1000) * 0.001  # Calculate based on actual tokens
            
            return Response({
                'success': True,
                'data': hashtag_data,
                'usage': {
                    'tokens_consumed': tokens_consumed,
                    'cost': round(cost, 4)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OptimalPostingTimeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Suggest optimal posting times for social media content
        """
        platform = request.data.get('platform', 'general')
        content_type = request.data.get('content_type', 'post')
        target_audience = request.data.get('target_audience', 'general')
        timezone = request.data.get('timezone', 'UTC')
        industry = request.data.get('industry', 'general')
        
        if not platform:
            return Response({'error': 'Missing platform'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = DeepSeekClient()
            
            # Create system and user prompts for optimal posting time analysis
            system_prompt = """You are a social media timing optimization expert. Analyze platforms and suggest optimal posting times for maximum engagement."""
            
            user_prompt = generate_optimal_posting_time_prompt(platform, content_type, target_audience, timezone, industry)
            
            # Generate optimal posting time suggestions
            try:
                timing_data = client.generate_content(system_prompt, user_prompt)
                
                # Validate the response structure
                if not isinstance(timing_data, dict):
                    raise ValueError("Invalid response format")
                
                # Ensure required fields exist
                if 'optimal_times' not in timing_data:
                    timing_data['optimal_times'] = {}
                if 'platform_strategy' not in timing_data:
                    timing_data['platform_strategy'] = {}
                if 'recommendations' not in timing_data:
                    timing_data['recommendations'] = []
                if 'timezone_considerations' not in timing_data:
                    timing_data['timezone_considerations'] = f"All times are in {timezone} timezone"
                    
            except Exception as e:
                logger.warning(f"AI response parsing failed for optimal posting time: {e}")
                # Fallback if response structure is unexpected
                timing_data = {
                    "optimal_times": {
                        "monday": ["09:00", "12:00", "18:00"],
                        "tuesday": ["09:00", "12:00", "18:00"],
                        "wednesday": ["09:00", "12:00", "18:00"],
                        "thursday": ["09:00", "12:00", "18:00"],
                        "friday": ["09:00", "12:00", "18:00"],
                        "saturday": ["10:00", "14:00", "19:00"],
                        "sunday": ["10:00", "14:00", "19:00"]
                    },
                    "platform_strategy": {
                        "best_days": ["monday", "wednesday", "friday"],
                        "best_hours": ["09:00-11:00", "12:00-14:00", "18:00-20:00"],
                        "audience_peak_times": "Peak engagement during business hours and evening",
                        "engagement_patterns": "Higher engagement on weekdays during business hours"
                    },
                    "recommendations": [
                        "Post during peak business hours (9 AM - 11 AM)",
                        "Engage during lunch hours (12 PM - 2 PM)",
                        "Post during evening hours (6 PM - 8 PM)",
                        "Avoid posting during weekends unless targeting specific audience"
                    ],
                    "timezone_considerations": f"All times are in {timezone} timezone"
                }
            
            # Calculate actual usage from client if available
            usage_data = getattr(client, 'last_usage', {})
            tokens_consumed = usage_data.get('total_tokens', 156)  # Fallback to estimate
            cost = (tokens_consumed / 1000) * 0.001  # Calculate based on actual tokens
            
            return Response({
                'success': True,
                'data': timing_data,
                'usage': {
                    'tokens_consumed': tokens_consumed,
                    'cost': round(cost, 4)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelHealthView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        # Real health check: ping DeepSeek API
        try:
            url = f"{settings.AI_MODELS['DEEPSEEK']['BASE_URL']}/v1/models"
            headers = {"Authorization": f"Bearer {settings.AI_MODELS['DEEPSEEK']['API_KEY']}"}
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            return Response({'status': 'healthy', 'models': r.json()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'unhealthy', 'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class UsageStatsView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        # Real usage/cost stats: aggregate from TaskResult or custom tracking
        total_tasks = TaskResult.objects.count()
        completed_tasks = TaskResult.objects.filter(status='SUCCESS').count()
        failed_tasks = TaskResult.objects.filter(status='FAILURE').count()
        # Cost tracking would require more logic, e.g., summing up cost fields if tracked
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
        }, status=status.HTTP_200_OK)

class TokenUsageView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        """Get current token usage and budget status"""
        try:
            client = DeepSeekClient()
            usage_stats = client.get_token_usage()
            
            # Add budget warnings
            warnings = []
            if usage_stats['daily_percentage'] > 0.8:
                warnings.append(f"Daily usage at {usage_stats['daily_percentage']:.1%}")
            if usage_stats['total_percentage'] > 0.8:
                warnings.append(f"Total budget at {usage_stats['total_percentage']:.1%}")
            
            response_data = {
                'token_usage': usage_stats,
                'budget_warnings': warnings,
                'remaining_daily': usage_stats['daily_limit'] - usage_stats['daily_usage'],
                'remaining_total': usage_stats['total_budget'] - usage_stats['total_usage'],
                'estimated_cost': (usage_stats['total_usage'] / 1000) * 0.001,  # Rough cost estimate
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
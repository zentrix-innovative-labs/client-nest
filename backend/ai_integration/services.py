import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .models import AIModel, AITask
from .exceptions import AIRateLimitError, AIServiceUnavailableError, AIAPIError, AITimeoutError

logger = logging.getLogger('ai.services')

class RateLimiter:
    """Rate limiter for AI API calls"""
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    async def acquire(self) -> bool:
        now = timezone.now()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True

class CircuitBreaker:
    """Circuit breaker for AI API calls"""
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def can_execute(self) -> bool:
        if self.state == 'closed':
            return True

        if self.state == 'open':
            if (timezone.now() - self.last_failure_time).seconds >= self.reset_timeout:
                self.state = 'half-open'
                return True
            return False

        return True  # half-open state

    def record_success(self):
        if self.state == 'half-open':
            self.state = 'closed'
        self.failures = 0

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = timezone.now()
        if self.failures >= self.failure_threshold:
            self.state = 'open'

class AIService:
    """Main AI service for handling AI tasks"""
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()

    async def process_content_generation(self, user_id: int, content_type: str,
                                       prompt: str, platform: str = 'general',
                                       **kwargs) -> Dict[str, Any]:
        """Process content generation request"""
        try:
            # Create AI task record
            model = await self._get_or_create_model('deepseek-chat', 'Content Generation Model')
            task = await self._create_task(model, user_id, {
                'type': 'content_generation',
                'content_type': content_type,
                'prompt': prompt,
                'platform': platform,
                **kwargs
            })

            # Check rate limits and circuit breaker
            if not await self.rate_limiter.acquire():
                raise AIRateLimitError('Rate limit exceeded')
            if not self.circuit_breaker.can_execute():
                raise AIServiceUnavailableError('Service temporarily unavailable')

            # Process the request
            async with DeepSeekClient() as client:
                result = await client.generate_content(
                    prompt=prompt,
                    content_type=content_type,
                    platform=platform,
                    **kwargs
                )

            # Update task with result
            await self._update_task_success(task, result)
            self.circuit_breaker.record_success()

            return result

        except Exception as e:
            self.circuit_breaker.record_failure()
            if isinstance(e, (AIRateLimitError, AIServiceUnavailableError, AIAPIError)):
                await self._update_task_failure(task, str(e))
                raise
            
            logger.error(f'Content generation error: {str(e)}')
            await self._update_task_failure(task, 'Internal processing error')
            raise AIServiceUnavailableError('Failed to process content generation request')

    async def process_sentiment_analysis(self, user_id: int, text: str,
                                       context: str = 'comment') -> Dict[str, Any]:
        """Process sentiment analysis request"""
        try:
            # Create AI task record
            model = await self._get_or_create_model('deepseek-chat', 'Sentiment Analysis Model')
            task = await self._create_task(model, user_id, {
                'type': 'sentiment_analysis',
                'text': text,
                'context': context
            })

            # Check rate limits and circuit breaker
            if not await self.rate_limiter.acquire():
                raise AIRateLimitError('Rate limit exceeded')
            if not self.circuit_breaker.can_execute():
                raise AIServiceUnavailableError('Service temporarily unavailable')

            # Process the request
            async with DeepSeekClient() as client:
                result = await client.analyze_sentiment(text, context)

            # Update task with result
            await self._update_task_success(task, result)
            self.circuit_breaker.record_success()

            return result

        except Exception as e:
            self.circuit_breaker.record_failure()
            if isinstance(e, (AIRateLimitError, AIServiceUnavailableError, AIAPIError)):
                await self._update_task_failure(task, str(e))
                raise
            
            logger.error(f'Sentiment analysis error: {str(e)}')
            await self._update_task_failure(task, 'Internal processing error')
            raise AIServiceUnavailableError('Failed to process sentiment analysis request')

    @staticmethod
    async def _get_or_create_model(name: str, description: str) -> AIModel:
        """Get or create AI model"""
        model, _ = await AIModel.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'version': '1.0'
            }
        )
        return model

    @staticmethod
    async def _create_task(model: AIModel, user_id: int, input_data: Dict) -> AITask:
        """Create new AI task"""
        return await AITask.objects.create(
            model=model,
            user_id=user_id,
            input_data=input_data,
            status='processing'
        )

    @staticmethod
    async def _update_task_success(task: AITask, output_data: Dict):
        """Update task with successful result"""
        task.output_data = output_data
        task.status = 'completed'
        await task.save()

    @staticmethod
    async def _update_task_failure(task: AITask, error: str):
        """Update task with failure result"""
        task.output_data = {'error': error}
        task.status = 'failed'
        await task.save()
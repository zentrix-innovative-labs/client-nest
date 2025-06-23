from celery import shared_task
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache
from .services import AIService
from .utils import (
    check_usage_limits,
    increment_usage_counters,
    calculate_token_cost,
    is_off_peak_hours,
    get_tier_limits
)
from .exceptions import (
    AIQuotaExceededError,
    AIContentFilterError,
    AIValidationError
)
import logging

logger = logging.getLogger('ai.tasks')

@shared_task(bind=True, max_retries=3)
def process_content_generation(self, user_id: int, user_tier: str,
                               content_type: str, prompt: str,
                               platform: str = 'general',
                               priority: str = 'normal',
                               **kwargs) -> Dict[str, Any]:
    """Celery task for processing content generation requests"""
    try:
        # Validate input
        if not prompt or len(prompt.strip()) == 0:
            raise AIValidationError('Empty prompt')

        # Check usage limits
        if not check_usage_limits(user_id, user_tier):
            raise AIQuotaExceededError(f'Usage limit exceeded for tier {user_tier}')

        # Calculate token cost
        token_cost = calculate_token_cost(prompt)
        tier_limits = get_tier_limits(user_tier)
        if token_cost > tier_limits['max_tokens']:
            raise AIValidationError(f'Prompt exceeds maximum token limit for tier {user_tier}')

        # Content filtering
        if _check_content_policy(prompt):
            raise AIContentFilterError('Content violates policy guidelines')

        # Process request
        ai_service = AIService()
        result = ai_service.process_content_generation(
            user_id=user_id,
            content_type=content_type,
            prompt=prompt,
            platform=platform,
            **kwargs
        )

        # Update usage counters
        increment_usage_counters(user_id)

        return result

    except (AIQuotaExceededError, AIContentFilterError, AIValidationError) as e:
        logger.warning(f'Content generation validation error: {str(e)}')
        raise

    except Exception as e:
        logger.error(f'Content generation error: {str(e)}')
        # Retry with exponential backoff
        retry_count = self.request.retries
        max_retries = self.max_retries
        
        if retry_count < max_retries:
            # Calculate delay with exponential backoff
            delay = (2 ** retry_count) * 60  # 60s, 120s, 240s
            raise self.retry(exc=e, countdown=delay)
        raise

@shared_task(bind=True, max_retries=3)
def process_sentiment_analysis(self, user_id: int, user_tier: str,
                               text: str, context: str = 'comment',
                               priority: str = 'normal') -> Dict[str, Any]:
    """Celery task for processing sentiment analysis requests"""
    try:
        # Validate input
        if not text or len(text.strip()) == 0:
            raise AIValidationError('Empty text')

        # Check usage limits
        if not check_usage_limits(user_id, user_tier):
            raise AIQuotaExceededError(f'Usage limit exceeded for tier {user_tier}')

        # Calculate token cost
        token_cost = calculate_token_cost(text)
        tier_limits = get_tier_limits(user_tier)
        if token_cost > tier_limits['max_tokens']:
            raise AIValidationError(f'Text exceeds maximum token limit for tier {user_tier}')

        # Process request
        ai_service = AIService()
        result = ai_service.process_sentiment_analysis(
            user_id=user_id,
            text=text,
            context=context
        )

        # Update usage counters
        increment_usage_counters(user_id)

        return result

    except (AIQuotaExceededError, AIValidationError) as e:
        logger.warning(f'Sentiment analysis validation error: {str(e)}')
        raise

    except Exception as e:
        logger.error(f'Sentiment analysis error: {str(e)}')
        # Retry with exponential backoff
        retry_count = self.request.retries
        max_retries = self.max_retries
        
        if retry_count < max_retries:
            delay = (2 ** retry_count) * 30  # 30s, 60s, 120s
            raise self.retry(exc=e, countdown=delay)
        raise

def cleanup_expired_tasks():
    """Periodic task to clean up expired AI tasks"""
    from .models import AITask
    from django.utils import timezone
    from datetime import timedelta

    # Delete failed tasks older than 7 days
    cutoff_date = timezone.now() - timedelta(days=7)
    AITask.objects.filter(
        status='failed',
        created_at__lt=cutoff_date
    ).delete()

    # Delete completed tasks older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    AITask.objects.filter(
        status='completed',
        created_at__lt=cutoff_date
    ).delete()

@shared_task(bind=True, max_retries=3)
def process_content_optimization(self, user_id: int, user_tier: str, content: str, platform: str, optimization_type: str = 'engagement', priority: str = 'normal') -> Dict[str, Any]:
    """Celery task for processing content optimization requests"""
    try:
        # Validate input
        if not content or len(content.strip()) == 0:
            raise AIValidationError('Empty content')

        # Check usage limits
        if not check_usage_limits(user_id, user_tier):
            raise AIQuotaExceededError(f'Usage limit exceeded for tier {user_tier}')

        # Calculate token cost
        token_cost = calculate_token_cost(content)
        tier_limits = get_tier_limits(user_tier)
        if token_cost > tier_limits['max_tokens']:
            raise AIValidationError(f'Content exceeds maximum token limit for tier {user_tier}')

        # Process request
        ai_service = AIService()
        result = ai_service.process_content_optimization(
            user_id=user_id,
            content=content,
            platform=platform,
            optimization_type=optimization_type
        )

        # Update usage counters
        increment_usage_counters(user_id)

        return result

    except (AIQuotaExceededError, AIValidationError) as e:
        logger.warning(f'Content optimization validation error: {str(e)}')
        raise

    except Exception as e:
        logger.error(f'Content optimization error: {str(e)}')
        # Retry with exponential backoff
        retry_count = self.request.retries
        max_retries = self.max_retries
        if retry_count < max_retries:
            delay = (2 ** retry_count) * 45  # 45s, 90s, 180s
            raise self.retry(exc=e, countdown=delay)
        raise

def _check_content_policy(text: str) -> bool:
    """Check if content violates policy guidelines"""
    # Implement content policy checking logic
    # This could include:
    # - Profanity detection
    # - Hate speech detection
    # - Adult content detection
    # - Spam detection
    # Returns True if content violates policy, False otherwise
    return False  # Placeholder implementation
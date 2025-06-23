from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import AITask, AIModel
import logging

logger = logging.getLogger('ai.signals')

@receiver(post_save, sender=AITask)
def handle_task_save(sender, instance, created, **kwargs):
    """Handle AI task save events"""
    try:
        # Update user's concurrent request count
        if created:
            concurrent_key = f'ai:concurrent:{instance.user.id}'
            if not cache.get(concurrent_key):
                cache.set(concurrent_key, 0)
            cache.incr(concurrent_key, 1)
            cache.expire(concurrent_key, 300)  # 5 minutes timeout

        # Update task completion metrics
        if instance.status == 'completed':
            # Decrement concurrent requests
            concurrent_key = f'ai:concurrent:{instance.user.id}'
            cache.decr(concurrent_key, 1)

            # Update success metrics
            success_key = f'ai:metrics:success:{instance.model.name}'
            cache.incr(success_key, 1)

        # Update failure metrics
        elif instance.status == 'failed':
            # Decrement concurrent requests
            concurrent_key = f'ai:concurrent:{instance.user.id}'
            cache.decr(concurrent_key, 1)

            # Update failure metrics
            failure_key = f'ai:metrics:failure:{instance.model.name}'
            cache.incr(failure_key, 1)

            # Log failure for monitoring
            logger.error(
                f'AI task failed - ID: {instance.id}, '
                f'Model: {instance.model.name}, '
                f'Error: {(instance.output_data.get("error", "Unknown error") if isinstance(instance.output_data, dict) else "Unknown error")}'
            )

    except Exception as e:
        logger.error(f'Error in handle_task_save signal: {str(e)}')

@receiver(post_delete, sender=AITask)
def handle_task_delete(sender, instance, **kwargs):
    """Handle AI task deletion events"""
    try:
        # Clean up any associated cache entries
        cache_keys = [
            f'ai:task:{instance.id}',
            f'ai:result:{instance.id}',
        ]
        cache.delete_many(cache_keys)

        # If task was in progress, decrement concurrent requests
        if instance.status == 'processing':
            concurrent_key = f'ai:concurrent:{instance.user.id}'
            cache.decr(concurrent_key, 1)

    except Exception as e:
        logger.error(f'Error in handle_task_delete signal: {str(e)}')

# Signal to update model version on training completion
@receiver(post_save, sender=AIModel)
def handle_model_update(sender, instance, created, **kwargs):
    """Handle AI model update events"""
    try:
        if not created:
            # Clear model-related caches
            cache_keys = [
                f'ai:model:{instance.id}',
                f'ai:model:config:{instance.id}',
            ]
            cache.delete_many(cache_keys)

            # Log model update
            logger.info(
                f'AI model updated - Name: {instance.name}, '
                f'Version: {instance.version}'
            )

    except Exception as e:
        logger.error(f'Error in handle_model_update signal: {str(e)}')
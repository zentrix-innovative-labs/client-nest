from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .models import Post, PostPlatform, PostStatus, Comment
from .tasks import publish_post_task, schedule_post_task, sync_post_analytics_task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def handle_post_save(sender, instance, created, **kwargs):
    """
    Handle post creation and status changes
    """
    try:
        if created:
            logger.info(f"New post created: {instance.id} - {instance.title}")
            
            # Log post creation for analytics
            log_post_event(instance, 'created')
            
        else:
            # Handle status changes
            if instance.status == PostStatus.PUBLISHED and instance.published_at is None:
                # Post is being published for the first time
                logger.info(f"Publishing post: {instance.id}")
                
                # Queue publishing task
                publish_post_task.delay(str(instance.id))
                
                # Log publishing event
                log_post_event(instance, 'published')
                
            elif instance.status == PostStatus.SCHEDULED and instance.scheduled_at:
                # Post is being scheduled
                logger.info(f"Scheduling post: {instance.id} for {instance.scheduled_at}")
                
                # Queue scheduling task
                schedule_post_task.apply_async(
                    args=[str(instance.id)],
                    eta=instance.scheduled_at
                )
                
                # Log scheduling event
                log_post_event(instance, 'scheduled')
                
    except Exception as e:
        logger.error(f"Error in post_save signal for post {instance.id}: {str(e)}")

@receiver(pre_save, sender=Post)
def handle_post_pre_save(sender, instance, **kwargs):
    """
    Handle pre-save operations for posts
    """
    try:
        if instance.pk:
            # Get the old instance to compare changes
            try:
                old_instance = Post.objects.get(pk=instance.pk)
                
                # Check if status changed from scheduled to something else
                if (old_instance.status == PostStatus.SCHEDULED and 
                    instance.status != PostStatus.SCHEDULED):
                    
                    logger.info(f"Post {instance.id} status changed from scheduled to {instance.status}")
                    
                    # TODO: Cancel scheduled task if needed
                    # This would require storing task IDs or using a task management system
                    
                # Check if scheduled time changed
                if (old_instance.scheduled_at != instance.scheduled_at and 
                    instance.status == PostStatus.SCHEDULED):
                    
                    logger.info(f"Post {instance.id} scheduled time changed")
                    
                    # TODO: Reschedule task
                    
            except Post.DoesNotExist:
                # This shouldn't happen, but handle gracefully
                pass
                
    except Exception as e:
        logger.error(f"Error in pre_save signal for post {instance.id}: {str(e)}")

@receiver(post_save, sender=PostPlatform)
def handle_post_platform_save(sender, instance, created, **kwargs):
    """
    Handle post platform creation and updates
    """
    try:
        if created:
            logger.info(f"New post platform created: {instance.id} - {instance.social_account.platform}")
            
        else:
            # Check if post was published to this platform
            if (instance.status == PostStatus.PUBLISHED and 
                instance.platform_post_id and 
                instance.published_at):
                
                logger.info(f"Post published to {instance.social_account.platform}: {instance.platform_post_id}")
                
                # Queue analytics sync task (delayed to allow platform processing)
                sync_post_analytics_task.apply_async(
                    args=[str(instance.id)],
                    countdown=300  # Wait 5 minutes before first analytics sync
                )
                
                # Log platform publishing event
                log_post_platform_event(instance, 'published')
                
    except Exception as e:
        logger.error(f"Error in post_platform_save signal for {instance.id}: {str(e)}")

@receiver(post_save, sender=Comment)
def handle_comment_save(sender, instance, created, **kwargs):
    """
    Handle comment creation and updates
    """
    try:
        if created:
            logger.info(f"New comment created on post platform {instance.post_platform.id}")
            
            # Update comment count on post
            post = instance.post_platform.post
            post.comment_count = Comment.objects.filter(
                post_platform__post=post
            ).count()
            post.save(update_fields=['comment_count'])
            
            # Log comment event
            log_comment_event(instance, 'created')
            
    except Exception as e:
        logger.error(f"Error in comment_save signal for comment {instance.id}: {str(e)}")

@receiver(post_delete, sender=Comment)
def handle_comment_delete(sender, instance, **kwargs):
    """
    Handle comment deletion
    """
    try:
        logger.info(f"Comment deleted from post platform {instance.post_platform.id}")
        
        # Update comment count on post
        post = instance.post_platform.post
        post.comment_count = Comment.objects.filter(
            post_platform__post=post
        ).count()
        post.save(update_fields=['comment_count'])
        
        # Log comment event
        log_comment_event(instance, 'deleted')
        
    except Exception as e:
        logger.error(f"Error in comment_delete signal: {str(e)}")

def log_post_event(post, event_type):
    """
    Log post events for analytics
    """
    try:
        # TODO: Integrate with analytics service
        # For now, just log to application logs
        logger.info(f"POST_EVENT: {event_type} - Post: {post.id} - User: {post.user.id} - Time: {timezone.now()}")
        
        # Example of what could be sent to analytics service:
        event_data = {
            'event_type': f'post_{event_type}',
            'post_id': str(post.id),
            'user_id': str(post.user.id),
            'team_id': str(post.team.id) if post.team else None,
            'post_type': post.type,
            'platform_count': post.platforms.count(),
            'has_media': post.media.exists(),
            'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else None,
            'timestamp': timezone.now().isoformat()
        }
        
        # TODO: Send to analytics service
        # analytics_service.track_event(event_data)
        
    except Exception as e:
        logger.error(f"Error logging post event: {str(e)}")

def log_post_platform_event(post_platform, event_type):
    """
    Log post platform events for analytics
    """
    try:
        logger.info(f"POST_PLATFORM_EVENT: {event_type} - PostPlatform: {post_platform.id} - Platform: {post_platform.social_account.platform}")
        
        event_data = {
            'event_type': f'post_platform_{event_type}',
            'post_platform_id': str(post_platform.id),
            'post_id': str(post_platform.post.id),
            'user_id': str(post_platform.post.user.id),
            'team_id': str(post_platform.post.team.id) if post_platform.post.team else None,
            'platform': post_platform.social_account.platform,
            'platform_post_id': post_platform.platform_post_id,
            'platform_url': post_platform.platform_url,
            'timestamp': timezone.now().isoformat()
        }
        
        # TODO: Send to analytics service
        # analytics_service.track_event(event_data)
        
    except Exception as e:
        logger.error(f"Error logging post platform event: {str(e)}")

def log_comment_event(comment, event_type):
    """
    Log comment events for analytics
    """
    try:
        logger.info(f"COMMENT_EVENT: {event_type} - Comment: {comment.id} - PostPlatform: {comment.post_platform.id}")
        
        event_data = {
            'event_type': f'comment_{event_type}',
            'comment_id': str(comment.id),
            'post_platform_id': str(comment.post_platform.id),
            'post_id': str(comment.post_platform.post.id),
            'platform': comment.post_platform.social_account.platform,
            'platform_comment_id': comment.platform_comment_id,
            'author_name': comment.author_name,
            'timestamp': timezone.now().isoformat()
        }
        
        # TODO: Send to analytics service
        # analytics_service.track_event(event_data)
        
    except Exception as e:
        logger.error(f"Error logging comment event: {str(e)}")

# Additional utility functions for signal handling

def schedule_analytics_sync(post_platform_id, delay_minutes=5):
    """
    Schedule analytics sync for a post platform
    """
    try:
        sync_post_analytics_task.apply_async(
            args=[str(post_platform_id)],
            countdown=delay_minutes * 60
        )
        logger.info(f"Analytics sync scheduled for post platform {post_platform_id} in {delay_minutes} minutes")
    except Exception as e:
        logger.error(f"Error scheduling analytics sync: {str(e)}")

def cancel_scheduled_tasks(post_id):
    """
    Cancel scheduled tasks for a post
    Note: This is a placeholder - actual implementation would depend on
    the task queue system and how task IDs are tracked
    """
    try:
        # TODO: Implement task cancellation
        # This would require:
        # 1. Storing task IDs when tasks are created
        # 2. Using the task queue's cancellation mechanism
        logger.info(f"Cancelling scheduled tasks for post {post_id}")
    except Exception as e:
        logger.error(f"Error cancelling scheduled tasks: {str(e)}")
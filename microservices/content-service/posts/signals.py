import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Post, PostPlatform, Comment

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Post)
def post_pre_save(sender, instance, **kwargs):
    """Handle pre-save validation and logging"""
    try:
        # Log status changes
        if instance.pk:
            try:
                old_instance = Post.objects.get(pk=instance.pk)
                if old_instance.status != instance.status:
                    logger.info(
                        "Post status changed",
                        extra={
                            'post_id': instance.id,
                            'post_title': instance.title,
                            'old_status': old_instance.status,
                            'new_status': instance.status,
                            'user_id': instance.user.id if instance.user else None,
                            'team_id': instance.team.id if instance.team else None,
                        }
                    )
            except Post.DoesNotExist:
                pass
    except Exception as e:
        logger.error(
            "Error in post pre_save signal",
            extra={
                'post_id': getattr(instance, 'id', None),
                'error': str(e),
                'error_type': type(e).__name__
            },
            exc_info=True
        )

@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    """Handle post save events"""
    try:
        if created:
            logger.info(
                "New post created",
                extra={
                    'post_id': instance.id,
                    'post_title': instance.title,
                    'user_id': instance.user.id if instance.user else None,
                    'team_id': instance.team.id if instance.team else None,
                    'status': instance.status,
                    'type': instance.type,
                    'scheduled_at': instance.scheduled_at.isoformat() if instance.scheduled_at else None
                }
            )
        else:
            logger.info(
                "Post updated",
                extra={
                    'post_id': instance.id,
                    'post_title': instance.title,
                    'user_id': instance.user.id if instance.user else None,
                    'team_id': instance.team.id if instance.team else None,
                    'status': instance.status,
                    'type': instance.type,
                    'scheduled_at': instance.scheduled_at.isoformat() if instance.scheduled_at else None
                }
            )
    except Exception as e:
        logger.error(
            "Error in post_saved signal",
            extra={
                'post_id': instance.id,
                'error': str(e),
                'error_type': type(e).__name__
            },
            exc_info=True
        )

@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    """Handle post delete events"""
    try:
        logger.warning(
            "Post deleted",
            extra={
                'post_id': instance.id,
                'post_title': instance.title,
                'user_id': instance.user.id if instance.user else None,
                'team_id': instance.team.id if instance.team else None,
                'status': instance.status,
                'type': instance.type,
                'platform_count': instance.platforms.count() if hasattr(instance, 'platforms') else 0
            }
        )
    except Exception as e:
        logger.error(
            "Error in post_deleted signal",
            extra={
                'post_id': getattr(instance, 'id', None),
                'error': str(e),
                'error_type': type(e).__name__
            },
            exc_info=True
        )

@receiver(post_save, sender=PostPlatform)
def post_platform_saved(sender, instance, created, **kwargs):
    """Handle post platform save events"""
    try:
        if created:
            logger.info(
                "Post platform created",
                extra={
                    'post_platform_id': instance.id,
                    'post_id': instance.post.id,
                    'post_title': instance.post.title,
                    'platform': instance.social_account.platform,
                    'platform_username': instance.social_account.platform_username,
                    'status': instance.status
                }
            )
        else:
            logger.info(
                "Post platform updated",
                extra={
                    'post_platform_id': instance.id,
                    'post_id': instance.post.id,
                    'post_title': instance.post.title,
                    'platform': instance.social_account.platform,
                    'platform_username': instance.social_account.platform_username,
                    'status': instance.status,
                    'platform_post_id': instance.platform_post_id
                }
            )
    except Exception as e:
        logger.error(
            "Error in post_platform_saved signal",
            extra={
                'post_platform_id': getattr(instance, 'id', None),
                'error': str(e),
                'error_type': type(e).__name__
            },
            exc_info=True
        )

@receiver(post_save, sender=Comment)
def comment_saved(sender, instance, created, **kwargs):
    """Handle comment save events"""
    try:
        if created:
            logger.info(
                "New comment created",
                extra={
                    'comment_id': instance.id,
                    'post_id': instance.post_platform.post.id,
                    'post_title': instance.post_platform.post.title,
                    'platform': instance.post_platform.social_account.platform,
                    'author_name': instance.author_name,
                    'platform_comment_id': instance.platform_comment_id
                }
            )
    except Exception as e:
        logger.error(
            "Error in comment_saved signal",
            extra={
                'comment_id': getattr(instance, 'id', None),
                'error': str(e),
                'error_type': type(e).__name__
            },
            exc_info=True
        )
import logging
logger = logging.getLogger(__name__)
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post

@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    """Handle post save events"""
    if created:
        logger.info(f"New post created: {instance.title}")
    else:
        logger.info(f"Post updated: {instance.title}")

@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    """Handle post delete events"""
    logger.info(f"Post deleted: {instance.title}")
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from datetime import timedelta
import logging

from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsCache, ReportStatus
)
from posts.models import Post
from .tasks import (
    sync_post_analytics, calculate_user_analytics,
    generate_analytics_insights, sync_platform_analytics
)

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def create_post_analytics(sender, instance, created, **kwargs):
    """
    Create analytics records when a new post is created.
    """
    if created:
        try:
            # Create analytics record for each platform the post is published to
            for platform in instance.platforms:
                analytics, analytics_created = PostAnalytics.objects.get_or_create(
                    post=instance,
                    platform=platform,
                    defaults={
                        'data_date': timezone.now().date(),
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'reach': 0,
                        'impressions': 0,
                        'engagement_rate': 0.0
                    }
                )
                
                if analytics_created:
                    logger.info(f"Created analytics record for post {instance.id} on {platform}")
                    
                    # Queue analytics sync task (delayed to allow platform processing)
                    sync_post_analytics.apply_async(
                        args=[str(analytics.id)],
                        countdown=300  # Wait 5 minutes before first sync
                    )
            
            # Invalidate user analytics cache
            _invalidate_user_analytics_cache(instance.owner)
            
        except Exception as e:
            logger.error(f"Error creating post analytics for post {instance.id}: {str(e)}")

@receiver(post_save, sender=PostAnalytics)
def handle_analytics_update(sender, instance, created, **kwargs):
    """
    Handle analytics updates and trigger related calculations.
    """
    try:
        # Invalidate related caches
        _invalidate_analytics_caches(instance)
        
        # Update engagement rate if metrics changed
        if not created:
            old_engagement_rate = instance.engagement_rate
            new_engagement_rate = _calculate_engagement_rate(instance)
            
            if abs(old_engagement_rate - new_engagement_rate) > 0.001:  # Significant change
                instance.engagement_rate = new_engagement_rate
                instance.save(update_fields=['engagement_rate'])
        
        # Queue user analytics recalculation if significant change
        if not created and _is_significant_change(instance):
            calculate_user_analytics.apply_async(
                args=[
                    str(instance.post.owner.id),
                    instance.data_date.strftime('%Y-%m-%d'),
                    instance.data_date.strftime('%Y-%m-%d')
                ],
                countdown=60  # Wait 1 minute to batch updates
            )
        
        # Generate insights for exceptional performance
        if _is_exceptional_performance(instance):
            generate_analytics_insights.apply_async(
                args=[str(instance.post.owner.id)],
                countdown=300  # Wait 5 minutes
            )
        
        logger.debug(f"Processed analytics update for post {instance.post.id}")
        
    except Exception as e:
        logger.error(f"Error handling analytics update: {str(e)}")

@receiver(post_save, sender=EngagementMetric)
def handle_engagement_metric_update(sender, instance, created, **kwargs):
    """
    Handle engagement metric updates and update parent analytics.
    """
    try:
        # Update parent analytics aggregated metrics
        analytics = instance.analytics
        
        # Recalculate daily totals from hourly metrics
        hourly_metrics = EngagementMetric.objects.filter(analytics=analytics)
        
        daily_totals = {
            'likes': sum(metric.likes for metric in hourly_metrics),
            'comments': sum(metric.comments for metric in hourly_metrics),
            'shares': sum(metric.shares for metric in hourly_metrics),
            'reach': max((metric.reach for metric in hourly_metrics), default=0),
            'impressions': sum(metric.impressions for metric in hourly_metrics)
        }
        
        # Update analytics if values changed significantly
        update_fields = []
        for field, value in daily_totals.items():
            current_value = getattr(analytics, field)
            if abs(current_value - value) > (current_value * 0.05):  # 5% change threshold
                setattr(analytics, field, value)
                update_fields.append(field)
        
        if update_fields:
            # Recalculate engagement rate
            analytics.engagement_rate = _calculate_engagement_rate(analytics)
            update_fields.append('engagement_rate')
            
            analytics.save(update_fields=update_fields)
            logger.debug(f"Updated analytics from hourly metrics: {update_fields}")
        
    except Exception as e:
        logger.error(f"Error handling engagement metric update: {str(e)}")

@receiver(post_save, sender=UserAnalytics)
def handle_user_analytics_update(sender, instance, created, **kwargs):
    """
    Handle user analytics updates and cache management.
    """
    try:
        # Invalidate user-specific caches
        cache_keys = [
            f"user_analytics_{instance.user.id}",
            f"user_summary_{instance.user.id}",
            f"user_trends_{instance.user.id}",
            f"dashboard_overview_{instance.user.id}"
        ]
        
        cache.delete_many(cache_keys)
        
        # Update analytics cache with new data
        cache_key = f"user_analytics_{instance.user.id}_{instance.period_start}_{instance.period_end}"
        AnalyticsCache.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'data': {
                    'total_posts': instance.total_posts,
                    'total_engagement': instance.total_engagement,
                    'average_engagement_rate': float(instance.average_engagement_rate),
                    'follower_growth': instance.follower_growth,
                    'platform_breakdown': instance.platform_breakdown
                },
                'expires_at': timezone.now() + timedelta(hours=6)
            }
        )
        
        logger.debug(f"Updated user analytics cache for user {instance.user.id}")
        
    except Exception as e:
        logger.error(f"Error handling user analytics update: {str(e)}")

@receiver(post_save, sender=PlatformAnalytics)
def handle_platform_analytics_update(sender, instance, created, **kwargs):
    """
    Handle platform analytics updates.
    """
    try:
        # Invalidate platform-specific caches
        cache_keys = [
            f"platform_analytics_{instance.user.id}_{instance.platform}",
            f"platform_overview_{instance.user.id}",
            f"platform_comparison_{instance.user.id}"
        ]
        
        cache.delete_many(cache_keys)
        
        # Trigger user analytics recalculation if significant follower change
        if not created:
            # Get previous day's data for comparison
            previous_day = instance.data_date - timedelta(days=1)
            previous_analytics = PlatformAnalytics.objects.filter(
                user=instance.user,
                platform=instance.platform,
                data_date=previous_day
            ).first()
            
            if previous_analytics:
                follower_change = instance.follower_count - previous_analytics.follower_count
                change_percentage = abs(follower_change) / max(previous_analytics.follower_count, 1)
                
                # If follower change is more than 5%, recalculate user analytics
                if change_percentage > 0.05:
                    calculate_user_analytics.apply_async(
                        args=[
                            str(instance.user.id),
                            instance.data_date.strftime('%Y-%m-%d'),
                            instance.data_date.strftime('%Y-%m-%d')
                        ],
                        countdown=120
                    )
        
        logger.debug(f"Processed platform analytics update for {instance.platform}")
        
    except Exception as e:
        logger.error(f"Error handling platform analytics update: {str(e)}")

@receiver(post_save, sender=AnalyticsReport)
def handle_report_status_change(sender, instance, created, **kwargs):
    """
    Handle analytics report status changes.
    """
    try:
        # Send notifications for completed reports
        if not created and instance.status == ReportStatus.COMPLETED:
            # Queue notification task (implement based on your notification system)
            logger.info(f"Report {instance.name} completed for user {instance.user.id}")
            
            # Cache report data for quick access
            if instance.data:
                cache_key = f"report_data_{instance.id}"
                cache.set(cache_key, instance.data, timeout=3600)  # 1 hour
        
        # Handle failed reports
        elif not created and instance.status == ReportStatus.FAILED:
            logger.error(f"Report {instance.name} failed: {instance.error_message}")
            
            # Optionally retry failed reports
            if instance.parameters.get('auto_retry', False):
                from .tasks import generate_analytics_report
                generate_analytics_report.apply_async(
                    args=[str(instance.id)],
                    countdown=1800  # Retry after 30 minutes
                )
        
    except Exception as e:
        logger.error(f"Error handling report status change: {str(e)}")

@receiver(post_save, sender=AnalyticsInsight)
def handle_insight_creation(sender, instance, created, **kwargs):
    """
    Handle analytics insight creation and updates.
    """
    if created:
        try:
            # Invalidate insights cache
            cache_keys = [
                f"user_insights_{instance.user.id}",
                f"recent_insights_{instance.user.id}",
                f"dashboard_insights_{instance.user.id}"
            ]
            cache.delete_many(cache_keys)
            
            # Log high-confidence insights
            if instance.confidence_score >= 0.8:
                logger.info(
                    f"High-confidence insight generated for user {instance.user.id}: "
                    f"{instance.title} (confidence: {instance.confidence_score})"
                )
            
            # Send notification for critical insights
            if instance.priority == 'high' and instance.confidence_score >= 0.9:
                # Queue notification task
                logger.info(f"Critical insight generated: {instance.title}")
        
        except Exception as e:
            logger.error(f"Error handling insight creation: {str(e)}")

@receiver(pre_delete, sender=PostAnalytics)
def handle_analytics_deletion(sender, instance, **kwargs):
    """
    Handle analytics deletion and cleanup.
    """
    try:
        # Delete related engagement metrics
        EngagementMetric.objects.filter(analytics=instance).delete()
        
        # Invalidate related caches
        _invalidate_analytics_caches(instance)
        
        logger.debug(f"Cleaned up analytics data for post {instance.post.id}")
        
    except Exception as e:
        logger.error(f"Error handling analytics deletion: {str(e)}")

@receiver(post_delete, sender=User)
def cleanup_user_analytics(sender, instance, **kwargs):
    """
    Clean up analytics data when a user is deleted.
    """
    try:
        # Delete user analytics
        UserAnalytics.objects.filter(user=instance).delete()
        PlatformAnalytics.objects.filter(user=instance).delete()
        AnalyticsReport.objects.filter(user=instance).delete()
        AnalyticsInsight.objects.filter(user=instance).delete()
        
        # Clear user-specific caches
        cache_pattern = f"*{instance.id}*"
        # Note: This is a simplified cache clearing - implement based on your cache backend
        
        logger.info(f"Cleaned up analytics data for deleted user {instance.id}")
        
    except Exception as e:
        logger.error(f"Error cleaning up user analytics: {str(e)}")

# Helper functions

def _invalidate_analytics_caches(analytics_instance):
    """
    Invalidate caches related to an analytics instance.
    """
    user_id = analytics_instance.post.owner.id
    cache_keys = [
        f"post_analytics_{analytics_instance.post.id}",
        f"user_analytics_{user_id}",
        f"user_summary_{user_id}",
        f"dashboard_overview_{user_id}",
        f"platform_analytics_{user_id}_{analytics_instance.platform}"
    ]
    cache.delete_many(cache_keys)

def _invalidate_user_analytics_cache(user):
    """
    Invalidate all analytics caches for a user.
    """
    cache_keys = [
        f"user_analytics_{user.id}",
        f"user_summary_{user.id}",
        f"user_trends_{user.id}",
        f"dashboard_overview_{user.id}",
        f"recent_insights_{user.id}"
    ]
    cache.delete_many(cache_keys)

def _calculate_engagement_rate(analytics):
    """
    Calculate engagement rate for analytics instance.
    """
    total_engagement = analytics.likes + analytics.comments + analytics.shares
    if analytics.reach > 0:
        return total_engagement / analytics.reach
    elif analytics.impressions > 0:
        return total_engagement / analytics.impressions
    return 0.0

def _is_significant_change(analytics):
    """
    Determine if analytics change is significant enough to trigger recalculation.
    """
    # Get previous analytics for comparison
    previous_analytics = PostAnalytics.objects.filter(
        post=analytics.post,
        platform=analytics.platform,
        data_date__lt=analytics.data_date
    ).order_by('-data_date').first()
    
    if not previous_analytics:
        return True  # First analytics record is always significant
    
    # Check for significant changes in key metrics
    metrics_to_check = ['likes', 'comments', 'shares', 'reach', 'impressions']
    
    for metric in metrics_to_check:
        current_value = getattr(analytics, metric)
        previous_value = getattr(previous_analytics, metric)
        
        if previous_value > 0:
            change_percentage = abs(current_value - previous_value) / previous_value
            if change_percentage > 0.1:  # 10% change threshold
                return True
    
    return False

def _is_exceptional_performance(analytics):
    """
    Determine if analytics show exceptional performance.
    """
    # Get user's average performance for comparison
    user_avg = PostAnalytics.objects.filter(
        post__owner=analytics.post.owner,
        platform=analytics.platform,
        data_date__gte=timezone.now().date() - timedelta(days=30)
    ).aggregate(
        avg_engagement_rate=models.Avg('engagement_rate'),
        avg_reach=models.Avg('reach')
    )
    
    avg_engagement_rate = user_avg.get('avg_engagement_rate', 0) or 0
    avg_reach = user_avg.get('avg_reach', 0) or 0
    
    # Consider exceptional if 2x better than average
    if avg_engagement_rate > 0 and analytics.engagement_rate > (avg_engagement_rate * 2):
        return True
    
    if avg_reach > 0 and analytics.reach > (avg_reach * 2):
        return True
    
    return False

def _log_analytics_event(event_type, analytics_instance, additional_data=None):
    """
    Log analytics events for monitoring and debugging.
    """
    log_data = {
        'event_type': event_type,
        'post_id': str(analytics_instance.post.id),
        'platform': analytics_instance.platform,
        'user_id': str(analytics_instance.post.owner.id),
        'timestamp': timezone.now().isoformat()
    }
    
    if additional_data:
        log_data.update(additional_data)
    
    logger.info(f"Analytics event: {event_type}", extra=log_data)
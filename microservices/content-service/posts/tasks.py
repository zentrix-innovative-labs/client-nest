from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import Post, PostPlatform, PostStatus, SocialAccount
import logging
import requests
import json

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def publish_post_task(self, post_id):
    """
    Publish a post to all configured social media platforms
    """
    try:
        post = Post.objects.get(id=post_id)
        logger.info(f"Starting publication of post {post_id}")
        
        # Get all platform relationships for this post
        post_platforms = PostPlatform.objects.filter(
            post=post,
            social_account__is_active=True
        )
        
        if not post_platforms.exists():
            logger.warning(f"No active platforms found for post {post_id}")
            post.status = PostStatus.FAILED
            post.error_message = "No active social media accounts configured"
            post.save()
            return
        
        success_count = 0
        total_platforms = post_platforms.count()
        
        for post_platform in post_platforms:
            try:
                # Publish to specific platform
                result = publish_to_platform(post, post_platform)
                
                if result['success']:
                    post_platform.status = PostStatus.PUBLISHED
                    post_platform.published_at = timezone.now()
                    post_platform.platform_post_id = result.get('platform_post_id', '')
                    post_platform.platform_url = result.get('platform_url', '')
                    post_platform.error_message = ''
                    success_count += 1
                    logger.info(f"Successfully published to {post_platform.social_account.platform}")
                else:
                    post_platform.status = PostStatus.FAILED
                    post_platform.error_message = result.get('error', 'Unknown error')
                    logger.error(f"Failed to publish to {post_platform.social_account.platform}: {result.get('error')}")
                
                post_platform.save()
                
            except Exception as e:
                logger.error(f"Error publishing to {post_platform.social_account.platform}: {str(e)}")
                post_platform.status = PostStatus.FAILED
                post_platform.error_message = str(e)
                post_platform.save()
        
        # Update main post status
        if success_count == total_platforms:
            post.status = PostStatus.PUBLISHED
            post.published_at = timezone.now()
            post.error_message = ''
        elif success_count > 0:
            post.status = PostStatus.PUBLISHED  # Partial success
            post.published_at = timezone.now()
            post.error_message = f"Published to {success_count}/{total_platforms} platforms"
        else:
            post.status = PostStatus.FAILED
            post.error_message = "Failed to publish to any platform"
        
        post.save()
        
        logger.info(f"Post {post_id} publication completed. Success: {success_count}/{total_platforms}")
        
        return {
            'post_id': post_id,
            'success_count': success_count,
            'total_platforms': total_platforms,
            'status': post.status
        }
        
    except Post.DoesNotExist:
        logger.error(f"Post {post_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error in publish_post_task for post {post_id}: {str(e)}")
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying publish_post_task for post {post_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))  # Exponential backoff
        else:
            # Mark post as failed after max retries
            try:
                post = Post.objects.get(id=post_id)
                post.status = PostStatus.FAILED
                post.error_message = f"Failed after {self.max_retries} retries: {str(e)}"
                post.save()
            except:
                pass
            raise

@shared_task
def schedule_post_task(post_id):
    """
    Task to publish a scheduled post
    """
    try:
        post = Post.objects.get(id=post_id)
        
        # Check if post is still scheduled and time has come
        if post.status != PostStatus.SCHEDULED:
            logger.warning(f"Post {post_id} is no longer scheduled (status: {post.status})")
            return
        
        if post.scheduled_at and post.scheduled_at > timezone.now():
            logger.warning(f"Post {post_id} is not yet due for publishing")
            return
        
        # Update status and trigger publishing
        post.status = PostStatus.PUBLISHED
        post.save()
        
        # Call the publish task
        publish_post_task.delay(post_id)
        
        logger.info(f"Scheduled post {post_id} queued for publishing")
        
    except Post.DoesNotExist:
        logger.error(f"Scheduled post {post_id} not found")
    except Exception as e:
        logger.error(f"Error in schedule_post_task for post {post_id}: {str(e)}")

@shared_task
def sync_post_analytics_task(post_platform_id):
    """
    Sync analytics data from social media platforms
    """
    try:
        post_platform = PostPlatform.objects.get(id=post_platform_id)
        
        if not post_platform.platform_post_id:
            logger.warning(f"No platform post ID for {post_platform_id}")
            return
        
        # Fetch analytics from platform
        analytics_data = fetch_platform_analytics(post_platform)
        
        if analytics_data:
            # Update post platform analytics
            post_platform.platform_analytics = analytics_data
            post_platform.last_analytics_update = timezone.now()
            post_platform.save()
            
            # Update main post analytics
            update_post_analytics(post_platform.post)
            
            logger.info(f"Analytics updated for post platform {post_platform_id}")
        
    except PostPlatform.DoesNotExist:
        logger.error(f"PostPlatform {post_platform_id} not found")
    except Exception as e:
        logger.error(f"Error syncing analytics for {post_platform_id}: {str(e)}")

@shared_task
def bulk_sync_analytics_task():
    """
    Bulk sync analytics for all published posts
    """
    try:
        # Get published posts from last 30 days
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        
        post_platforms = PostPlatform.objects.filter(
            status=PostStatus.PUBLISHED,
            published_at__gte=cutoff_date,
            platform_post_id__isnull=False
        ).exclude(platform_post_id='')
        
        logger.info(f"Starting bulk analytics sync for {post_platforms.count()} post platforms")
        
        for post_platform in post_platforms:
            # Queue individual sync tasks
            sync_post_analytics_task.delay(str(post_platform.id))
        
        logger.info("Bulk analytics sync tasks queued")
        
    except Exception as e:
        logger.error(f"Error in bulk_sync_analytics_task: {str(e)}")

def publish_to_platform(post, post_platform):
    """
    Publish post to a specific social media platform
    """
    platform = post_platform.social_account.platform
    
    try:
        if platform == 'facebook':
            return publish_to_facebook(post, post_platform)
        elif platform == 'instagram':
            return publish_to_instagram(post, post_platform)
        elif platform == 'twitter':
            return publish_to_twitter(post, post_platform)
        elif platform == 'linkedin':
            return publish_to_linkedin(post, post_platform)
        elif platform == 'youtube':
            return publish_to_youtube(post, post_platform)
        elif platform == 'tiktok':
            return publish_to_tiktok(post, post_platform)
        else:
            return {
                'success': False,
                'error': f'Unsupported platform: {platform}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def publish_to_facebook(post, post_platform):
    """
    Publish to Facebook
    """
    # TODO: Implement Facebook Graph API integration
    logger.info(f"Publishing to Facebook (mock): {post.title}")
    
    # Mock implementation
    return {
        'success': True,
        'platform_post_id': f'fb_{post.id}',
        'platform_url': f'https://facebook.com/posts/fb_{post.id}'
    }

def publish_to_instagram(post, post_platform):
    """
    Publish to Instagram
    """
    # TODO: Implement Instagram Basic Display API integration
    logger.info(f"Publishing to Instagram (mock): {post.title}")
    
    # Mock implementation
    return {
        'success': True,
        'platform_post_id': f'ig_{post.id}',
        'platform_url': f'https://instagram.com/p/ig_{post.id}'
    }

def publish_to_twitter(post, post_platform):
    """
    Publish to Twitter
    """
    # TODO: Implement Twitter API v2 integration
    logger.info(f"Publishing to Twitter (mock): {post.title}")
    
    # Mock implementation
    return {
        'success': True,
        'platform_post_id': f'tw_{post.id}',
        'platform_url': f'https://twitter.com/status/tw_{post.id}'
    }

def publish_to_linkedin(post, post_platform):
    """
    Publish to LinkedIn
    """
    # TODO: Implement LinkedIn API integration
    logger.info(f"Publishing to LinkedIn (mock): {post.title}")
    
    # Mock implementation
    return {
        'success': True,
        'platform_post_id': f'li_{post.id}',
        'platform_url': f'https://linkedin.com/posts/li_{post.id}'
    }

def publish_to_youtube(post, post_platform):
    """
    Publish to YouTube
    """
    # TODO: Implement YouTube Data API integration
    logger.info(f"Publishing to YouTube (mock): {post.title}")
    
    # Mock implementation
    return {
        'success': True,
        'platform_post_id': f'yt_{post.id}',
        'platform_url': f'https://youtube.com/watch?v=yt_{post.id}'
    }

def publish_to_tiktok(post, post_platform):
    """
    Publish to TikTok
    """
    # TODO: Implement TikTok API integration
    logger.info(f"Publishing to TikTok (mock): {post.title}")
    
    # Mock implementation
    return {
        'success': True,
        'platform_post_id': f'tt_{post.id}',
        'platform_url': f'https://tiktok.com/@user/video/tt_{post.id}'
    }

def fetch_platform_analytics(post_platform):
    """
    Fetch analytics data from social media platform
    """
    platform = post_platform.social_account.platform
    
    try:
        if platform == 'facebook':
            return fetch_facebook_analytics(post_platform)
        elif platform == 'instagram':
            return fetch_instagram_analytics(post_platform)
        elif platform == 'twitter':
            return fetch_twitter_analytics(post_platform)
        elif platform == 'linkedin':
            return fetch_linkedin_analytics(post_platform)
        elif platform == 'youtube':
            return fetch_youtube_analytics(post_platform)
        elif platform == 'tiktok':
            return fetch_tiktok_analytics(post_platform)
        else:
            logger.warning(f'Analytics not supported for platform: {platform}')
            return None
    except Exception as e:
        logger.error(f"Error fetching analytics for {platform}: {str(e)}")
        return None

def fetch_facebook_analytics(post_platform):
    """
    Fetch Facebook analytics
    """
    # TODO: Implement Facebook Graph API analytics
    # Mock data
    return {
        'views': 1250,
        'likes': 45,
        'comments': 12,
        'shares': 8,
        'reach': 2100,
        'impressions': 3500
    }

def fetch_instagram_analytics(post_platform):
    """
    Fetch Instagram analytics
    """
    # TODO: Implement Instagram analytics
    # Mock data
    return {
        'views': 890,
        'likes': 67,
        'comments': 23,
        'shares': 15,
        'reach': 1800,
        'impressions': 2400
    }

def fetch_twitter_analytics(post_platform):
    """
    Fetch Twitter analytics
    """
    # TODO: Implement Twitter analytics
    # Mock data
    return {
        'views': 2100,
        'likes': 89,
        'comments': 34,
        'shares': 56,
        'reach': 4200,
        'impressions': 6800
    }

def fetch_linkedin_analytics(post_platform):
    """
    Fetch LinkedIn analytics
    """
    # TODO: Implement LinkedIn analytics
    # Mock data
    return {
        'views': 560,
        'likes': 23,
        'comments': 8,
        'shares': 12,
        'reach': 890,
        'impressions': 1200
    }

def fetch_youtube_analytics(post_platform):
    """
    Fetch YouTube analytics
    """
    # TODO: Implement YouTube analytics
    # Mock data
    return {
        'views': 3400,
        'likes': 156,
        'comments': 67,
        'shares': 89,
        'watch_time': 12500,  # seconds
        'subscribers_gained': 12
    }

def fetch_tiktok_analytics(post_platform):
    """
    Fetch TikTok analytics
    """
    # TODO: Implement TikTok analytics
    # Mock data
    return {
        'views': 15600,
        'likes': 890,
        'comments': 234,
        'shares': 456,
        'reach': 18900,
        'profile_visits': 67
    }

def update_post_analytics(post):
    """
    Update main post analytics from all platforms
    """
    try:
        # Aggregate analytics from all platforms
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        for post_platform in post.platforms.all():
            analytics = post_platform.platform_analytics
            if analytics:
                total_views += analytics.get('views', 0)
                total_likes += analytics.get('likes', 0)
                total_comments += analytics.get('comments', 0)
                total_shares += analytics.get('shares', 0)
        
        # Update post analytics
        post.view_count = total_views
        post.like_count = total_likes
        post.comment_count = total_comments
        post.share_count = total_shares
        post.save()
        
        logger.info(f"Updated analytics for post {post.id}")
        
    except Exception as e:
        logger.error(f"Error updating post analytics for {post.id}: {str(e)}")
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Count, F, Q
from datetime import datetime, timedelta
import json
import csv
import io
import logging
import requests
from typing import Dict, List, Any, Optional

from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsCache, AnalyticsTimeframe, ReportStatus
)
from posts.models import Post, SocialAccount
from media.models import MediaFile

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sync_post_analytics(self, analytics_id: str):
    """
    Sync analytics data for a specific post from the platform API.
    """
    try:
        analytics = PostAnalytics.objects.get(id=analytics_id)
        post = analytics.post
        
        # Get platform credentials
        social_account = SocialAccount.objects.filter(
            user=post.owner,
            platform=analytics.platform
        ).first()
        
        if not social_account:
            logger.error(f"No social account found for {analytics.platform}")
            return {'error': 'No social account found'}
        
        # Sync data based on platform
        if analytics.platform == 'instagram':
            data = _sync_instagram_analytics(social_account, post)
        elif analytics.platform == 'facebook':
            data = _sync_facebook_analytics(social_account, post)
        elif analytics.platform == 'twitter':
            data = _sync_twitter_analytics(social_account, post)
        elif analytics.platform == 'linkedin':
            data = _sync_linkedin_analytics(social_account, post)
        elif analytics.platform == 'tiktok':
            data = _sync_tiktok_analytics(social_account, post)
        elif analytics.platform == 'youtube':
            data = _sync_youtube_analytics(social_account, post)
        else:
            logger.warning(f"Platform {analytics.platform} not supported")
            return {'error': 'Platform not supported'}
        
        # Update analytics with synced data
        if data:
            for field, value in data.items():
                if hasattr(analytics, field) and value is not None:
                    setattr(analytics, field, value)
            
            analytics.last_synced = timezone.now()
            analytics.save()
            
            # Generate hourly metrics if available
            if 'hourly_data' in data:
                _create_hourly_metrics(analytics, data['hourly_data'])
            
            logger.info(f"Successfully synced analytics for post {post.id}")
            return {'success': True, 'analytics_id': analytics_id}
        
        return {'error': 'No data received from platform'}
        
    except PostAnalytics.DoesNotExist:
        logger.error(f"PostAnalytics {analytics_id} not found")
        return {'error': 'Analytics not found'}
    except Exception as exc:
        logger.error(f"Error syncing analytics {analytics_id}: {str(exc)}")
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task(bind=True, max_retries=3)
def sync_platform_analytics(self, user_id: str, platforms: List[str] = None):
    """
    Sync platform-level analytics for a user.
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Get user's social accounts
        social_accounts = SocialAccount.objects.filter(user=user)
        
        if platforms:
            social_accounts = social_accounts.filter(platform__in=platforms)
        
        synced_count = 0
        
        for account in social_accounts:
            try:
                # Get platform analytics
                if account.platform == 'instagram':
                    data = _sync_instagram_platform_analytics(account)
                elif account.platform == 'facebook':
                    data = _sync_facebook_platform_analytics(account)
                elif account.platform == 'twitter':
                    data = _sync_twitter_platform_analytics(account)
                elif account.platform == 'linkedin':
                    data = _sync_linkedin_platform_analytics(account)
                elif account.platform == 'tiktok':
                    data = _sync_tiktok_platform_analytics(account)
                elif account.platform == 'youtube':
                    data = _sync_youtube_platform_analytics(account)
                else:
                    continue
                
                if data:
                    # Create or update platform analytics
                    platform_analytics, created = PlatformAnalytics.objects.get_or_create(
                        user=user,
                        platform=account.platform,
                        data_date=timezone.now().date(),
                        defaults=data
                    )
                    
                    if not created:
                        for field, value in data.items():
                            if hasattr(platform_analytics, field) and value is not None:
                                setattr(platform_analytics, field, value)
                        platform_analytics.save()
                    
                    synced_count += 1
                    
            except Exception as e:
                logger.error(f"Error syncing {account.platform} analytics: {str(e)}")
                continue
        
        logger.info(f"Synced analytics for {synced_count} platforms")
        return {'success': True, 'synced_count': synced_count}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'error': 'User not found'}
    except Exception as exc:
        logger.error(f"Error syncing platform analytics: {str(exc)}")
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task(bind=True, max_retries=3)
def calculate_user_analytics(self, user_id: str, start_date: str, end_date: str):
    """
    Calculate user analytics for a specific period.
    """
    try:
        user = User.objects.get(id=user_id)
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get post analytics for the period
        post_analytics = PostAnalytics.objects.filter(
            post__owner=user,
            data_date__gte=start_date,
            data_date__lte=end_date
        )
        
        # Calculate aggregated metrics
        aggregated_data = post_analytics.aggregate(
            total_posts=Count('id'),
            total_likes=Sum('likes'),
            total_comments=Sum('comments'),
            total_shares=Sum('shares'),
            total_reach=Sum('reach'),
            total_impressions=Sum('impressions'),
            avg_engagement_rate=Avg('engagement_rate')
        )
        
        # Calculate platform breakdown
        platform_breakdown = {}
        for platform_data in post_analytics.values('platform').annotate(
            posts=Count('id'),
            engagement=Sum(F('likes') + F('comments') + F('shares')),
            reach=Sum('reach')
        ):
            platform_breakdown[platform_data['platform']] = {
                'posts': platform_data['posts'],
                'engagement': platform_data['engagement'] or 0,
                'reach': platform_data['reach'] or 0
            }
        
        # Calculate follower growth
        follower_growth = _calculate_follower_growth(user, start_date, end_date)
        
        # Calculate top performing content
        top_posts = post_analytics.order_by('-engagement_rate')[:10]
        top_content_types = {}
        for post in top_posts:
            content_type = post.post.content_type
            if content_type not in top_content_types:
                top_content_types[content_type] = 0
            top_content_types[content_type] += 1
        
        # Create or update user analytics
        user_analytics, created = UserAnalytics.objects.get_or_create(
            user=user,
            period_start=start_date,
            period_end=end_date,
            defaults={
                'total_posts': aggregated_data['total_posts'] or 0,
                'total_engagement': (
                    (aggregated_data['total_likes'] or 0) +
                    (aggregated_data['total_comments'] or 0) +
                    (aggregated_data['total_shares'] or 0)
                ),
                'total_reach': aggregated_data['total_reach'] or 0,
                'total_impressions': aggregated_data['total_impressions'] or 0,
                'average_engagement_rate': aggregated_data['avg_engagement_rate'] or 0,
                'follower_growth': follower_growth,
                'platform_breakdown': platform_breakdown,
                'top_content_types': top_content_types
            }
        )
        
        if not created:
            # Update existing record
            user_analytics.total_posts = aggregated_data['total_posts'] or 0
            user_analytics.total_engagement = (
                (aggregated_data['total_likes'] or 0) +
                (aggregated_data['total_comments'] or 0) +
                (aggregated_data['total_shares'] or 0)
            )
            user_analytics.total_reach = aggregated_data['total_reach'] or 0
            user_analytics.total_impressions = aggregated_data['total_impressions'] or 0
            user_analytics.average_engagement_rate = aggregated_data['avg_engagement_rate'] or 0
            user_analytics.follower_growth = follower_growth
            user_analytics.platform_breakdown = platform_breakdown
            user_analytics.top_content_types = top_content_types
            user_analytics.save()
        
        logger.info(f"Calculated user analytics for {user.username}")
        return {'success': True, 'user_analytics_id': str(user_analytics.id)}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'error': 'User not found'}
    except Exception as exc:
        logger.error(f"Error calculating user analytics: {str(exc)}")
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task(bind=True, max_retries=3)
def generate_analytics_report(self, report_id: str):
    """
    Generate an analytics report.
    """
    try:
        report = AnalyticsReport.objects.get(id=report_id)
        report.status = ReportStatus.PROCESSING
        report.save()
        
        # Generate report based on type
        if report.report_type == 'summary':
            data = _generate_summary_report(report)
        elif report.report_type == 'detailed':
            data = _generate_detailed_report(report)
        elif report.report_type == 'comparison':
            data = _generate_comparison_report(report)
        elif report.report_type == 'custom':
            data = _generate_custom_report(report)
        else:
            data = _generate_summary_report(report)
        
        # Save report data
        report.data = data
        report.status = ReportStatus.COMPLETED
        report.completed_at = timezone.now()
        
        # Generate file if requested
        if report.parameters.get('generate_file', False):
            file_url = _generate_report_file(report, data)
            report.file_url = file_url
        
        report.save()
        
        logger.info(f"Generated report {report.name}")
        return {'success': True, 'report_id': report_id}
        
    except AnalyticsReport.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'error': 'Report not found'}
    except Exception as exc:
        logger.error(f"Error generating report: {str(exc)}")
        
        # Update report status to failed
        try:
            report = AnalyticsReport.objects.get(id=report_id)
            report.status = ReportStatus.FAILED
            report.error_message = str(exc)
            report.save()
        except:
            pass
        
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task(bind=True, max_retries=3)
def generate_analytics_insights(self, user_id: str):
    """
    Generate AI-powered analytics insights for a user.
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Get recent analytics data
        recent_analytics = PostAnalytics.objects.filter(
            post__owner=user,
            data_date__gte=timezone.now().date() - timedelta(days=30)
        )
        
        insights = []
        
        # Performance insights
        performance_insights = _generate_performance_insights(recent_analytics)
        insights.extend(performance_insights)
        
        # Audience insights
        audience_insights = _generate_audience_insights(recent_analytics)
        insights.extend(audience_insights)
        
        # Content insights
        content_insights = _generate_content_insights(recent_analytics)
        insights.extend(content_insights)
        
        # Timing insights
        timing_insights = _generate_timing_insights(recent_analytics)
        insights.extend(timing_insights)
        
        # Growth insights
        growth_insights = _generate_growth_insights(user)
        insights.extend(growth_insights)
        
        # Save insights
        created_count = 0
        for insight_data in insights:
            insight, created = AnalyticsInsight.objects.get_or_create(
                user=user,
                insight_type=insight_data['type'],
                title=insight_data['title'],
                defaults={
                    'description': insight_data['description'],
                    'confidence_score': insight_data['confidence'],
                    'data': insight_data.get('data', {}),
                    'related_object_type': insight_data.get('related_type'),
                    'related_object_id': insight_data.get('related_id')
                }
            )
            
            if created:
                created_count += 1
        
        logger.info(f"Generated {created_count} insights for {user.username}")
        return {'success': True, 'insights_created': created_count}
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'error': 'User not found'}
    except Exception as exc:
        logger.error(f"Error generating insights: {str(exc)}")
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task(bind=True, max_retries=3)
def export_analytics_data(self, user_id: str, export_params: Dict[str, Any]):
    """
    Export analytics data in various formats.
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Get data based on parameters
        start_date = export_params.get('start_date')
        end_date = export_params.get('end_date')
        platforms = export_params.get('platforms', [])
        metrics = export_params.get('metrics', [])
        format_type = export_params.get('format', 'csv')
        
        # Query analytics data
        queryset = PostAnalytics.objects.filter(
            post__owner=user
        )
        
        if start_date:
            queryset = queryset.filter(data_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(data_date__lte=end_date)
        if platforms:
            queryset = queryset.filter(platform__in=platforms)
        
        # Export data
        if format_type == 'csv':
            file_content = _export_to_csv(queryset, metrics)
            file_extension = 'csv'
        elif format_type == 'json':
            file_content = _export_to_json(queryset, metrics)
            file_extension = 'json'
        elif format_type == 'excel':
            file_content = _export_to_excel(queryset, metrics)
            file_extension = 'xlsx'
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Save export file (implement your file storage logic)
        file_url = _save_export_file(user, file_content, file_extension)
        
        # Create export record
        export_report = AnalyticsReport.objects.create(
            user=user,
            name=f"Analytics Export {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            report_type='export',
            parameters=export_params,
            status=ReportStatus.COMPLETED,
            file_url=file_url,
            completed_at=timezone.now()
        )
        
        logger.info(f"Exported analytics data for {user.username}")
        return {
            'success': True,
            'file_url': file_url,
            'report_id': str(export_report.id)
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'error': 'User not found'}
    except Exception as exc:
        logger.error(f"Error exporting analytics data: {str(exc)}")
        self.retry(countdown=60 * (self.request.retries + 1))

@shared_task
def cleanup_old_analytics_cache():
    """
    Periodic task to clean up expired analytics cache entries.
    """
    try:
        # Delete expired cache entries
        expired_count = AnalyticsCache.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        logger.info(f"Cleaned up {expired_count} expired cache entries")
        return {'success': True, 'cleaned_count': expired_count}
        
    except Exception as exc:
        logger.error(f"Error cleaning up cache: {str(exc)}")
        return {'error': str(exc)}

@shared_task
def generate_daily_analytics_summary():
    """
    Generate daily analytics summary for all users.
    """
    try:
        yesterday = timezone.now().date() - timedelta(days=1)
        users_processed = 0
        
        # Get users with posts from yesterday
        users_with_posts = User.objects.filter(
            posts__created_at__date=yesterday
        ).distinct()
        
        for user in users_with_posts:
            try:
                # Calculate daily summary
                calculate_user_analytics.delay(
                    str(user.id),
                    yesterday.strftime('%Y-%m-%d'),
                    yesterday.strftime('%Y-%m-%d')
                )
                users_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing daily summary for user {user.id}: {str(e)}")
                continue
        
        logger.info(f"Queued daily analytics for {users_processed} users")
        return {'success': True, 'users_processed': users_processed}
        
    except Exception as exc:
        logger.error(f"Error generating daily summaries: {str(exc)}")
        return {'error': str(exc)}

# Helper functions

def _sync_instagram_analytics(social_account, post):
    """Sync Instagram analytics for a post"""
    # Implement Instagram API integration
    # This is a placeholder - implement actual API calls
    return {
        'likes': 100,
        'comments': 10,
        'shares': 5,
        'reach': 1000,
        'impressions': 1500,
        'engagement_rate': 0.115
    }

def _sync_facebook_analytics(social_account, post):
    """Sync Facebook analytics for a post"""
    # Implement Facebook API integration
    return {}

def _sync_twitter_analytics(social_account, post):
    """Sync Twitter analytics for a post"""
    # Implement Twitter API integration
    return {}

def _sync_linkedin_analytics(social_account, post):
    """Sync LinkedIn analytics for a post"""
    # Implement LinkedIn API integration
    return {}

def _sync_tiktok_analytics(social_account, post):
    """Sync TikTok analytics for a post"""
    # Implement TikTok API integration
    return {}

def _sync_youtube_analytics(social_account, post):
    """Sync YouTube analytics for a post"""
    # Implement YouTube API integration
    return {}

def _sync_instagram_platform_analytics(social_account):
    """Sync Instagram platform analytics"""
    # Implement Instagram platform API integration
    return {
        'follower_count': 5000,
        'following_count': 1000,
        'posts_count': 100,
        'average_engagement_rate': 0.05
    }

def _sync_facebook_platform_analytics(social_account):
    """Sync Facebook platform analytics"""
    return {}

def _sync_twitter_platform_analytics(social_account):
    """Sync Twitter platform analytics"""
    return {}

def _sync_linkedin_platform_analytics(social_account):
    """Sync LinkedIn platform analytics"""
    return {}

def _sync_tiktok_platform_analytics(social_account):
    """Sync TikTok platform analytics"""
    return {}

def _sync_youtube_platform_analytics(social_account):
    """Sync YouTube platform analytics"""
    return {}

def _create_hourly_metrics(analytics, hourly_data):
    """Create hourly engagement metrics"""
    for hour_data in hourly_data:
        EngagementMetric.objects.update_or_create(
            analytics=analytics,
            hour=hour_data['hour'],
            defaults={
                'likes': hour_data.get('likes', 0),
                'comments': hour_data.get('comments', 0),
                'shares': hour_data.get('shares', 0),
                'reach': hour_data.get('reach', 0),
                'impressions': hour_data.get('impressions', 0)
            }
        )

def _calculate_follower_growth(user, start_date, end_date):
    """Calculate follower growth for a period"""
    start_analytics = PlatformAnalytics.objects.filter(
        user=user,
        data_date=start_date
    ).aggregate(total=Sum('follower_count'))
    
    end_analytics = PlatformAnalytics.objects.filter(
        user=user,
        data_date=end_date
    ).aggregate(total=Sum('follower_count'))
    
    start_total = start_analytics['total'] or 0
    end_total = end_analytics['total'] or 0
    
    return end_total - start_total

def _generate_summary_report(report):
    """Generate summary report data"""
    # Implement summary report generation
    return {'type': 'summary', 'data': {}}

def _generate_detailed_report(report):
    """Generate detailed report data"""
    # Implement detailed report generation
    return {'type': 'detailed', 'data': {}}

def _generate_comparison_report(report):
    """Generate comparison report data"""
    # Implement comparison report generation
    return {'type': 'comparison', 'data': {}}

def _generate_custom_report(report):
    """Generate custom report data"""
    # Implement custom report generation
    return {'type': 'custom', 'data': {}}

def _generate_report_file(report, data):
    """Generate report file and return URL"""
    # Implement file generation and storage
    return f"/reports/{report.id}.pdf"

def _generate_performance_insights(analytics_queryset):
    """Generate performance-related insights"""
    insights = []
    
    # Example: Low engagement rate insight
    avg_engagement = analytics_queryset.aggregate(
        avg_rate=Avg('engagement_rate')
    )['avg_rate'] or 0
    
    if avg_engagement < 0.02:  # Less than 2%
        insights.append({
            'type': 'performance',
            'title': 'Low Engagement Rate Detected',
            'description': f'Your average engagement rate is {avg_engagement:.2%}, which is below the recommended 2%. Consider posting more engaging content.',
            'confidence': 0.8,
            'data': {'avg_engagement_rate': avg_engagement}
        })
    
    return insights

def _generate_audience_insights(analytics_queryset):
    """Generate audience-related insights"""
    return []

def _generate_content_insights(analytics_queryset):
    """Generate content-related insights"""
    return []

def _generate_timing_insights(analytics_queryset):
    """Generate timing-related insights"""
    return []

def _generate_growth_insights(user):
    """Generate growth-related insights"""
    return []

def _export_to_csv(queryset, metrics):
    """Export data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = ['Date', 'Platform', 'Likes', 'Comments', 'Shares', 'Reach', 'Impressions', 'Engagement Rate']
    writer.writerow(headers)
    
    # Write data
    for analytics in queryset:
        writer.writerow([
            analytics.data_date,
            analytics.platform,
            analytics.likes,
            analytics.comments,
            analytics.shares,
            analytics.reach,
            analytics.impressions,
            analytics.engagement_rate
        ])
    
    return output.getvalue()

def _export_to_json(queryset, metrics):
    """Export data to JSON format"""
    data = []
    for analytics in queryset:
        data.append({
            'date': str(analytics.data_date),
            'platform': analytics.platform,
            'likes': analytics.likes,
            'comments': analytics.comments,
            'shares': analytics.shares,
            'reach': analytics.reach,
            'impressions': analytics.impressions,
            'engagement_rate': float(analytics.engagement_rate or 0)
        })
    
    return json.dumps(data, indent=2)

def _export_to_excel(queryset, metrics):
    """Export data to Excel format"""
    # Implement Excel export using openpyxl or similar
    return b""  # Placeholder

def _save_export_file(user, content, extension):
    """Save export file and return URL"""
    # Implement file saving logic
    filename = f"analytics_export_{user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return f"/exports/{filename}"
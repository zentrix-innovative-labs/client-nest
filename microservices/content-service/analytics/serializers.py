from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsCache, AnalyticsTimeframe, MetricType, ReportStatus
)
from posts.models import Post

User = get_user_model()

class EngagementMetricSerializer(serializers.ModelSerializer):
    """Serializer for engagement metrics"""
    
    class Meta:
        model = EngagementMetric
        fields = [
            'id', 'metric_type', 'value', 'hour', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class PostAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for post analytics data"""
    
    hourly_metrics = EngagementMetricSerializer(many=True, read_only=True)
    total_engagement = serializers.ReadOnlyField()
    post_title = serializers.CharField(source='post.content', read_only=True)
    post_type = serializers.CharField(source='post.post_type', read_only=True)
    
    class Meta:
        model = PostAnalytics
        fields = [
            'id', 'post', 'platform', 'post_title', 'post_type',
            'likes', 'comments', 'shares', 'saves', 'clicks',
            'impressions', 'reach', 'unique_views',
            'video_views', 'video_completion_rate', 'average_watch_time',
            'engagement_rate', 'total_engagement',
            'demographic_data', 'geographic_data', 'traffic_sources',
            'recorded_at', 'data_date', 'is_organic', 'campaign_id',
            'hourly_metrics', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'engagement_rate', 'total_engagement',
            'post_title', 'post_type', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate analytics data"""
        # Ensure data_date is not in the future
        if data.get('data_date') and data['data_date'] > timezone.now().date():
            raise serializers.ValidationError(
                "Data date cannot be in the future"
            )
        
        # Validate video metrics are only for video posts
        post = data.get('post')
        if post and hasattr(post, 'post_type'):
            if post.post_type != 'video':
                video_fields = ['video_views', 'video_completion_rate', 'average_watch_time']
                for field in video_fields:
                    if data.get(field) is not None:
                        raise serializers.ValidationError(
                            f"{field} can only be set for video posts"
                        )
        
        return data

class PostAnalyticsListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing post analytics"""
    
    total_engagement = serializers.ReadOnlyField()
    post_title = serializers.CharField(source='post.content', read_only=True)
    
    class Meta:
        model = PostAnalytics
        fields = [
            'id', 'post', 'platform', 'post_title',
            'engagement_rate', 'total_engagement',
            'reach', 'impressions', 'data_date'
        ]

class UserAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for user analytics data"""
    
    period_duration = serializers.ReadOnlyField()
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserAnalytics
        fields = [
            'id', 'user', 'username',
            'total_posts', 'total_media_files', 'total_collections',
            'total_likes_received', 'total_comments_received',
            'total_shares_received', 'total_reach', 'total_impressions',
            'average_engagement_rate', 'average_reach_per_post',
            'platform_data', 'top_post_id', 'best_performing_platform',
            'period_start', 'period_end', 'period_duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'period_duration', 'created_at', 'updated_at'
        ]

class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for platform analytics data"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PlatformAnalytics
        fields = [
            'id', 'user', 'username', 'platform',
            'follower_count', 'following_count', 'follower_growth',
            'posts_count', 'total_likes', 'total_comments',
            'total_shares', 'total_reach', 'total_impressions',
            'average_engagement_rate', 'best_post_performance',
            'data_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']

class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for analytics reports"""
    
    is_overdue = serializers.ReadOnlyField()
    owner_username = serializers.CharField(source='user.username', read_only=True)
    shared_with_usernames = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsReport
        fields = [
            'id', 'user', 'owner_username', 'name', 'description',
            'timeframe', 'start_date', 'end_date',
            'platforms', 'post_types', 'metrics',
            'is_scheduled', 'schedule_frequency', 'next_run_date',
            'status', 'report_data', 'file_url',
            'is_public', 'shared_with', 'shared_with_usernames',
            'is_overdue', 'created_at', 'updated_at', 'generated_at'
        ]
        read_only_fields = [
            'id', 'owner_username', 'shared_with_usernames',
            'status', 'report_data', 'file_url', 'is_overdue',
            'created_at', 'updated_at', 'generated_at'
        ]
    
    def get_shared_with_usernames(self, obj):
        """Get usernames of users the report is shared with"""
        return [user.username for user in obj.shared_with.all()]
    
    def validate(self, data):
        """Validate report configuration"""
        timeframe = data.get('timeframe')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Custom timeframe requires start and end dates
        if timeframe == AnalyticsTimeframe.CUSTOM:
            if not start_date or not end_date:
                raise serializers.ValidationError(
                    "Custom timeframe requires both start_date and end_date"
                )
            
            if start_date >= end_date:
                raise serializers.ValidationError(
                    "start_date must be before end_date"
                )
        
        # Validate scheduled reports
        is_scheduled = data.get('is_scheduled', False)
        if is_scheduled:
            schedule_frequency = data.get('schedule_frequency')
            if not schedule_frequency:
                raise serializers.ValidationError(
                    "Scheduled reports require schedule_frequency"
                )
            
            if schedule_frequency not in ['daily', 'weekly', 'monthly']:
                raise serializers.ValidationError(
                    "Invalid schedule_frequency. Must be daily, weekly, or monthly"
                )
        
        return data

class AnalyticsReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating analytics reports"""
    
    class Meta:
        model = AnalyticsReport
        fields = [
            'name', 'description', 'timeframe', 'start_date', 'end_date',
            'platforms', 'post_types', 'metrics',
            'is_scheduled', 'schedule_frequency', 'is_public'
        ]
    
    def create(self, validated_data):
        """Create report with current user as owner"""
        validated_data['user'] = self.context['request'].user
        
        # Set next_run_date for scheduled reports
        if validated_data.get('is_scheduled'):
            frequency = validated_data.get('schedule_frequency')
            now = timezone.now()
            
            if frequency == 'daily':
                next_run = now + timedelta(days=1)
            elif frequency == 'weekly':
                next_run = now + timedelta(weeks=1)
            elif frequency == 'monthly':
                next_run = now + timedelta(days=30)
            else:
                next_run = now + timedelta(days=1)
            
            validated_data['next_run_date'] = next_run
        
        return super().create(validated_data)

class AnalyticsInsightSerializer(serializers.ModelSerializer):
    """Serializer for analytics insights"""
    
    is_valid = serializers.ReadOnlyField()
    username = serializers.CharField(source='user.username', read_only=True)
    related_post_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsInsight
        fields = [
            'id', 'user', 'username', 'title', 'description',
            'insight_type', 'data', 'confidence_score',
            'related_posts', 'related_post_titles', 'related_platforms',
            'is_actionable', 'action_taken', 'is_dismissed',
            'is_valid', 'valid_from', 'valid_until',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'related_post_titles', 'is_valid',
            'created_at', 'updated_at'
        ]
    
    def get_related_post_titles(self, obj):
        """Get titles of related posts"""
        return [post.content[:50] for post in obj.related_posts.all()]

class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for analytics summary data"""
    
    total_posts = serializers.IntegerField()
    total_engagement = serializers.IntegerField()
    total_reach = serializers.IntegerField()
    total_impressions = serializers.IntegerField()
    average_engagement_rate = serializers.FloatField()
    
    # Platform breakdown
    platform_breakdown = serializers.DictField()
    
    # Top performing content
    top_posts = PostAnalyticsListSerializer(many=True)
    
    # Growth metrics
    engagement_growth = serializers.FloatField()
    reach_growth = serializers.FloatField()
    follower_growth = serializers.IntegerField()
    
    # Time period
    period_start = serializers.DateField()
    period_end = serializers.DateField()

class AnalyticsComparisonSerializer(serializers.Serializer):
    """Serializer for comparing analytics between periods"""
    
    current_period = AnalyticsSummarySerializer()
    previous_period = AnalyticsSummarySerializer()
    
    # Comparison metrics
    engagement_change = serializers.FloatField()
    reach_change = serializers.FloatField()
    impressions_change = serializers.FloatField()
    engagement_rate_change = serializers.FloatField()
    
    # Insights
    insights = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

class AnalyticsExportSerializer(serializers.Serializer):
    """Serializer for analytics export requests"""
    
    format = serializers.ChoiceField(
        choices=['csv', 'xlsx', 'pdf'],
        default='csv'
    )
    timeframe = serializers.ChoiceField(
        choices=AnalyticsTimeframe.choices,
        default=AnalyticsTimeframe.MONTH
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    metrics = serializers.ListField(
        child=serializers.ChoiceField(choices=MetricType.choices),
        required=False
    )
    include_demographics = serializers.BooleanField(default=False)
    include_geographic = serializers.BooleanField(default=False)
    
    def validate(self, data):
        """Validate export parameters"""
        timeframe = data.get('timeframe')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if timeframe == AnalyticsTimeframe.CUSTOM:
            if not start_date or not end_date:
                raise serializers.ValidationError(
                    "Custom timeframe requires both start_date and end_date"
                )
        
        return data

class BulkAnalyticsActionSerializer(serializers.Serializer):
    """Serializer for bulk analytics actions"""
    
    action = serializers.ChoiceField(
        choices=['sync', 'recalculate', 'export', 'delete']
    )
    post_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    platforms = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    date_range = serializers.DictField(
        child=serializers.DateField(),
        required=False
    )
    
    def validate(self, data):
        """Validate bulk action parameters"""
        action = data.get('action')
        
        if action in ['sync', 'recalculate', 'delete']:
            if not data.get('post_ids') and not data.get('platforms'):
                raise serializers.ValidationError(
                    f"{action} action requires either post_ids or platforms"
                )
        
        date_range = data.get('date_range')
        if date_range:
            start_date = date_range.get('start')
            end_date = date_range.get('end')
            
            if start_date and end_date and start_date >= end_date:
                raise serializers.ValidationError(
                    "start_date must be before end_date in date_range"
                )
        
        return data

class AnalyticsMetricSerializer(serializers.Serializer):
    """Serializer for individual analytics metrics"""
    
    metric_name = serializers.CharField()
    current_value = serializers.FloatField()
    previous_value = serializers.FloatField(required=False)
    change_percentage = serializers.FloatField(required=False)
    trend = serializers.ChoiceField(
        choices=['up', 'down', 'stable'],
        required=False
    )
    
class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for analytics dashboard data"""
    
    overview = AnalyticsSummarySerializer()
    key_metrics = AnalyticsMetricSerializer(many=True)
    recent_insights = AnalyticsInsightSerializer(many=True)
    top_performing_posts = PostAnalyticsListSerializer(many=True)
    platform_performance = PlatformAnalyticsSerializer(many=True)
    
    # Charts data
    engagement_chart = serializers.DictField()
    reach_chart = serializers.DictField()
    growth_chart = serializers.DictField()
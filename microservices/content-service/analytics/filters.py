import django_filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsTimeframe, MetricType, ReportStatus
)
from posts.models import Post

class PostAnalyticsFilter(django_filters.FilterSet):
    """Filter for PostAnalytics model"""
    
    # Platform filtering
    platform = django_filters.ChoiceFilter(
        choices=[
            ('instagram', 'Instagram'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('linkedin', 'LinkedIn'),
            ('tiktok', 'TikTok'),
            ('youtube', 'YouTube'),
            ('pinterest', 'Pinterest')
        ]
    )
    
    # Date range filtering
    data_date = django_filters.DateFilter()
    data_date_after = django_filters.DateFilter(
        field_name='data_date',
        lookup_expr='gte'
    )
    data_date_before = django_filters.DateFilter(
        field_name='data_date',
        lookup_expr='lte'
    )
    
    # Engagement metrics filtering
    likes_min = django_filters.NumberFilter(
        field_name='likes',
        lookup_expr='gte'
    )
    likes_max = django_filters.NumberFilter(
        field_name='likes',
        lookup_expr='lte'
    )
    
    comments_min = django_filters.NumberFilter(
        field_name='comments',
        lookup_expr='gte'
    )
    comments_max = django_filters.NumberFilter(
        field_name='comments',
        lookup_expr='lte'
    )
    
    shares_min = django_filters.NumberFilter(
        field_name='shares',
        lookup_expr='gte'
    )
    shares_max = django_filters.NumberFilter(
        field_name='shares',
        lookup_expr='lte'
    )
    
    # Reach and impressions filtering
    reach_min = django_filters.NumberFilter(
        field_name='reach',
        lookup_expr='gte'
    )
    reach_max = django_filters.NumberFilter(
        field_name='reach',
        lookup_expr='lte'
    )
    
    impressions_min = django_filters.NumberFilter(
        field_name='impressions',
        lookup_expr='gte'
    )
    impressions_max = django_filters.NumberFilter(
        field_name='impressions',
        lookup_expr='lte'
    )
    
    # Engagement rate filtering
    engagement_rate_min = django_filters.NumberFilter(
        field_name='engagement_rate',
        lookup_expr='gte'
    )
    engagement_rate_max = django_filters.NumberFilter(
        field_name='engagement_rate',
        lookup_expr='lte'
    )
    
    # Video metrics filtering (for video posts)
    video_views_min = django_filters.NumberFilter(
        field_name='video_views',
        lookup_expr='gte'
    )
    video_completion_rate_min = django_filters.NumberFilter(
        field_name='video_completion_rate',
        lookup_expr='gte'
    )
    
    # Post content filtering
    post_type = django_filters.CharFilter(
        field_name='post__content_type'
    )
    
    # Timeframe filtering
    timeframe = django_filters.ChoiceFilter(
        method='filter_by_timeframe',
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('last_7_days', 'Last 7 Days'),
            ('last_30_days', 'Last 30 Days'),
            ('last_90_days', 'Last 90 Days'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year')
        ]
    )
    
    # Performance filtering
    performance = django_filters.ChoiceFilter(
        method='filter_by_performance',
        choices=[
            ('top', 'Top Performing'),
            ('bottom', 'Bottom Performing'),
            ('average', 'Average Performing')
        ]
    )
    
    # Demographics filtering
    top_age_group = django_filters.CharFilter(
        field_name='demographics__age_groups',
        lookup_expr='icontains'
    )
    top_gender = django_filters.CharFilter(
        field_name='demographics__gender',
        lookup_expr='icontains'
    )
    top_location = django_filters.CharFilter(
        field_name='demographics__locations',
        lookup_expr='icontains'
    )
    
    # Search across multiple fields
    search = django_filters.CharFilter(
        method='filter_search'
    )
    
    # Has video metrics
    has_video_metrics = django_filters.BooleanFilter(
        method='filter_has_video_metrics'
    )
    
    # Viral content (high engagement)
    is_viral = django_filters.BooleanFilter(
        method='filter_viral_content'
    )
    
    class Meta:
        model = PostAnalytics
        fields = [
            'platform', 'data_date', 'likes', 'comments', 'shares',
            'reach', 'impressions', 'engagement_rate'
        ]
    
    def filter_by_timeframe(self, queryset, name, value):
        """Filter by predefined timeframes"""
        today = timezone.now().date()
        
        if value == 'today':
            return queryset.filter(data_date=today)
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            return queryset.filter(data_date=yesterday)
        elif value == 'last_7_days':
            week_ago = today - timedelta(days=7)
            return queryset.filter(data_date__gte=week_ago)
        elif value == 'last_30_days':
            month_ago = today - timedelta(days=30)
            return queryset.filter(data_date__gte=month_ago)
        elif value == 'last_90_days':
            three_months_ago = today - timedelta(days=90)
            return queryset.filter(data_date__gte=three_months_ago)
        elif value == 'this_month':
            month_start = today.replace(day=1)
            return queryset.filter(data_date__gte=month_start)
        elif value == 'last_month':
            month_start = today.replace(day=1)
            last_month_end = month_start - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return queryset.filter(
                data_date__gte=last_month_start,
                data_date__lte=last_month_end
            )
        elif value == 'this_year':
            year_start = today.replace(month=1, day=1)
            return queryset.filter(data_date__gte=year_start)
        
        return queryset
    
    def filter_by_performance(self, queryset, name, value):
        """Filter by performance level"""
        if value == 'top':
            # Top 20% by engagement rate
            total_count = queryset.count()
            top_count = max(1, int(total_count * 0.2))
            return queryset.order_by('-engagement_rate')[:top_count]
        elif value == 'bottom':
            # Bottom 20% by engagement rate
            total_count = queryset.count()
            bottom_count = max(1, int(total_count * 0.2))
            return queryset.order_by('engagement_rate')[:bottom_count]
        elif value == 'average':
            # Middle 60% by engagement rate
            total_count = queryset.count()
            skip_count = max(1, int(total_count * 0.2))
            take_count = max(1, int(total_count * 0.6))
            return queryset.order_by('-engagement_rate')[skip_count:skip_count + take_count]
        
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        return queryset.filter(
            Q(post__caption__icontains=value) |
            Q(post__hashtags__icontains=value) |
            Q(platform__icontains=value)
        )
    
    def filter_has_video_metrics(self, queryset, name, value):
        """Filter posts with video metrics"""
        if value:
            return queryset.filter(
                video_views__isnull=False,
                video_views__gt=0
            )
        else:
            return queryset.filter(
                Q(video_views__isnull=True) |
                Q(video_views=0)
            )
    
    def filter_viral_content(self, queryset, name, value):
        """Filter viral content (top 5% by engagement)"""
        if value:
            total_count = queryset.count()
            viral_count = max(1, int(total_count * 0.05))
            return queryset.order_by('-engagement_rate')[:viral_count]
        
        return queryset

class UserAnalyticsFilter(django_filters.FilterSet):
    """Filter for UserAnalytics model"""
    
    # Date range filtering
    period_start = django_filters.DateFilter()
    period_start_after = django_filters.DateFilter(
        field_name='period_start',
        lookup_expr='gte'
    )
    period_start_before = django_filters.DateFilter(
        field_name='period_start',
        lookup_expr='lte'
    )
    
    period_end = django_filters.DateFilter()
    period_end_after = django_filters.DateFilter(
        field_name='period_end',
        lookup_expr='gte'
    )
    period_end_before = django_filters.DateFilter(
        field_name='period_end',
        lookup_expr='lte'
    )
    
    # Metrics filtering
    total_posts_min = django_filters.NumberFilter(
        field_name='total_posts',
        lookup_expr='gte'
    )
    total_posts_max = django_filters.NumberFilter(
        field_name='total_posts',
        lookup_expr='lte'
    )
    
    # total_engagement is a property, not a field
    # total_engagement_min = django_filters.NumberFilter(
    #     field_name='total_engagement',
    #     lookup_expr='gte'
    # )
    # total_engagement_max = django_filters.NumberFilter(
    #     field_name='total_engagement',
    #     lookup_expr='lte'
    # )
    
    average_engagement_rate_min = django_filters.NumberFilter(
        field_name='average_engagement_rate',
        lookup_expr='gte'
    )
    average_engagement_rate_max = django_filters.NumberFilter(
        field_name='average_engagement_rate',
        lookup_expr='lte'
    )
    
    # Growth filtering
    follower_growth_min = django_filters.NumberFilter(
        field_name='follower_growth',
        lookup_expr='gte'
    )
    follower_growth_max = django_filters.NumberFilter(
        field_name='follower_growth',
        lookup_expr='lte'
    )
    
    # Timeframe filtering
    timeframe = django_filters.ChoiceFilter(
        method='filter_by_timeframe',
        choices=[
            ('last_week', 'Last Week'),
            ('last_month', 'Last Month'),
            ('last_quarter', 'Last Quarter'),
            ('last_year', 'Last Year')
        ]
    )
    
    class Meta:
        model = UserAnalytics
        fields = [
            'period_start', 'period_end', 'total_posts',
            'average_engagement_rate'
        ]
    
    def filter_by_timeframe(self, queryset, name, value):
        """Filter by predefined timeframes"""
        today = timezone.now().date()
        
        if value == 'last_week':
            week_ago = today - timedelta(days=7)
            return queryset.filter(period_end__gte=week_ago)
        elif value == 'last_month':
            month_ago = today - timedelta(days=30)
            return queryset.filter(period_end__gte=month_ago)
        elif value == 'last_quarter':
            quarter_ago = today - timedelta(days=90)
            return queryset.filter(period_end__gte=quarter_ago)
        elif value == 'last_year':
            year_ago = today - timedelta(days=365)
            return queryset.filter(period_end__gte=year_ago)
        
        return queryset

class PlatformAnalyticsFilter(django_filters.FilterSet):
    """Filter for PlatformAnalytics model"""
    
    # Platform filtering
    platform = django_filters.ChoiceFilter(
        choices=[
            ('instagram', 'Instagram'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('linkedin', 'LinkedIn'),
            ('tiktok', 'TikTok'),
            ('youtube', 'YouTube'),
            ('pinterest', 'Pinterest')
        ]
    )
    
    # Date filtering
    data_date = django_filters.DateFilter()
    data_date_after = django_filters.DateFilter(
        field_name='data_date',
        lookup_expr='gte'
    )
    data_date_before = django_filters.DateFilter(
        field_name='data_date',
        lookup_expr='lte'
    )
    
    # Follower metrics
    follower_count_min = django_filters.NumberFilter(
        field_name='follower_count',
        lookup_expr='gte'
    )
    follower_count_max = django_filters.NumberFilter(
        field_name='follower_count',
        lookup_expr='lte'
    )
    
    # Engagement metrics
    average_engagement_rate_min = django_filters.NumberFilter(
        field_name='average_engagement_rate',
        lookup_expr='gte'
    )
    average_engagement_rate_max = django_filters.NumberFilter(
        field_name='average_engagement_rate',
        lookup_expr='lte'
    )
    
    # Posts count
    posts_count_min = django_filters.NumberFilter(
        field_name='posts_count',
        lookup_expr='gte'
    )
    posts_count_max = django_filters.NumberFilter(
        field_name='posts_count',
        lookup_expr='lte'
    )
    
    # Growth filtering
    has_growth = django_filters.BooleanFilter(
        method='filter_has_growth'
    )
    
    class Meta:
        model = PlatformAnalytics
        fields = [
            'platform', 'data_date', 'follower_count',
            'average_engagement_rate', 'posts_count'
        ]
    
    def filter_has_growth(self, queryset, name, value):
        """Filter platforms with follower growth"""
        if value:
            return queryset.filter(follower_growth__gt=0)
        else:
            return queryset.filter(follower_growth__lte=0)

class AnalyticsReportFilter(django_filters.FilterSet):
    """Filter for AnalyticsReport model"""
    
    # Report type filtering
    report_type = django_filters.ChoiceFilter(
        choices=[
            ('summary', 'Summary'),
            ('detailed', 'Detailed'),
            ('comparison', 'Comparison'),
            ('export', 'Export'),
            ('custom', 'Custom')
        ]
    )
    
    # Status filtering
    status = django_filters.ChoiceFilter(
        choices=ReportStatus.choices
    )
    
    # Date filtering
    created_at = django_filters.DateFilter()
    created_at_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_at_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    # Scheduling filtering
    is_scheduled = django_filters.BooleanFilter()
    
    # Sharing filtering
    is_public = django_filters.BooleanFilter()
    is_shared = django_filters.BooleanFilter(
        method='filter_is_shared'
    )
    
    # Search
    search = django_filters.CharFilter(
        method='filter_search'
    )
    
    # Report period filtering
    report_period = django_filters.ChoiceFilter(
        method='filter_by_report_period',
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly')
        ]
    )
    
    class Meta:
        model = AnalyticsReport
        fields = [
            'report_type', 'status', 'is_scheduled',
            'is_public', 'created_at'
        ]
    
    def filter_is_shared(self, queryset, name, value):
        """Filter shared reports"""
        if value:
            return queryset.filter(shared_with__isnull=False).distinct()
        else:
            return queryset.filter(shared_with__isnull=True)
    
    def filter_search(self, queryset, name, value):
        """Search reports by name and description"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_by_report_period(self, queryset, name, value):
        """Filter by report period length"""
        # This would depend on how you calculate period length
        # For now, we'll filter by report type
        period_mapping = {
            'daily': 'daily',
            'weekly': 'weekly',
            'monthly': 'monthly',
            'quarterly': 'quarterly',
            'yearly': 'yearly'
        }
        
        if value in period_mapping:
            return queryset.filter(
                parameters__period=period_mapping[value]
            )
        
        return queryset

class AnalyticsInsightFilter(django_filters.FilterSet):
    """Filter for AnalyticsInsight model"""
    
    # Insight type filtering
    insight_type = django_filters.ChoiceFilter(
        choices=[
            ('performance', 'Performance'),
            ('audience', 'Audience'),
            ('content', 'Content'),
            ('timing', 'Timing'),
            ('growth', 'Growth'),
            ('engagement', 'Engagement')
        ]
    )
    
    # Confidence filtering
    confidence_score_min = django_filters.NumberFilter(
        field_name='confidence_score',
        lookup_expr='gte'
    )
    confidence_score_max = django_filters.NumberFilter(
        field_name='confidence_score',
        lookup_expr='lte'
    )
    
    # Status filtering
    is_dismissed = django_filters.BooleanFilter()
    action_taken = django_filters.BooleanFilter()
    
    # Date filtering
    created_at = django_filters.DateFilter()
    created_at_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_at_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    
    # Priority filtering
    priority = django_filters.ChoiceFilter(
        method='filter_by_priority',
        choices=[
            ('high', 'High Priority'),
            ('medium', 'Medium Priority'),
            ('low', 'Low Priority')
        ]
    )
    
    # Search
    search = django_filters.CharFilter(
        method='filter_search'
    )
    
    # Recent insights
    is_recent = django_filters.BooleanFilter(
        method='filter_recent'
    )
    
    class Meta:
        model = AnalyticsInsight
        fields = [
            'insight_type', 'confidence_score', 'is_dismissed',
            'action_taken', 'created_at'
        ]
    
    def filter_by_priority(self, queryset, name, value):
        """Filter by insight priority based on confidence score"""
        if value == 'high':
            return queryset.filter(confidence_score__gte=0.8)
        elif value == 'medium':
            return queryset.filter(
                confidence_score__gte=0.5,
                confidence_score__lt=0.8
            )
        elif value == 'low':
            return queryset.filter(confidence_score__lt=0.5)
        
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search insights by title and description"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_recent(self, queryset, name, value):
        """Filter recent insights (last 7 days)"""
        if value:
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        
        return queryset

class EngagementMetricFilter(django_filters.FilterSet):
    """Filter for EngagementMetric model"""
    
    # Date and hour filtering
    date = django_filters.DateFilter(
        field_name='hour',
        lookup_expr='date'
    )
    hour = django_filters.NumberFilter(
        field_name='hour',
        lookup_expr='hour'
    )
    
    # Engagement filtering
    likes_min = django_filters.NumberFilter(
        field_name='likes',
        lookup_expr='gte'
    )
    comments_min = django_filters.NumberFilter(
        field_name='comments',
        lookup_expr='gte'
    )
    shares_min = django_filters.NumberFilter(
        field_name='shares',
        lookup_expr='gte'
    )
    
    # Time range filtering
    hour_after = django_filters.DateTimeFilter(
        field_name='hour',
        lookup_expr='gte'
    )
    hour_before = django_filters.DateTimeFilter(
        field_name='hour',
        lookup_expr='lte'
    )
    
    class Meta:
        model = EngagementMetric
        fields = ['hour', 'metric_type', 'value']
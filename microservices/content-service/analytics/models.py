from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import timedelta

User = get_user_model()

class AnalyticsTimeframe(models.TextChoices):
    """Time frame options for analytics"""
    HOUR = 'hour', 'Hour'
    DAY = 'day', 'Day'
    WEEK = 'week', 'Week'
    MONTH = 'month', 'Month'
    QUARTER = 'quarter', 'Quarter'
    YEAR = 'year', 'Year'
    CUSTOM = 'custom', 'Custom'

class MetricType(models.TextChoices):
    """Types of metrics tracked"""
    ENGAGEMENT = 'engagement', 'Engagement'
    REACH = 'reach', 'Reach'
    IMPRESSIONS = 'impressions', 'Impressions'
    CLICKS = 'clicks', 'Clicks'
    SHARES = 'shares', 'Shares'
    SAVES = 'saves', 'Saves'
    COMMENTS = 'comments', 'Comments'
    LIKES = 'likes', 'Likes'
    VIEWS = 'views', 'Views'
    FOLLOWERS = 'followers', 'Followers'
    CONVERSION = 'conversion', 'Conversion'

class ReportStatus(models.TextChoices):
    """Status of analytics reports"""
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'

class PostAnalytics(models.Model):
    """Analytics data for individual posts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='analytics_data'
    )
    platform = models.CharField(max_length=50)  # facebook, instagram, twitter, etc.
    
    # Engagement metrics
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    
    # Reach and impressions
    impressions = models.PositiveIntegerField(default=0)
    reach = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    
    # Video-specific metrics
    video_views = models.PositiveIntegerField(default=0, null=True, blank=True)
    video_completion_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True
    )
    average_watch_time = models.DurationField(null=True, blank=True)
    
    # Engagement rate calculation
    engagement_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # Demographic data (JSON field for flexibility)
    demographic_data = models.JSONField(default=dict, blank=True)
    
    # Geographic data
    geographic_data = models.JSONField(default=dict, blank=True)
    
    # Traffic sources
    traffic_sources = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    recorded_at = models.DateTimeField(default=timezone.now)
    data_date = models.DateField()  # The date this data represents
    
    # Metadata
    is_organic = models.BooleanField(default=True)
    campaign_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_post_analytics'
        verbose_name = 'Post Analytics'
        verbose_name_plural = 'Post Analytics'
        unique_together = ['post', 'platform', 'data_date']
        indexes = [
            models.Index(fields=['post', 'platform']),
            models.Index(fields=['data_date']),
            models.Index(fields=['recorded_at']),
            models.Index(fields=['engagement_rate']),
        ]
    
    def __str__(self):
        return f'{self.post.content[:50]} - {self.platform} ({self.data_date})'
    
    @property
    def total_engagement(self):
        """Calculate total engagement"""
        return self.likes + self.comments + self.shares + self.saves
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate based on reach"""
        if self.reach > 0:
            return (self.total_engagement / self.reach) * 100
        return 0.0
    
    def save(self, *args, **kwargs):
        """Override save to calculate engagement rate"""
        self.engagement_rate = self.calculate_engagement_rate()
        super().save(*args, **kwargs)

class EngagementMetric(models.Model):
    """Detailed engagement metrics with hourly granularity"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_analytics = models.ForeignKey(
        PostAnalytics,
        on_delete=models.CASCADE,
        related_name='hourly_metrics'
    )
    
    metric_type = models.CharField(max_length=20, choices=MetricType.choices)
    value = models.PositiveIntegerField(default=0)
    
    # Time granularity
    hour = models.DateTimeField()  # Rounded to the hour
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_engagement_metrics'
        verbose_name = 'Engagement Metric'
        verbose_name_plural = 'Engagement Metrics'
        unique_together = ['post_analytics', 'metric_type', 'hour']
        indexes = [
            models.Index(fields=['hour']),
            models.Index(fields=['metric_type']),
        ]
    
    def __str__(self):
        return f'{self.metric_type}: {self.value} at {self.hour}'

class UserAnalytics(models.Model):
    """Analytics data for user accounts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analytics_data'
    )
    
    # Content metrics
    total_posts = models.PositiveIntegerField(default=0)
    total_media_files = models.PositiveIntegerField(default=0)
    total_collections = models.PositiveIntegerField(default=0)
    
    # Engagement summary
    total_likes_received = models.PositiveIntegerField(default=0)
    total_comments_received = models.PositiveIntegerField(default=0)
    total_shares_received = models.PositiveIntegerField(default=0)
    total_reach = models.PositiveIntegerField(default=0)
    total_impressions = models.PositiveIntegerField(default=0)
    
    # Average metrics
    average_engagement_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    average_reach_per_post = models.FloatField(default=0.0)
    
    # Platform-specific data
    platform_data = models.JSONField(default=dict, blank=True)
    
    # Top performing content
    top_post_id = models.UUIDField(null=True, blank=True)
    best_performing_platform = models.CharField(max_length=50, blank=True)
    
    # Time period this data represents
    period_start = models.DateField()
    period_end = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_user_analytics'
        verbose_name = 'User Analytics'
        verbose_name_plural = 'User Analytics'
        unique_together = ['user', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['average_engagement_rate']),
        ]
    
    def __str__(self):
        return f'{self.user.username} Analytics ({self.period_start} - {self.period_end})'
    
    @property
    def period_duration(self):
        """Get the duration of the analytics period"""
        return self.period_end - self.period_start

class PlatformAnalytics(models.Model):
    """Analytics aggregated by platform"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='platform_analytics'
    )
    platform = models.CharField(max_length=50)
    
    # Account metrics
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    follower_growth = models.IntegerField(default=0)  # Can be negative
    
    # Content metrics
    posts_count = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    total_reach = models.PositiveIntegerField(default=0)
    total_impressions = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_engagement_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    best_post_performance = models.JSONField(default=dict, blank=True)
    
    # Time period
    data_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_platform_analytics'
        verbose_name = 'Platform Analytics'
        verbose_name_plural = 'Platform Analytics'
        unique_together = ['user', 'platform', 'data_date']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['data_date']),
            models.Index(fields=['follower_count']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.platform} ({self.data_date})'

class AnalyticsReport(models.Model):
    """Custom analytics reports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analytics_reports'
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Report configuration
    timeframe = models.CharField(
        max_length=20,
        choices=AnalyticsTimeframe.choices,
        default=AnalyticsTimeframe.MONTH
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Filters
    platforms = models.JSONField(default=list, blank=True)  # List of platforms
    post_types = models.JSONField(default=list, blank=True)  # List of post types
    metrics = models.JSONField(default=list, blank=True)  # List of metrics to include
    
    # Report settings
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    next_run_date = models.DateTimeField(null=True, blank=True)
    
    # Report status
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING
    )
    
    # Generated report data
    report_data = models.JSONField(default=dict, blank=True)
    file_url = models.URLField(blank=True)  # URL to exported file
    
    # Metadata
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(
        User,
        related_name='shared_reports',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'analytics_reports'
        verbose_name = 'Analytics Report'
        verbose_name_plural = 'Analytics Reports'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['is_scheduled']),
            models.Index(fields=['next_run_date']),
        ]
    
    def __str__(self):
        return f'{self.name} - {self.user.username}'
    
    def is_overdue(self):
        """Check if scheduled report is overdue"""
        if self.is_scheduled and self.next_run_date:
            return timezone.now() > self.next_run_date
        return False

class AnalyticsInsight(models.Model):
    """AI-generated insights from analytics data"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analytics_insights'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    insight_type = models.CharField(max_length=50)  # trend, anomaly, recommendation, etc.
    
    # Insight data
    data = models.JSONField(default=dict)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Related objects
    related_posts = models.ManyToManyField(
        'posts.Post',
        related_name='insights',
        blank=True
    )
    related_platforms = models.JSONField(default=list, blank=True)
    
    # Metadata
    is_actionable = models.BooleanField(default=False)
    action_taken = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Time relevance
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_insights'
        verbose_name = 'Analytics Insight'
        verbose_name_plural = 'Analytics Insights'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['insight_type']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['is_actionable']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]
    
    def __str__(self):
        return f'{self.title} - {self.user.username}'
    
    def is_valid(self):
        """Check if insight is still valid"""
        now = timezone.now()
        if self.valid_until:
            return self.valid_from <= now <= self.valid_until
        return self.valid_from <= now

class AnalyticsCache(models.Model):
    """Cache for expensive analytics calculations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cache_key = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    
    # Cache metadata
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='analytics_cache',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'analytics_cache'
        verbose_name = 'Analytics Cache'
        verbose_name_plural = 'Analytics Cache'
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f'Cache: {self.cache_key}'
    
    def is_expired(self):
        """Check if cache entry is expired"""
        return timezone.now() > self.expires_at
    
    @classmethod
    def get_cached_data(cls, cache_key):
        """Get cached data if not expired"""
        try:
            cache_entry = cls.objects.get(cache_key=cache_key)
            if not cache_entry.is_expired():
                return cache_entry.data
            else:
                cache_entry.delete()
                return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, cache_key, data, expires_in_hours=24, user=None):
        """Set cached data with expiration"""
        expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        
        cache_entry, created = cls.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'data': data,
                'expires_at': expires_at,
                'user': user
            }
        )
        return cache_entry
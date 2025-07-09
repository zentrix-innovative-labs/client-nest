import django_filters
from django.db.models import Q
from .models import Post, PostStatus, PostType, SocialPlatform

class PostFilter(django_filters.FilterSet):
    """
    Filter set for Post model
    """
    # Status filters
    status = django_filters.ChoiceFilter(
        choices=PostStatus.choices,
        help_text="Filter by post status"
    )
    
    # Type filters
    post_type = django_filters.ChoiceFilter(
        choices=PostType.choices,
        help_text="Filter by post type"
    )
    
    # Platform filters
    platform = django_filters.ChoiceFilter(
        field_name='platforms__social_account__platform',
        choices=SocialPlatform.choices,
        help_text="Filter by social platform"
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter posts created after this date"
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter posts created before this date"
    )
    
    scheduled_after = django_filters.DateTimeFilter(
        field_name='scheduled_at',
        lookup_expr='gte',
        help_text="Filter posts scheduled after this date"
    )
    
    scheduled_before = django_filters.DateTimeFilter(
        field_name='scheduled_at',
        lookup_expr='lte',
        help_text="Filter posts scheduled before this date"
    )
    
    published_after = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='gte',
        help_text="Filter posts published after this date"
    )
    
    published_before = django_filters.DateTimeFilter(
        field_name='published_at',
        lookup_expr='lte',
        help_text="Filter posts published before this date"
    )
    
    # Content filters
    has_media = django_filters.BooleanFilter(
        method='filter_has_media',
        help_text="Filter posts that have media attachments"
    )
    
    has_hashtags = django_filters.BooleanFilter(
        method='filter_has_hashtags',
        help_text="Filter posts that have hashtags"
    )
    
    hashtag = django_filters.CharFilter(
        method='filter_by_hashtag',
        help_text="Filter posts containing specific hashtag"
    )
    
    # Engagement filters
    min_views = django_filters.NumberFilter(
        field_name='view_count',
        lookup_expr='gte',
        help_text="Filter posts with minimum view count"
    )
    
    min_likes = django_filters.NumberFilter(
        field_name='like_count',
        lookup_expr='gte',
        help_text="Filter posts with minimum like count"
    )
    
    min_comments = django_filters.NumberFilter(
        field_name='comment_count',
        lookup_expr='gte',
        help_text="Filter posts with minimum comment count"
    )
    
    # Search filters
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Search in title and content"
    )
    
    class Meta:
        model = Post
        fields = {
            'title': ['exact', 'icontains'],
            'allow_comments': ['exact'],
            'allow_sharing': ['exact'],
        }
    
    def filter_has_media(self, queryset, name, value):
        """
        Filter posts that have media attachments
        """
        if value:
            return queryset.filter(media__isnull=False).distinct()
        else:
            return queryset.filter(media__isnull=True)
    
    def filter_has_hashtags(self, queryset, name, value):
        """
        Filter posts that have hashtags
        """
        if value:
            return queryset.exclude(hashtags=[]).exclude(hashtags__isnull=True)
        else:
            return queryset.filter(Q(hashtags=[]) | Q(hashtags__isnull=True))
    
    def filter_by_hashtag(self, queryset, name, value):
        """
        Filter posts containing a specific hashtag
        """
        if value:
            # Remove # if present
            hashtag = value.lstrip('#').lower()
            return queryset.filter(hashtags__icontains=hashtag)
        return queryset
    
    def filter_search(self, queryset, name, value):
        """
        Search in title and content
        """
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(content__icontains=value)
            )
        return queryset

class ScheduledPostFilter(django_filters.FilterSet):
    """
    Filter set specifically for scheduled posts
    """
    due_soon = django_filters.BooleanFilter(
        method='filter_due_soon',
        help_text="Filter posts due to be published within next hour"
    )
    
    overdue = django_filters.BooleanFilter(
        method='filter_overdue',
        help_text="Filter posts that are overdue for publishing"
    )
    
    class Meta:
        model = Post
        fields = ['scheduled_at']
    
    def filter_due_soon(self, queryset, name, value):
        """
        Filter posts due to be published within next hour
        """
        if value:
            from django.utils import timezone
            from datetime import timedelta
            
            now = timezone.now()
            one_hour_later = now + timedelta(hours=1)
            
            return queryset.filter(
                status=PostStatus.SCHEDULED,
                scheduled_at__gte=now,
                scheduled_at__lte=one_hour_later
            )
        return queryset
    
    def filter_overdue(self, queryset, name, value):
        """
        Filter posts that are overdue for publishing
        """
        if value:
            from django.utils import timezone
            
            return queryset.filter(
                status=PostStatus.SCHEDULED,
                scheduled_at__lt=timezone.now()
            )
        return queryset

class AnalyticsFilter(django_filters.FilterSet):
    """
    Filter set for analytics queries
    """
    date_range = django_filters.ChoiceFilter(
        method='filter_date_range',
        choices=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('last_7_days', 'Last 7 Days'),
            ('last_30_days', 'Last 30 Days'),
            ('last_90_days', 'Last 90 Days'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year'),
        ],
        help_text="Predefined date ranges for analytics"
    )
    
    high_engagement = django_filters.BooleanFilter(
        method='filter_high_engagement',
        help_text="Filter posts with above-average engagement"
    )
    
    class Meta:
        model = Post
        fields = []
    
    def filter_date_range(self, queryset, name, value):
        """
        Filter by predefined date ranges
        """
        from django.utils import timezone
        from datetime import timedelta, date
        import calendar
        
        now = timezone.now()
        today = now.date()
        
        if value == 'today':
            start_date = timezone.make_aware(
                timezone.datetime.combine(today, timezone.datetime.min.time())
            )
            return queryset.filter(created_at__gte=start_date)
        
        elif value == 'yesterday':
            yesterday = today - timedelta(days=1)
            start_date = timezone.make_aware(
                timezone.datetime.combine(yesterday, timezone.datetime.min.time())
            )
            end_date = timezone.make_aware(
                timezone.datetime.combine(yesterday, timezone.datetime.max.time())
            )
            return queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        elif value == 'last_7_days':
            start_date = now - timedelta(days=7)
            return queryset.filter(created_at__gte=start_date)
        
        elif value == 'last_30_days':
            start_date = now - timedelta(days=30)
            return queryset.filter(created_at__gte=start_date)
        
        elif value == 'last_90_days':
            start_date = now - timedelta(days=90)
            return queryset.filter(created_at__gte=start_date)
        
        elif value == 'this_month':
            start_date = timezone.make_aware(
                timezone.datetime.combine(
                    date(today.year, today.month, 1),
                    timezone.datetime.min.time()
                )
            )
            return queryset.filter(created_at__gte=start_date)
        
        elif value == 'last_month':
            if today.month == 1:
                last_month = 12
                year = today.year - 1
            else:
                last_month = today.month - 1
                year = today.year
            
            start_date = timezone.make_aware(
                timezone.datetime.combine(
                    date(year, last_month, 1),
                    timezone.datetime.min.time()
                )
            )
            
            # Last day of last month
            last_day = calendar.monthrange(year, last_month)[1]
            end_date = timezone.make_aware(
                timezone.datetime.combine(
                    date(year, last_month, last_day),
                    timezone.datetime.max.time()
                )
            )
            
            return queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        elif value == 'this_year':
            start_date = timezone.make_aware(
                timezone.datetime.combine(
                    date(today.year, 1, 1),
                    timezone.datetime.min.time()
                )
            )
            return queryset.filter(created_at__gte=start_date)
        
        return queryset
    
    def filter_high_engagement(self, queryset, name, value):
        """
        Filter posts with above-average engagement
        """
        if value:
            from django.db.models import Avg
            
            avg_engagement = queryset.aggregate(
                avg_views=Avg('view_count'),
                avg_likes=Avg('like_count'),
                avg_comments=Avg('comment_count'),
                avg_shares=Avg('share_count')
            )
            
            avg_total = (
                (avg_engagement['avg_views'] or 0) +
                (avg_engagement['avg_likes'] or 0) +
                (avg_engagement['avg_comments'] or 0) +
                (avg_engagement['avg_shares'] or 0)
            )
            
            if avg_total > 0:
                return queryset.filter(
                    view_count__gte=avg_engagement['avg_views'] or 0,
                    like_count__gte=avg_engagement['avg_likes'] or 0
                )
        
        return queryset
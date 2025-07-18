from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from django.contrib import messages
from django.http import HttpResponse
import csv
import json
from datetime import timedelta

from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsCache, ReportStatus
)
from .tasks import (
    sync_post_analytics, calculate_user_analytics,
    generate_analytics_insights, generate_analytics_report
)

# Inline admin classes

class EngagementMetricInline(admin.TabularInline):
    model = EngagementMetric
    extra = 0
    readonly_fields = ('hour', 'likes', 'comments', 'shares', 'reach', 'impressions')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

# Main admin classes

@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'post_title', 'platform', 'data_date', 'engagement_display',
        'reach', 'impressions', 'engagement_rate_display', 'last_synced_display'
    )
    list_filter = (
        'platform', 'data_date', 'last_synced',
    )
    search_fields = ('post__title', 'post__content', 'post__owner__username')
    readonly_fields = (
        'post', 'platform', 'data_date', 'created_at', 'updated_at',
        'engagement_rate_display', 'performance_score'
    )
    inlines = [EngagementMetricInline]
    date_hierarchy = 'data_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('post', 'platform', 'data_date')
        }),
        ('Engagement Metrics', {
            'fields': ('likes', 'comments', 'shares', 'saves', 'engagement_rate_display')
        }),
        ('Reach & Impressions', {
            'fields': ('reach', 'impressions', 'unique_views')
        }),
        ('Video Metrics', {
            'fields': ('video_views', 'video_completion_rate', 'average_watch_time'),
            'classes': ('collapse',)
        }),
        ('Demographics', {
            'fields': ('demographics_data',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('last_synced', 'created_at', 'updated_at', 'performance_score'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'sync_analytics', 'recalculate_engagement_rate',
        'export_to_csv', 'generate_insights'
    ]
    
    def post_title(self, obj):
        return obj.post.title[:50] + '...' if len(obj.post.title) > 50 else obj.post.title
    post_title.short_description = 'Post Title'
    
    def engagement_display(self, obj):
        total = obj.likes + obj.comments + obj.shares
        return format_html(
            '<span style="font-weight: bold;">{}</span><br/>'
            '<small>👍 {} 💬 {} 🔄 {}</small>',
            total, obj.likes, obj.comments, obj.shares
        )
    engagement_display.short_description = 'Engagement'
    
    def engagement_rate_display(self, obj):
        rate = obj.engagement_rate * 100
        color = 'green' if rate > 3 else 'orange' if rate > 1 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, rate
        )
    engagement_rate_display.short_description = 'Engagement Rate'
    
    def last_synced_display(self, obj):
        if obj.last_synced:
            time_diff = timezone.now() - obj.last_synced
            if time_diff.days > 1:
                color = 'red'
                text = f'{time_diff.days} days ago'
            elif time_diff.seconds > 3600:
                color = 'orange'
                text = f'{time_diff.seconds // 3600} hours ago'
            else:
                color = 'green'
                text = 'Recently'
            
            return format_html(
                '<span style="color: {};">{}</span>',
                color, text
            )
        return format_html('<span style="color: red;">Never</span>')
    last_synced_display.short_description = 'Last Synced'
    
    def performance_score(self, obj):
        # Calculate a simple performance score
        if obj.reach > 0:
            score = (obj.engagement_rate * 100) + (obj.reach / 1000)
            return f'{score:.1f}'
        return 'N/A'
    performance_score.short_description = 'Performance Score'
    
    def sync_analytics(self, request, queryset):
        count = 0
        for analytics in queryset:
            sync_post_analytics.delay(str(analytics.id))
            count += 1
        
        self.message_user(
            request,
            f'Queued {count} analytics records for sync.',
            messages.SUCCESS
        )
    sync_analytics.short_description = 'Sync selected analytics'
    
    def recalculate_engagement_rate(self, request, queryset):
        count = 0
        for analytics in queryset:
            total_engagement = analytics.likes + analytics.comments + analytics.shares
            if analytics.reach > 0:
                analytics.engagement_rate = total_engagement / analytics.reach
            elif analytics.impressions > 0:
                analytics.engagement_rate = total_engagement / analytics.impressions
            else:
                analytics.engagement_rate = 0
            analytics.save(update_fields=['engagement_rate'])
            count += 1
        
        self.message_user(
            request,
            f'Recalculated engagement rate for {count} records.',
            messages.SUCCESS
        )
    recalculate_engagement_rate.short_description = 'Recalculate engagement rate'
    
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Post Title', 'Platform', 'Date', 'Likes', 'Comments', 'Shares',
            'Reach', 'Impressions', 'Engagement Rate', 'Video Views'
        ])
        
        for analytics in queryset:
            writer.writerow([
                analytics.post.title,
                analytics.platform,
                analytics.data_date,
                analytics.likes,
                analytics.comments,
                analytics.shares,
                analytics.reach,
                analytics.impressions,
                analytics.engagement_rate,
                analytics.video_views or 0
            ])
        
        return response
    export_to_csv.short_description = 'Export to CSV'
    
    def generate_insights(self, request, queryset):
        users = set(analytics.post.owner for analytics in queryset)
        count = 0
        
        for user in users:
            generate_analytics_insights.delay(str(user.id))
            count += 1
        
        self.message_user(
            request,
            f'Queued insight generation for {count} users.',
            messages.SUCCESS
        )
    generate_insights.short_description = 'Generate insights for users'

@admin.register(EngagementMetric)
class EngagementMetricAdmin(admin.ModelAdmin):
    list_display = (
        'analytics_post', 'analytics_platform', 'date', 'hour',
        'engagement_total', 'reach', 'impressions'
    )
    list_filter = (
        'analytics__platform', 'analytics__data_date', 'hour',
    )
    search_fields = ('analytics__post__title',)
    readonly_fields = ('analytics', 'hour', 'engagement_total')
    
    def analytics_post(self, obj):
        return obj.analytics.post.title[:30] + '...' if len(obj.analytics.post.title) > 30 else obj.analytics.post.title
    analytics_post.short_description = 'Post'
    
    def analytics_platform(self, obj):
        return obj.analytics.platform
    analytics_platform.short_description = 'Platform'
    
    def date(self, obj):
        return obj.analytics.data_date
    date.short_description = 'Date'
    
    def engagement_total(self, obj):
        return obj.likes + obj.comments + obj.shares
    engagement_total.short_description = 'Total Engagement'

@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'period_display', 'total_posts', 'total_engagement',
        'average_engagement_rate_display', 'follower_growth_display'
    )
    list_filter = (
        'period_start', 'period_end',
    )
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'user', 'period_start', 'period_end', 'created_at', 'updated_at',
        'platform_breakdown_display', 'top_content_types_display'
    )
    
    fieldsets = (
        ('Period Information', {
            'fields': ('user', 'period_start', 'period_end')
        }),
        ('Metrics', {
            'fields': (
                'total_posts', 'total_engagement', 'total_reach', 'total_impressions',
                'average_engagement_rate', 'follower_growth'
            )
        }),
        ('Breakdown', {
            'fields': ('platform_breakdown_display', 'top_content_types_display'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['recalculate_analytics', 'export_user_analytics']
    
    def period_display(self, obj):
        return f'{obj.period_start} to {obj.period_end}'
    period_display.short_description = 'Period'
    
    def average_engagement_rate_display(self, obj):
        rate = obj.average_engagement_rate * 100
        return f'{rate:.2f}%'
    average_engagement_rate_display.short_description = 'Avg Engagement Rate'
    
    def follower_growth_display(self, obj):
        growth = obj.follower_growth
        color = 'green' if growth > 0 else 'red' if growth < 0 else 'gray'
        symbol = '+' if growth > 0 else ''
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{}</span>',
            color, symbol, growth
        )
    follower_growth_display.short_description = 'Follower Growth'
    
    def platform_breakdown_display(self, obj):
        if obj.platform_breakdown:
            breakdown = []
            for platform, data in obj.platform_breakdown.items():
                breakdown.append(f"{platform}: {data.get('posts', 0)} posts")
            return '\n'.join(breakdown)
        return 'No data'
    platform_breakdown_display.short_description = 'Platform Breakdown'
    
    def top_content_types_display(self, obj):
        if obj.top_content_types:
            types = []
            for content_type, count in obj.top_content_types.items():
                types.append(f"{content_type}: {count}")
            return '\n'.join(types)
        return 'No data'
    top_content_types_display.short_description = 'Top Content Types'
    
    def recalculate_analytics(self, request, queryset):
        count = 0
        for user_analytics in queryset:
            calculate_user_analytics.delay(
                str(user_analytics.user.id),
                user_analytics.period_start.strftime('%Y-%m-%d'),
                user_analytics.period_end.strftime('%Y-%m-%d')
            )
            count += 1
        
        self.message_user(
            request,
            f'Queued recalculation for {count} user analytics.',
            messages.SUCCESS
        )
    recalculate_analytics.short_description = 'Recalculate analytics'
    
    def export_user_analytics(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_analytics_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'User', 'Period Start', 'Period End', 'Total Posts', 'Total Engagement',
            'Total Reach', 'Average Engagement Rate', 'Follower Growth'
        ])
        
        for analytics in queryset:
            writer.writerow([
                analytics.user.username,
                analytics.period_start,
                analytics.period_end,
                analytics.total_posts,
                analytics.total_engagement,
                analytics.total_reach,
                analytics.average_engagement_rate,
                analytics.follower_growth
            ])
        
        return response
    export_user_analytics.short_description = 'Export to CSV'

@admin.register(PlatformAnalytics)
class PlatformAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'platform', 'data_date', 'follower_count',
        'following_count', 'posts_count', 'average_engagement_rate_display'
    )
    list_filter = (
        'platform', 'data_date',
    )
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'platform', 'data_date', 'created_at', 'updated_at')
    date_hierarchy = 'data_date'
    
    actions = ['sync_platform_data']
    
    def average_engagement_rate_display(self, obj):
        if obj.average_engagement_rate:
            rate = obj.average_engagement_rate * 100
            return f'{rate:.2f}%'
        return 'N/A'
    average_engagement_rate_display.short_description = 'Avg Engagement Rate'
    
    def sync_platform_data(self, request, queryset):
        users = set(analytics.user for analytics in queryset)
        platforms = set(analytics.platform for analytics in queryset)
        
        for user in users:
            from .tasks import sync_platform_analytics
            sync_platform_analytics.delay(str(user.id), list(platforms))
        
        self.message_user(
            request,
            f'Queued platform sync for {len(users)} users.',
            messages.SUCCESS
        )
    sync_platform_data.short_description = 'Sync platform data'

@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'report_type', 'status_display',
        'created_at', 'completed_at', 'is_scheduled'
    )
    list_filter = (
        'report_type', 'status', 'is_scheduled', 'is_public',
        'created_at', 'completed_at'
    )
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = (
        'user', 'status', 'created_at', 'updated_at', 'completed_at',
        'file_url', 'data_preview'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'user', 'report_type')
        }),
        ('Configuration', {
            'fields': ('parameters', 'is_scheduled', 'schedule_frequency', 'is_public')
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'file_url')
        }),
        ('Data Preview', {
            'fields': ('data_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['generate_reports', 'mark_as_public', 'mark_as_private']
    
    def status_display(self, obj):
        status_colors = {
            ReportStatus.PENDING: 'orange',
            ReportStatus.PROCESSING: 'blue',
            ReportStatus.COMPLETED: 'green',
            ReportStatus.FAILED: 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def data_preview(self, obj):
        if obj.data:
            preview = json.dumps(obj.data, indent=2)[:500]
            if len(preview) >= 500:
                preview += '...'
            return format_html('<pre>{}</pre>', preview)
        return 'No data'
    data_preview.short_description = 'Data Preview'
    
    def generate_reports(self, request, queryset):
        count = 0
        for report in queryset.filter(status__in=[ReportStatus.PENDING, ReportStatus.FAILED]):
            generate_analytics_report.delay(str(report.id))
            count += 1
        
        self.message_user(
            request,
            f'Queued {count} reports for generation.',
            messages.SUCCESS
        )
    generate_reports.short_description = 'Generate selected reports'
    
    def mark_as_public(self, request, queryset):
        count = queryset.update(is_public=True)
        self.message_user(
            request,
            f'Marked {count} reports as public.',
            messages.SUCCESS
        )
    mark_as_public.short_description = 'Mark as public'
    
    def mark_as_private(self, request, queryset):
        count = queryset.update(is_public=False)
        self.message_user(
            request,
            f'Marked {count} reports as private.',
            messages.SUCCESS
        )
    mark_as_private.short_description = 'Mark as private'

@admin.register(AnalyticsInsight)
class AnalyticsInsightAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'insight_type', 'confidence_score_display',
        'priority', 'status', 'created_at'
    )
    list_filter = (
        'insight_type', 'priority', 'status',
        'created_at'
    )
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = (
        'user', 'insight_type', 'confidence_score', 'data',
        'related_object_type', 'related_object_id', 'created_at', 'updated_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user', 'insight_type')
        }),
        ('Metrics', {
            'fields': ('confidence_score', 'priority', 'status')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_viewed', 'mark_as_dismissed', 'regenerate_insights']
    
    def confidence_score_display(self, obj):
        score = obj.confidence_score * 100
        if score >= 80:
            color = 'green'
        elif score >= 60:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f}%</span>',
            color, score
        )
    confidence_score_display.short_description = 'Confidence'
    
    def mark_as_viewed(self, request, queryset):
        count = queryset.update(status='viewed')
        self.message_user(
            request,
            f'Marked {count} insights as viewed.',
            messages.SUCCESS
        )
    mark_as_viewed.short_description = 'Mark as viewed'
    
    def mark_as_dismissed(self, request, queryset):
        count = queryset.update(status='dismissed')
        self.message_user(
            request,
            f'Dismissed {count} insights.',
            messages.SUCCESS
        )
    mark_as_dismissed.short_description = 'Dismiss insights'
    
    def regenerate_insights(self, request, queryset):
        users = set(insight.user for insight in queryset)
        count = 0
        
        for user in users:
            generate_analytics_insights.delay(str(user.id))
            count += 1
        
        self.message_user(
            request,
            f'Queued insight regeneration for {count} users.',
            messages.SUCCESS
        )
    regenerate_insights.short_description = 'Regenerate insights'

@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    list_display = ('cache_key', 'expires_at', 'is_expired', 'created_at')
    list_filter = ('expires_at', 'created_at')
    search_fields = ('cache_key',)
    readonly_fields = ('cache_key', 'data', 'created_at', 'updated_at', 'is_expired')
    
    actions = ['clear_expired_cache', 'clear_selected_cache']
    
    def is_expired(self, obj):
        expired = obj.expires_at < timezone.now()
        color = 'red' if expired else 'green'
        text = 'Yes' if expired else 'No'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    is_expired.short_description = 'Expired'
    
    def clear_expired_cache(self, request, queryset):
        count = queryset.filter(expires_at__lt=timezone.now()).delete()[0]
        self.message_user(
            request,
            f'Cleared {count} expired cache entries.',
            messages.SUCCESS
        )
    clear_expired_cache.short_description = 'Clear expired cache'
    
    def clear_selected_cache(self, request, queryset):
        count = queryset.delete()[0]
        self.message_user(
            request,
            f'Cleared {count} cache entries.',
            messages.SUCCESS
        )
    clear_selected_cache.short_description = 'Clear selected cache'

# Custom admin views

class AnalyticsOverviewAdmin(admin.ModelAdmin):
    """
    Custom admin view for analytics overview.
    """
    change_list_template = 'admin/analytics/analytics_overview.html'
    
    def changelist_view(self, request, extra_context=None):
        # Calculate overview statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Get analytics summary
        total_posts = PostAnalytics.objects.count()
        total_users = PostAnalytics.objects.values('post__owner').distinct().count()
        
        weekly_analytics = PostAnalytics.objects.filter(data_date__gte=week_ago)
        monthly_analytics = PostAnalytics.objects.filter(data_date__gte=month_ago)
        
        weekly_stats = weekly_analytics.aggregate(
            total_engagement=Sum('likes') + Sum('comments') + Sum('shares'),
            total_reach=Sum('reach'),
            avg_engagement_rate=Avg('engagement_rate')
        )
        
        monthly_stats = monthly_analytics.aggregate(
            total_engagement=Sum('likes') + Sum('comments') + Sum('shares'),
            total_reach=Sum('reach'),
            avg_engagement_rate=Avg('engagement_rate')
        )
        
        # Platform breakdown
        platform_stats = PostAnalytics.objects.filter(
            data_date__gte=week_ago
        ).values('platform').annotate(
            posts=Count('id'),
            engagement=Sum('likes') + Sum('comments') + Sum('shares')
        ).order_by('-engagement')
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_posts': total_posts,
            'total_users': total_users,
            'weekly_stats': weekly_stats,
            'monthly_stats': monthly_stats,
            'platform_stats': platform_stats,
        })
        
        return super().changelist_view(request, extra_context=extra_context)

# Register the overview admin
# admin.site.register_view(
#     'analytics/overview/',
#     view=AnalyticsOverviewAdmin().changelist_view,
#     name='Analytics Overview'
# )
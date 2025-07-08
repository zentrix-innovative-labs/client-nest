from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Sum, Avg, Count, F
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import json

from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsCache, AnalyticsTimeframe
)
from .serializers import (
    PostAnalyticsSerializer, PostAnalyticsListSerializer,
    EngagementMetricSerializer, UserAnalyticsSerializer,
    PlatformAnalyticsSerializer, AnalyticsReportSerializer,
    AnalyticsReportCreateSerializer, AnalyticsInsightSerializer,
    AnalyticsSummarySerializer, AnalyticsComparisonSerializer,
    AnalyticsExportSerializer, BulkAnalyticsActionSerializer,
    AnalyticsDashboardSerializer
)
from .permissions import (
    CanViewAnalytics, CanManageAnalytics, CanExportAnalytics,
    CanCreateReports, CanShareReports
)
from .filters import (
    PostAnalyticsFilter, UserAnalyticsFilter,
    PlatformAnalyticsFilter, AnalyticsReportFilter,
    AnalyticsInsightFilter
)
from .tasks import (
    generate_analytics_report, sync_platform_analytics,
    calculate_user_analytics, export_analytics_data,
    generate_analytics_insights
)
from posts.models import Post

class PostAnalyticsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing post analytics data"""
    
    serializer_class = PostAnalyticsSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostAnalyticsFilter
    
    def get_queryset(self):
        """Filter analytics by user's posts"""
        return PostAnalytics.objects.filter(
            post__owner=self.request.user
        ).select_related('post').prefetch_related('hourly_metrics')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return PostAnalyticsListSerializer
        return PostAnalyticsSerializer
    
    def get_permissions(self):
        """Different permissions for different actions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageAnalytics]
        else:
            permission_classes = [IsAuthenticated, CanViewAnalytics]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def hourly_breakdown(self, request, pk=None):
        """Get hourly engagement breakdown for a post"""
        analytics = self.get_object()
        metrics = analytics.hourly_metrics.all().order_by('hour')
        serializer = EngagementMetricSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync analytics data from platform"""
        analytics = self.get_object()
        
        # Queue sync task
        from .tasks import sync_post_analytics
        sync_post_analytics.delay(str(analytics.id))
        
        return Response({
            'message': 'Analytics sync queued',
            'analytics_id': str(analytics.id)
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get analytics summary for user's posts"""
        queryset = self.get_queryset()
        
        # Apply filters
        filtered_queryset = self.filter_queryset(queryset)
        
        # Calculate summary metrics
        summary_data = filtered_queryset.aggregate(
            total_posts=Count('id'),
            total_likes=Sum('likes'),
            total_comments=Sum('comments'),
            total_shares=Sum('shares'),
            total_reach=Sum('reach'),
            total_impressions=Sum('impressions'),
            avg_engagement_rate=Avg('engagement_rate')
        )
        
        # Platform breakdown
        platform_breakdown = {}
        for platform_data in filtered_queryset.values('platform').annotate(
            count=Count('id'),
            total_engagement=Sum(F('likes') + F('comments') + F('shares'))
        ):
            platform_breakdown[platform_data['platform']] = {
                'posts': platform_data['count'],
                'engagement': platform_data['total_engagement'] or 0
            }
        
        # Top performing posts
        top_posts = filtered_queryset.order_by('-engagement_rate')[:5]
        
        response_data = {
            'total_posts': summary_data['total_posts'] or 0,
            'total_engagement': (
                (summary_data['total_likes'] or 0) +
                (summary_data['total_comments'] or 0) +
                (summary_data['total_shares'] or 0)
            ),
            'total_reach': summary_data['total_reach'] or 0,
            'total_impressions': summary_data['total_impressions'] or 0,
            'average_engagement_rate': summary_data['avg_engagement_rate'] or 0,
            'platform_breakdown': platform_breakdown,
            'top_posts': PostAnalyticsListSerializer(top_posts, many=True).data
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def bulk_sync(self, request):
        """Bulk sync analytics for multiple posts"""
        serializer = BulkAnalyticsActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data['action']
        if action != 'sync':
            return Response(
                {'error': 'Only sync action is supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post_ids = serializer.validated_data.get('post_ids', [])
        platforms = serializer.validated_data.get('platforms', [])
        
        # Filter analytics to sync
        queryset = self.get_queryset()
        
        if post_ids:
            queryset = queryset.filter(post_id__in=post_ids)
        
        if platforms:
            queryset = queryset.filter(platform__in=platforms)
        
        # Queue sync tasks
        from .tasks import sync_post_analytics
        synced_count = 0
        
        for analytics in queryset:
            sync_post_analytics.delay(str(analytics.id))
            synced_count += 1
        
        return Response({
            'message': f'{synced_count} analytics sync tasks queued',
            'synced_count': synced_count
        })

class UserAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user analytics data"""
    
    serializer_class = UserAnalyticsSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserAnalyticsFilter
    
    def get_queryset(self):
        """Filter analytics by current user"""
        return UserAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate user analytics for a specific period"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue analytics calculation
        calculate_user_analytics.delay(
            str(request.user.id),
            start_date,
            end_date
        )
        
        return Response({
            'message': 'User analytics generation queued',
            'period': f'{start_date} to {end_date}'
        })

class PlatformAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing platform analytics data"""
    
    serializer_class = PlatformAnalyticsSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlatformAnalyticsFilter
    
    def get_queryset(self):
        """Filter analytics by current user"""
        return PlatformAnalytics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Sync analytics for all user's platforms"""
        platforms = request.data.get('platforms', [])
        
        # Queue sync tasks
        sync_platform_analytics.delay(
            str(request.user.id),
            platforms
        )
        
        return Response({
            'message': 'Platform analytics sync queued',
            'platforms': platforms or 'all'
        })
    
    @action(detail=False, methods=['get'])
    def comparison(self, request):
        """Compare platform performance"""
        queryset = self.get_queryset()
        
        # Get latest data for each platform
        latest_data = {}
        for platform_analytics in queryset.order_by('platform', '-data_date').distinct('platform'):
            latest_data[platform_analytics.platform] = {
                'follower_count': platform_analytics.follower_count,
                'engagement_rate': platform_analytics.average_engagement_rate,
                'total_reach': platform_analytics.total_reach,
                'posts_count': platform_analytics.posts_count
            }
        
        return Response(latest_data)

class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing analytics reports"""
    
    serializer_class = AnalyticsReportSerializer
    permission_classes = [IsAuthenticated, CanCreateReports]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyticsReportFilter
    
    def get_queryset(self):
        """Filter reports by user access"""
        user = self.request.user
        return AnalyticsReport.objects.filter(
            Q(user=user) | Q(shared_with=user) | Q(is_public=True)
        ).distinct()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return AnalyticsReportCreateSerializer
        return AnalyticsReportSerializer
    
    def get_permissions(self):
        """Different permissions for different actions"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, CanManageAnalytics]
        elif self.action in ['share', 'unshare']:
            permission_classes = [IsAuthenticated, CanShareReports]
        else:
            permission_classes = [IsAuthenticated, CanCreateReports]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate the analytics report"""
        report = self.get_object()
        
        # Queue report generation
        generate_analytics_report.delay(str(report.id))
        
        return Response({
            'message': 'Report generation queued',
            'report_id': str(report.id)
        })
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share report with other users"""
        report = self.get_object()
        usernames = request.data.get('usernames', [])
        
        # Add users to shared_with
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        shared_count = 0
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                report.shared_with.add(user)
                shared_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'message': f'Report shared with {shared_count} users',
            'shared_count': shared_count
        })
    
    @action(detail=True, methods=['post'])
    def unshare(self, request, pk=None):
        """Unshare report from users"""
        report = self.get_object()
        usernames = request.data.get('usernames', [])
        
        # Remove users from shared_with
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        unshared_count = 0
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                report.shared_with.remove(user)
                unshared_count += 1
            except User.DoesNotExist:
                continue
        
        return Response({
            'message': f'Report unshared from {unshared_count} users',
            'unshared_count': unshared_count
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download generated report file"""
        report = self.get_object()
        
        if not report.file_url:
            return Response(
                {'error': 'Report file not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return file URL for download
        return Response({
            'download_url': report.file_url,
            'filename': f'{report.name}.pdf'
        })

class AnalyticsInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing analytics insights"""
    
    serializer_class = AnalyticsInsightSerializer
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AnalyticsInsightFilter
    
    def get_queryset(self):
        """Filter insights by current user"""
        return AnalyticsInsight.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).order_by('-confidence_score', '-created_at')
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss an insight"""
        insight = self.get_object()
        insight.is_dismissed = True
        insight.save()
        
        return Response({'message': 'Insight dismissed'})
    
    @action(detail=True, methods=['post'])
    def mark_action_taken(self, request, pk=None):
        """Mark that action was taken on insight"""
        insight = self.get_object()
        insight.action_taken = True
        insight.save()
        
        return Response({'message': 'Action marked as taken'})
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate new insights for user"""
        # Queue insight generation
        generate_analytics_insights.delay(str(request.user.id))
        
        return Response({
            'message': 'Insight generation queued'
        })

class AnalyticsDashboardViewSet(viewsets.ViewSet):
    """ViewSet for analytics dashboard data"""
    
    permission_classes = [IsAuthenticated, CanViewAnalytics]
    
    def list(self, request):
        """Get dashboard data"""
        user = request.user
        
        # Check cache first
        cache_key = f'dashboard_{user.id}_{timezone.now().date()}'
        cached_data = AnalyticsCache.get_cached_data(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Calculate dashboard data
        dashboard_data = self._calculate_dashboard_data(user)
        
        # Cache the data
        AnalyticsCache.set_cached_data(
            cache_key,
            dashboard_data,
            expires_in_hours=6,
            user=user
        )
        
        return Response(dashboard_data)
    
    def _calculate_dashboard_data(self, user):
        """Calculate dashboard data for user"""
        # Get date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Get post analytics
        post_analytics = PostAnalytics.objects.filter(
            post__owner=user,
            data_date__gte=month_ago
        )
        
        # Overview metrics
        overview = post_analytics.aggregate(
            total_posts=Count('id'),
            total_engagement=Sum(F('likes') + F('comments') + F('shares')),
            total_reach=Sum('reach'),
            total_impressions=Sum('impressions'),
            avg_engagement_rate=Avg('engagement_rate')
        )
        
        # Platform breakdown
        platform_breakdown = {}
        for platform_data in post_analytics.values('platform').annotate(
            engagement=Sum(F('likes') + F('comments') + F('shares'))
        ):
            platform_breakdown[platform_data['platform']] = platform_data['engagement'] or 0
        
        # Top performing posts
        top_posts = post_analytics.order_by('-engagement_rate')[:5]
        
        # Recent insights
        recent_insights = AnalyticsInsight.objects.filter(
            user=user,
            is_dismissed=False,
            created_at__gte=week_ago
        )[:5]
        
        # Platform performance
        platform_performance = PlatformAnalytics.objects.filter(
            user=user,
            data_date__gte=week_ago
        ).order_by('platform', '-data_date').distinct('platform')
        
        return {
            'overview': {
                'total_posts': overview['total_posts'] or 0,
                'total_engagement': overview['total_engagement'] or 0,
                'total_reach': overview['total_reach'] or 0,
                'total_impressions': overview['total_impressions'] or 0,
                'average_engagement_rate': overview['avg_engagement_rate'] or 0,
                'platform_breakdown': platform_breakdown,
                'period_start': month_ago,
                'period_end': today
            },
            'top_performing_posts': PostAnalyticsListSerializer(top_posts, many=True).data,
            'recent_insights': AnalyticsInsightSerializer(recent_insights, many=True).data,
            'platform_performance': PlatformAnalyticsSerializer(platform_performance, many=True).data,
            'engagement_chart': self._get_engagement_chart_data(post_analytics),
            'reach_chart': self._get_reach_chart_data(post_analytics),
            'growth_chart': self._get_growth_chart_data(user)
        }
    
    def _get_engagement_chart_data(self, queryset):
        """Get engagement chart data"""
        # Group by date and sum engagement
        chart_data = {}
        for analytics in queryset.values('data_date').annotate(
            engagement=Sum(F('likes') + F('comments') + F('shares'))
        ).order_by('data_date'):
            chart_data[str(analytics['data_date'])] = analytics['engagement'] or 0
        
        return chart_data
    
    def _get_reach_chart_data(self, queryset):
        """Get reach chart data"""
        chart_data = {}
        for analytics in queryset.values('data_date').annotate(
            total_reach=Sum('reach')
        ).order_by('data_date'):
            chart_data[str(analytics['data_date'])] = analytics['total_reach'] or 0
        
        return chart_data
    
    def _get_growth_chart_data(self, user):
        """Get growth chart data"""
        # Get follower growth from platform analytics
        today = timezone.now().date()
        month_ago = today - timedelta(days=30)
        
        platform_analytics = PlatformAnalytics.objects.filter(
            user=user,
            data_date__gte=month_ago
        ).order_by('data_date')
        
        chart_data = {}
        for analytics in platform_analytics.values('data_date').annotate(
            total_followers=Sum('follower_count')
        ).order_by('data_date'):
            chart_data[str(analytics['data_date'])] = analytics['total_followers'] or 0
        
        return chart_data
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Export dashboard data"""
        serializer = AnalyticsExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Queue export task
        export_analytics_data.delay(
            str(request.user.id),
            serializer.validated_data
        )
        
        return Response({
            'message': 'Export queued',
            'format': serializer.validated_data['format']
        })
    
    @action(detail=False, methods=['get'])
    def comparison(self, request):
        """Get comparison data between periods"""
        user = request.user
        
        # Get current and previous month data
        today = timezone.now().date()
        current_start = today.replace(day=1)
        previous_start = (current_start - timedelta(days=1)).replace(day=1)
        previous_end = current_start - timedelta(days=1)
        
        current_data = self._get_period_data(user, current_start, today)
        previous_data = self._get_period_data(user, previous_start, previous_end)
        
        # Calculate changes
        engagement_change = self._calculate_percentage_change(
            current_data['total_engagement'],
            previous_data['total_engagement']
        )
        
        reach_change = self._calculate_percentage_change(
            current_data['total_reach'],
            previous_data['total_reach']
        )
        
        return Response({
            'current_period': current_data,
            'previous_period': previous_data,
            'engagement_change': engagement_change,
            'reach_change': reach_change
        })
    
    def _get_period_data(self, user, start_date, end_date):
        """Get analytics data for a specific period"""
        post_analytics = PostAnalytics.objects.filter(
            post__owner=user,
            data_date__gte=start_date,
            data_date__lte=end_date
        )
        
        return post_analytics.aggregate(
            total_posts=Count('id'),
            total_engagement=Sum(F('likes') + F('comments') + F('shares')),
            total_reach=Sum('reach'),
            total_impressions=Sum('impressions'),
            avg_engagement_rate=Avg('engagement_rate')
        )
    
    def _calculate_percentage_change(self, current, previous):
        """Calculate percentage change between two values"""
        if previous and previous > 0:
            return ((current or 0) - previous) / previous * 100
        return 0
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from posts.models import Post
from .models import (
    PostAnalytics, EngagementMetric, UserAnalytics,
    PlatformAnalytics, AnalyticsReport, AnalyticsInsight,
    AnalyticsCache, ReportStatus, AnalyticsTimeframe,
    MetricType
)
from .serializers import (
    PostAnalyticsSerializer, UserAnalyticsSerializer,
    AnalyticsReportSerializer, AnalyticsInsightSerializer
)
from .tasks import (
    sync_post_analytics, calculate_user_analytics,
    generate_analytics_report, generate_analytics_insights
)
from .permissions import (
    CanViewAnalytics, CanManageAnalytics, CanExportAnalytics
)

User = get_user_model()

class AnalyticsModelTestCase(TestCase):
    """Base test case for analytics models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            owner=self.user,
            platform='instagram'
        )
        self.analytics_date = timezone.now().date()

class PostAnalyticsModelTest(AnalyticsModelTestCase):
    """Test cases for PostAnalytics model."""
    
    def test_create_post_analytics(self):
        """Test creating a PostAnalytics instance."""
        analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=self.analytics_date,
            likes=100,
            comments=20,
            shares=10,
            reach=1000,
            impressions=1500
        )
        
        self.assertEqual(analytics.post, self.post)
        self.assertEqual(analytics.platform, 'instagram')
        self.assertEqual(analytics.likes, 100)
        self.assertEqual(analytics.comments, 20)
        self.assertEqual(analytics.shares, 10)
        self.assertEqual(analytics.reach, 1000)
        self.assertEqual(analytics.impressions, 1500)
    
    def test_engagement_rate_calculation(self):
        """Test automatic engagement rate calculation."""
        analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=self.analytics_date,
            likes=100,
            comments=20,
            shares=10,
            reach=1000
        )
        
        # Engagement rate should be (100+20+10)/1000 = 0.13
        expected_rate = Decimal('0.13')
        self.assertEqual(analytics.engagement_rate, expected_rate)
    
    def test_engagement_rate_with_zero_reach(self):
        """Test engagement rate calculation with zero reach."""
        analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=self.analytics_date,
            likes=100,
            comments=20,
            shares=10,
            reach=0,
            impressions=1500
        )
        
        # Should use impressions when reach is 0
        expected_rate = Decimal('130') / Decimal('1500')
        self.assertEqual(analytics.engagement_rate, expected_rate)
    
    def test_unique_constraint(self):
        """Test unique constraint on post, platform, and data_date."""
        PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=self.analytics_date,
            likes=100
        )
        
        with self.assertRaises(Exception):
            PostAnalytics.objects.create(
                post=self.post,
                platform='instagram',
                data_date=self.analytics_date,
                likes=200
            )
    
    def test_str_representation(self):
        """Test string representation of PostAnalytics."""
        analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=self.analytics_date
        )
        
        expected_str = f"{self.post.title} - instagram - {self.analytics_date}"
        self.assertEqual(str(analytics), expected_str)

class EngagementMetricModelTest(AnalyticsModelTestCase):
    """Test cases for EngagementMetric model."""
    
    def setUp(self):
        super().setUp()
        self.analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=self.analytics_date
        )
    
    def test_create_engagement_metric(self):
        """Test creating an EngagementMetric instance."""
        metric = EngagementMetric.objects.create(
            analytics=self.analytics,
            hour=12,
            likes=50,
            comments=10,
            shares=5,
            reach=500,
            impressions=750
        )
        
        self.assertEqual(metric.analytics, self.analytics)
        self.assertEqual(metric.hour, 12)
        self.assertEqual(metric.likes, 50)
        self.assertEqual(metric.comments, 10)
        self.assertEqual(metric.shares, 5)
        self.assertEqual(metric.reach, 500)
        self.assertEqual(metric.impressions, 750)
    
    def test_hour_validation(self):
        """Test hour field validation (0-23)."""
        # Valid hour
        metric = EngagementMetric.objects.create(
            analytics=self.analytics,
            hour=23
        )
        self.assertEqual(metric.hour, 23)
        
        # Invalid hour should be handled by model validation
        with self.assertRaises(Exception):
            EngagementMetric.objects.create(
                analytics=self.analytics,
                hour=25
            )
    
    def test_unique_constraint(self):
        """Test unique constraint on analytics and hour."""
        EngagementMetric.objects.create(
            analytics=self.analytics,
            hour=12,
            likes=50
        )
        
        with self.assertRaises(Exception):
            EngagementMetric.objects.create(
                analytics=self.analytics,
                hour=12,
                likes=100
            )

class UserAnalyticsModelTest(AnalyticsModelTestCase):
    """Test cases for UserAnalytics model."""
    
    def test_create_user_analytics(self):
        """Test creating a UserAnalytics instance."""
        start_date = self.analytics_date - timedelta(days=7)
        end_date = self.analytics_date
        
        user_analytics = UserAnalytics.objects.create(
            user=self.user,
            period_start=start_date,
            period_end=end_date,
            total_posts=10,
            total_engagement=1000,
            total_reach=10000,
            average_engagement_rate=Decimal('0.10'),
            follower_growth=50
        )
        
        self.assertEqual(user_analytics.user, self.user)
        self.assertEqual(user_analytics.period_start, start_date)
        self.assertEqual(user_analytics.period_end, end_date)
        self.assertEqual(user_analytics.total_posts, 10)
        self.assertEqual(user_analytics.total_engagement, 1000)
        self.assertEqual(user_analytics.follower_growth, 50)
    
    def test_platform_breakdown_json_field(self):
        """Test platform_breakdown JSON field."""
        platform_data = {
            'instagram': {'posts': 5, 'engagement': 500},
            'facebook': {'posts': 3, 'engagement': 300},
            'twitter': {'posts': 2, 'engagement': 200}
        }
        
        user_analytics = UserAnalytics.objects.create(
            user=self.user,
            period_start=self.analytics_date - timedelta(days=7),
            period_end=self.analytics_date,
            platform_breakdown=platform_data
        )
        
        self.assertEqual(user_analytics.platform_breakdown, platform_data)
        self.assertEqual(
            user_analytics.platform_breakdown['instagram']['posts'], 5
        )

class PlatformAnalyticsModelTest(AnalyticsModelTestCase):
    """Test cases for PlatformAnalytics model."""
    
    def test_create_platform_analytics(self):
        """Test creating a PlatformAnalytics instance."""
        platform_analytics = PlatformAnalytics.objects.create(
            user=self.user,
            platform='instagram',
            data_date=self.analytics_date,
            follower_count=1000,
            following_count=500,
            posts_count=50,
            average_engagement_rate=Decimal('0.05')
        )
        
        self.assertEqual(platform_analytics.user, self.user)
        self.assertEqual(platform_analytics.platform, 'instagram')
        self.assertEqual(platform_analytics.follower_count, 1000)
        self.assertEqual(platform_analytics.following_count, 500)
        self.assertEqual(platform_analytics.posts_count, 50)
    
    def test_unique_constraint(self):
        """Test unique constraint on user, platform, and data_date."""
        PlatformAnalytics.objects.create(
            user=self.user,
            platform='instagram',
            data_date=self.analytics_date,
            follower_count=1000
        )
        
        with self.assertRaises(Exception):
            PlatformAnalytics.objects.create(
                user=self.user,
                platform='instagram',
                data_date=self.analytics_date,
                follower_count=1100
            )

class AnalyticsReportModelTest(AnalyticsModelTestCase):
    """Test cases for AnalyticsReport model."""
    
    def test_create_analytics_report(self):
        """Test creating an AnalyticsReport instance."""
        report = AnalyticsReport.objects.create(
            name='Weekly Report',
            description='Weekly analytics summary',
            user=self.user,
            report_type='summary',
            parameters={'timeframe': 'week'},
            status=ReportStatus.PENDING
        )
        
        self.assertEqual(report.name, 'Weekly Report')
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.report_type, 'summary')
        self.assertEqual(report.status, ReportStatus.PENDING)
        self.assertFalse(report.is_scheduled)
        self.assertFalse(report.is_public)
    
    def test_scheduled_report(self):
        """Test creating a scheduled report."""
        report = AnalyticsReport.objects.create(
            name='Daily Report',
            user=self.user,
            report_type='summary',
            is_scheduled=True,
            schedule_frequency='daily'
        )
        
        self.assertTrue(report.is_scheduled)
        self.assertEqual(report.schedule_frequency, 'daily')

class AnalyticsInsightModelTest(AnalyticsModelTestCase):
    """Test cases for AnalyticsInsight model."""
    
    def test_create_analytics_insight(self):
        """Test creating an AnalyticsInsight instance."""
        insight = AnalyticsInsight.objects.create(
            title='High Engagement Post',
            description='This post performed exceptionally well',
            user=self.user,
            insight_type='performance',
            confidence_score=Decimal('0.95'),
            priority='high',
            data={'engagement_rate': 0.15, 'reach': 5000}
        )
        
        self.assertEqual(insight.title, 'High Engagement Post')
        self.assertEqual(insight.user, self.user)
        self.assertEqual(insight.insight_type, 'performance')
        self.assertEqual(insight.confidence_score, Decimal('0.95'))
        self.assertEqual(insight.priority, 'high')
        self.assertEqual(insight.status, 'new')

class AnalyticsCacheModelTest(AnalyticsModelTestCase):
    """Test cases for AnalyticsCache model."""
    
    def test_create_analytics_cache(self):
        """Test creating an AnalyticsCache instance."""
        cache_data = {'total_posts': 10, 'total_engagement': 1000}
        expires_at = timezone.now() + timedelta(hours=1)
        
        cache_entry = AnalyticsCache.objects.create(
            cache_key='user_analytics_123',
            data=cache_data,
            expires_at=expires_at
        )
        
        self.assertEqual(cache_entry.cache_key, 'user_analytics_123')
        self.assertEqual(cache_entry.data, cache_data)
        self.assertEqual(cache_entry.expires_at, expires_at)
    
    def test_cache_expiration(self):
        """Test cache expiration logic."""
        # Create expired cache
        expired_cache = AnalyticsCache.objects.create(
            cache_key='expired_cache',
            data={'test': 'data'},
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Create valid cache
        valid_cache = AnalyticsCache.objects.create(
            cache_key='valid_cache',
            data={'test': 'data'},
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Test expiration check (would need custom manager method)
        self.assertTrue(expired_cache.expires_at < timezone.now())
        self.assertTrue(valid_cache.expires_at > timezone.now())

class PostAnalyticsAPITest(APITestCase):
    """Test cases for PostAnalytics API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            owner=self.user,
            platform='instagram'
        )
        
        self.analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=timezone.now().date(),
            likes=100,
            comments=20,
            shares=10,
            reach=1000,
            impressions=1500
        )
    
    def test_list_post_analytics(self):
        """Test listing post analytics."""
        url = reverse('postanalytics-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['likes'], 100)
    
    def test_retrieve_post_analytics(self):
        """Test retrieving specific post analytics."""
        url = reverse('postanalytics-detail', kwargs={'pk': self.analytics.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes'], 100)
        self.assertEqual(response.data['platform'], 'instagram')
    
    def test_filter_by_platform(self):
        """Test filtering analytics by platform."""
        # Create analytics for different platform
        PostAnalytics.objects.create(
            post=self.post,
            platform='facebook',
            data_date=timezone.now().date(),
            likes=50
        )
        
        url = reverse('postanalytics-list')
        response = self.client.get(url, {'platform': 'instagram'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['platform'], 'instagram')
    
    def test_filter_by_date_range(self):
        """Test filtering analytics by date range."""
        yesterday = timezone.now().date() - timedelta(days=1)
        PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=yesterday,
            likes=75
        )
        
        url = reverse('postanalytics-list')
        response = self.client.get(url, {
            'date_from': yesterday.strftime('%Y-%m-%d'),
            'date_to': yesterday.strftime('%Y-%m-%d')
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['likes'], 75)
    
    @patch('analytics.tasks.sync_post_analytics.delay')
    def test_sync_analytics_action(self, mock_sync):
        """Test sync analytics custom action."""
        url = reverse('postanalytics-sync', kwargs={'pk': self.analytics.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_sync.assert_called_once_with(str(self.analytics.id))
    
    def test_hourly_breakdown_action(self):
        """Test hourly breakdown custom action."""
        # Create hourly metrics
        EngagementMetric.objects.create(
            analytics=self.analytics,
            hour=10,
            likes=30,
            comments=5,
            shares=2
        )
        EngagementMetric.objects.create(
            analytics=self.analytics,
            hour=14,
            likes=70,
            comments=15,
            shares=8
        )
        
        url = reverse('postanalytics-hourly-breakdown', kwargs={'pk': self.analytics.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['hour'], 10)
        self.assertEqual(response.data[1]['hour'], 14)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to analytics."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_post = Post.objects.create(
            title='Other Post',
            content='Other content',
            owner=other_user,
            platform='instagram'
        )
        other_analytics = PostAnalytics.objects.create(
            post=other_post,
            platform='instagram',
            data_date=timezone.now().date()
        )
        
        url = reverse('postanalytics-detail', kwargs={'pk': other_analytics.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UserAnalyticsAPITest(APITestCase):
    """Test cases for UserAnalytics API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.user_analytics = UserAnalytics.objects.create(
            user=self.user,
            period_start=timezone.now().date() - timedelta(days=7),
            period_end=timezone.now().date(),
            total_posts=10,
            total_engagement=1000,
            average_engagement_rate=Decimal('0.10')
        )
    
    def test_list_user_analytics(self):
        """Test listing user analytics."""
        url = reverse('useranalytics-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['total_posts'], 10)
    
    @patch('analytics.tasks.calculate_user_analytics.delay')
    def test_generate_analytics_action(self, mock_calculate):
        """Test generate analytics custom action."""
        url = reverse('useranalytics-generate')
        response = self.client.post(url, {
            'period_start': '2023-01-01',
            'period_end': '2023-01-07'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_calculate.assert_called_once()

class AnalyticsReportAPITest(APITestCase):
    """Test cases for AnalyticsReport API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.report = AnalyticsReport.objects.create(
            name='Test Report',
            description='Test description',
            user=self.user,
            report_type='summary',
            status=ReportStatus.COMPLETED,
            data={'total_posts': 10}
        )
    
    def test_create_report(self):
        """Test creating a new analytics report."""
        url = reverse('analyticsreport-list')
        data = {
            'name': 'New Report',
            'description': 'New report description',
            'report_type': 'detailed',
            'parameters': {'timeframe': 'month'}
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Report')
        self.assertEqual(response.data['status'], ReportStatus.PENDING)
    
    def test_list_reports(self):
        """Test listing analytics reports."""
        url = reverse('analyticsreport-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Report')
    
    @patch('analytics.tasks.generate_analytics_report.delay')
    def test_generate_report_action(self, mock_generate):
        """Test generate report custom action."""
        url = reverse('analyticsreport-generate', kwargs={'pk': self.report.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_generate.assert_called_once_with(str(self.report.id))
    
    def test_share_report_action(self):
        """Test share report custom action."""
        url = reverse('analyticsreport-share', kwargs={'pk': self.report.pk})
        response = self.client.post(url, {'is_public': True})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertTrue(self.report.is_public)

class AnalyticsTaskTest(TransactionTestCase):
    """Test cases for analytics Celery tasks."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            owner=self.user,
            platform='instagram'
        )
        self.analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=timezone.now().date()
        )
    
    @patch('analytics.tasks.requests.get')
    def test_sync_post_analytics_task(self, mock_get):
        """Test sync_post_analytics task."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'likes': 150,
            'comments': 30,
            'shares': 15,
            'reach': 1200,
            'impressions': 1800
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Run task
        result = sync_post_analytics(str(self.analytics.id))
        
        # Verify results
        self.assertTrue(result)
        self.analytics.refresh_from_db()
        self.assertEqual(self.analytics.likes, 150)
        self.assertEqual(self.analytics.comments, 30)
        self.assertEqual(self.analytics.reach, 1200)
    
    @patch('analytics.tasks.PostAnalytics.objects.filter')
    def test_calculate_user_analytics_task(self, mock_filter):
        """Test calculate_user_analytics task."""
        # Mock queryset
        mock_queryset = Mock()
        mock_queryset.aggregate.return_value = {
            'total_posts': 5,
            'total_engagement': 500,
            'total_reach': 5000,
            'avg_engagement_rate': 0.10
        }
        mock_filter.return_value = mock_queryset
        
        # Run task
        start_date = '2023-01-01'
        end_date = '2023-01-07'
        result = calculate_user_analytics(str(self.user.id), start_date, end_date)
        
        # Verify task completed
        self.assertTrue(result)
    
    def test_generate_analytics_report_task(self):
        """Test generate_analytics_report task."""
        report = AnalyticsReport.objects.create(
            name='Test Report',
            user=self.user,
            report_type='summary',
            status=ReportStatus.PENDING
        )
        
        # Run task
        result = generate_analytics_report(str(report.id))
        
        # Verify report was processed
        self.assertTrue(result)
        report.refresh_from_db()
        self.assertEqual(report.status, ReportStatus.COMPLETED)
    
    @patch('analytics.tasks.openai.ChatCompletion.create')
    def test_generate_analytics_insights_task(self, mock_openai):
        """Test generate_analytics_insights task."""
        # Mock OpenAI response
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'insights': [{
                            'title': 'High Engagement',
                            'description': 'Your posts are performing well',
                            'type': 'performance',
                            'confidence': 0.9,
                            'priority': 'high'
                        }]
                    })
                }
            }]
        }
        
        # Run task
        result = generate_analytics_insights(str(self.user.id))
        
        # Verify insights were created
        self.assertTrue(result)
        insights = AnalyticsInsight.objects.filter(user=self.user)
        self.assertEqual(insights.count(), 1)
        self.assertEqual(insights.first().title, 'High Engagement')

class AnalyticsPermissionTest(TestCase):
    """Test cases for analytics permissions."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            owner=self.user,
            platform='instagram'
        )
        
        self.analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=timezone.now().date()
        )
    
    def test_can_view_analytics_permission(self):
        """Test CanViewAnalytics permission."""
        permission = CanViewAnalytics()
        
        # Mock request and view
        request = Mock()
        request.user = self.user
        view = Mock()
        
        # User should be able to view their own analytics
        self.assertTrue(permission.has_object_permission(request, view, self.analytics))
        
        # Other user should not be able to view
        request.user = self.other_user
        self.assertFalse(permission.has_object_permission(request, view, self.analytics))
    
    def test_can_manage_analytics_permission(self):
        """Test CanManageAnalytics permission."""
        permission = CanManageAnalytics()
        
        # Mock request and view
        request = Mock()
        request.user = self.user
        view = Mock()
        
        # User should be able to manage their own analytics
        self.assertTrue(permission.has_object_permission(request, view, self.analytics))
        
        # Other user should not be able to manage
        request.user = self.other_user
        self.assertFalse(permission.has_object_permission(request, view, self.analytics))
    
    @patch('analytics.permissions.cache')
    def test_can_export_analytics_rate_limit(self, mock_cache):
        """Test CanExportAnalytics rate limiting."""
        permission = CanExportAnalytics()
        
        # Mock request
        request = Mock()
        request.user = self.user
        view = Mock()
        
        # Mock cache to return under limit
        mock_cache.get.return_value = 5
        self.assertTrue(permission.has_permission(request, view))
        
        # Mock cache to return over limit
        mock_cache.get.return_value = 15
        self.assertFalse(permission.has_permission(request, view))

class AnalyticsSerializerTest(TestCase):
    """Test cases for analytics serializers."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            owner=self.user,
            platform='instagram'
        )
        self.analytics = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=timezone.now().date(),
            likes=100,
            comments=20,
            shares=10,
            reach=1000
        )
    
    def test_post_analytics_serializer(self):
        """Test PostAnalyticsSerializer."""
        serializer = PostAnalyticsSerializer(instance=self.analytics)
        data = serializer.data
        
        self.assertEqual(data['likes'], 100)
        self.assertEqual(data['comments'], 20)
        self.assertEqual(data['platform'], 'instagram')
        self.assertIn('engagement_rate', data)
        self.assertIn('post', data)
    
    def test_post_analytics_validation(self):
        """Test PostAnalyticsSerializer validation."""
        # Test future date validation
        future_date = timezone.now().date() + timedelta(days=1)
        data = {
            'post': self.post.id,
            'platform': 'instagram',
            'data_date': future_date,
            'likes': 100
        }
        
        serializer = PostAnalyticsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('data_date', serializer.errors)
    
    def test_user_analytics_serializer(self):
        """Test UserAnalyticsSerializer."""
        user_analytics = UserAnalytics.objects.create(
            user=self.user,
            period_start=timezone.now().date() - timedelta(days=7),
            period_end=timezone.now().date(),
            total_posts=10,
            total_engagement=1000
        )
        
        serializer = UserAnalyticsSerializer(instance=user_analytics)
        data = serializer.data
        
        self.assertEqual(data['total_posts'], 10)
        self.assertEqual(data['total_engagement'], 1000)
        self.assertIn('user', data)
        self.assertIn('period_start', data)
    
    def test_analytics_report_serializer(self):
        """Test AnalyticsReportSerializer."""
        report = AnalyticsReport.objects.create(
            name='Test Report',
            description='Test description',
            user=self.user,
            report_type='summary'
        )
        
        serializer = AnalyticsReportSerializer(instance=report)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Report')
        self.assertEqual(data['report_type'], 'summary')
        self.assertIn('user', data)
        self.assertIn('status', data)

class AnalyticsFilterTest(TestCase):
    """Test cases for analytics filters."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            owner=self.user,
            platform='instagram'
        )
        
        # Create analytics for different dates and platforms
        self.analytics1 = PostAnalytics.objects.create(
            post=self.post,
            platform='instagram',
            data_date=timezone.now().date(),
            likes=100,
            reach=1000
        )
        
        self.analytics2 = PostAnalytics.objects.create(
            post=self.post,
            platform='facebook',
            data_date=timezone.now().date() - timedelta(days=1),
            likes=50,
            reach=500
        )
    
    def test_platform_filter(self):
        """Test filtering by platform."""
        from .filters import PostAnalyticsFilter
        
        # Filter by Instagram
        filterset = PostAnalyticsFilter(
            data={'platform': 'instagram'},
            queryset=PostAnalytics.objects.all()
        )
        
        self.assertTrue(filterset.is_valid())
        filtered_qs = filterset.qs
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().platform, 'instagram')
    
    def test_date_range_filter(self):
        """Test filtering by date range."""
        from .filters import PostAnalyticsFilter
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Filter by date range
        filterset = PostAnalyticsFilter(
            data={
                'date_from': yesterday.strftime('%Y-%m-%d'),
                'date_to': yesterday.strftime('%Y-%m-%d')
            },
            queryset=PostAnalytics.objects.all()
        )
        
        self.assertTrue(filterset.is_valid())
        filtered_qs = filterset.qs
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().data_date, yesterday)
    
    def test_engagement_filter(self):
        """Test filtering by engagement metrics."""
        from .filters import PostAnalyticsFilter
        
        # Filter by minimum likes
        filterset = PostAnalyticsFilter(
            data={'likes_min': 75},
            queryset=PostAnalytics.objects.all()
        )
        
        self.assertTrue(filterset.is_valid())
        filtered_qs = filterset.qs
        self.assertEqual(filtered_qs.count(), 1)
        self.assertEqual(filtered_qs.first().likes, 100)

class AnalyticsCacheTest(TestCase):
    """Test cases for analytics caching functionality."""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_cache_analytics_data(self):
        """Test caching analytics data."""
        cache_key = 'test_analytics_data'
        test_data = {'total_posts': 10, 'total_engagement': 1000}
        
        # Cache data
        cache.set(cache_key, test_data, timeout=3600)
        
        # Retrieve cached data
        cached_data = cache.get(cache_key)
        self.assertEqual(cached_data, test_data)
    
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache_key = 'test_analytics_data'
        test_data = {'total_posts': 10}
        
        # Cache data
        cache.set(cache_key, test_data, timeout=3600)
        self.assertIsNotNone(cache.get(cache_key))
        
        # Invalidate cache
        cache.delete(cache_key)
        self.assertIsNone(cache.get(cache_key))
    
    def test_analytics_cache_model(self):
        """Test AnalyticsCache model functionality."""
        cache_data = {'user_analytics': {'posts': 5, 'engagement': 500}}
        expires_at = timezone.now() + timedelta(hours=1)
        
        # Create cache entry
        cache_entry = AnalyticsCache.objects.create(
            cache_key='user_123_analytics',
            data=cache_data,
            expires_at=expires_at
        )
        
        # Verify cache entry
        self.assertEqual(cache_entry.cache_key, 'user_123_analytics')
        self.assertEqual(cache_entry.data, cache_data)
        
        # Test retrieval
        retrieved_entry = AnalyticsCache.objects.get(cache_key='user_123_analytics')
        self.assertEqual(retrieved_entry.data, cache_data)
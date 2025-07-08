from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'posts', views.PostAnalyticsViewSet, basename='post-analytics')
router.register(r'users', views.UserAnalyticsViewSet, basename='user-analytics')
router.register(r'platforms', views.PlatformAnalyticsViewSet, basename='platform-analytics')
router.register(r'reports', views.AnalyticsReportViewSet, basename='analytics-reports')
router.register(r'insights', views.AnalyticsInsightViewSet, basename='analytics-insights')
router.register(r'dashboard', views.AnalyticsDashboardViewSet, basename='analytics-dashboard')

# Custom URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Post Analytics custom endpoints
    path('posts/<uuid:pk>/hourly/', 
         views.PostAnalyticsViewSet.as_view({'get': 'hourly_breakdown'}),
         name='post-analytics-hourly'),
    path('posts/<uuid:pk>/sync/', 
         views.PostAnalyticsViewSet.as_view({'post': 'sync'}),
         name='post-analytics-sync'),
    path('posts/<uuid:pk>/summary/', 
         views.PostAnalyticsViewSet.as_view({'get': 'summary'}),
         name='post-analytics-summary'),
    path('posts/bulk-sync/', 
         views.PostAnalyticsViewSet.as_view({'post': 'bulk_sync'}),
         name='post-analytics-bulk-sync'),
    
    # User Analytics custom endpoints
    path('users/<uuid:pk>/generate/', 
         views.UserAnalyticsViewSet.as_view({'post': 'generate'}),
         name='user-analytics-generate'),
    path('users/<uuid:pk>/summary/', 
         views.UserAnalyticsViewSet.as_view({'get': 'summary'}),
         name='user-analytics-summary'),
    path('users/<uuid:pk>/trends/', 
         views.UserAnalyticsViewSet.as_view({'get': 'trends'}),
         name='user-analytics-trends'),
    path('users/<uuid:pk>/export/', 
         views.UserAnalyticsViewSet.as_view({'post': 'export'}),
         name='user-analytics-export'),
    
    # Platform Analytics custom endpoints
    path('platforms/<uuid:pk>/sync/', 
         views.PlatformAnalyticsViewSet.as_view({'post': 'sync'}),
         name='platform-analytics-sync'),
    path('platforms/<uuid:pk>/compare/', 
         views.PlatformAnalyticsViewSet.as_view({'get': 'compare'}),
         name='platform-analytics-compare'),
    path('platforms/overview/', 
         views.PlatformAnalyticsViewSet.as_view({'get': 'overview'}),
         name='platform-analytics-overview'),
    
    # Analytics Reports custom endpoints
    path('reports/<uuid:pk>/generate/', 
         views.AnalyticsReportViewSet.as_view({'post': 'generate'}),
         name='analytics-reports-generate'),
    path('reports/<uuid:pk>/download/', 
         views.AnalyticsReportViewSet.as_view({'get': 'download'}),
         name='analytics-reports-download'),
    path('reports/<uuid:pk>/share/', 
         views.AnalyticsReportViewSet.as_view({'post': 'share'}),
         name='analytics-reports-share'),
    path('reports/<uuid:pk>/duplicate/', 
         views.AnalyticsReportViewSet.as_view({'post': 'duplicate'}),
         name='analytics-reports-duplicate'),
    path('reports/<uuid:pk>/schedule/', 
         views.AnalyticsReportViewSet.as_view({'post': 'schedule'}),
         name='analytics-reports-schedule'),
    path('reports/templates/', 
         views.AnalyticsReportViewSet.as_view({'get': 'templates'}),
         name='analytics-reports-templates'),
    
    # Analytics Insights custom endpoints
    path('insights/<uuid:pk>/dismiss/', 
         views.AnalyticsInsightViewSet.as_view({'post': 'dismiss'}),
         name='analytics-insights-dismiss'),
    path('insights/<uuid:pk>/action-taken/', 
         views.AnalyticsInsightViewSet.as_view({'post': 'mark_action_taken'}),
         name='analytics-insights-action-taken'),
    path('insights/generate/', 
         views.AnalyticsInsightViewSet.as_view({'post': 'generate'}),
         name='analytics-insights-generate'),
    path('insights/bulk-dismiss/', 
         views.AnalyticsInsightViewSet.as_view({'post': 'bulk_dismiss'}),
         name='analytics-insights-bulk-dismiss'),
    
    # Dashboard custom endpoints
    path('dashboard/overview/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'overview'}),
         name='analytics-dashboard-overview'),
    path('dashboard/top-posts/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'top_posts'}),
         name='analytics-dashboard-top-posts'),
    path('dashboard/recent-insights/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'recent_insights'}),
         name='analytics-dashboard-recent-insights'),
    path('dashboard/platform-performance/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'platform_performance'}),
         name='analytics-dashboard-platform-performance'),
    path('dashboard/engagement-chart/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'engagement_chart'}),
         name='analytics-dashboard-engagement-chart'),
    path('dashboard/reach-chart/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'reach_chart'}),
         name='analytics-dashboard-reach-chart'),
    path('dashboard/growth-chart/', 
         views.AnalyticsDashboardViewSet.as_view({'get': 'growth_chart'}),
         name='analytics-dashboard-growth-chart'),
    path('dashboard/export/', 
         views.AnalyticsDashboardViewSet.as_view({'post': 'export'}),
         name='analytics-dashboard-export'),
    
    # Analytics API endpoints
    path('api/metrics/', 
         views.analytics_metrics_api,
         name='analytics-metrics-api'),
    path('api/summary/', 
         views.analytics_summary_api,
         name='analytics-summary-api'),
    path('api/comparison/', 
         views.analytics_comparison_api,
         name='analytics-comparison-api'),
    path('api/export/', 
         views.analytics_export_api,
         name='analytics-export-api'),
    
    # Utility endpoints
    path('utils/validate-timeframe/', 
         views.validate_timeframe,
         name='analytics-validate-timeframe'),
    path('utils/available-metrics/', 
         views.available_metrics,
         name='analytics-available-metrics'),
    path('utils/platform-status/', 
         views.platform_status,
         name='analytics-platform-status'),
    path('utils/sync-status/', 
         views.sync_status,
         name='analytics-sync-status'),
    
    # Webhook endpoints for platform integrations
    path('webhooks/instagram/', 
         views.instagram_webhook,
         name='analytics-instagram-webhook'),
    path('webhooks/facebook/', 
         views.facebook_webhook,
         name='analytics-facebook-webhook'),
    path('webhooks/twitter/', 
         views.twitter_webhook,
         name='analytics-twitter-webhook'),
    path('webhooks/linkedin/', 
         views.linkedin_webhook,
         name='analytics-linkedin-webhook'),
    path('webhooks/tiktok/', 
         views.tiktok_webhook,
         name='analytics-tiktok-webhook'),
    path('webhooks/youtube/', 
         views.youtube_webhook,
         name='analytics-youtube-webhook'),
]

# Add app name for namespacing
app_name = 'analytics'
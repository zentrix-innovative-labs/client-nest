from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialAccountViewSet, PostAnalyticsViewSet, XConnectionTestView, XPostTestView, LinkedInConnectionTestView, LinkedInPostView, LinkedInUserInfoView, LinkedInImagePostView, FacebookConnectionTestView, SocialAccountsStatusView, XAndLinkedInConnectionTestView, CommentViewSet, x_env_test_view, youtube_channel_info, youtube_oauth_start, youtube_oauth_callback, youtube_upload_video, youtube_read_comments, youtube_feed
from .instagram_auth import InstagramAuthView, InstagramCallbackView
from .x_auth import XAuthView, XCallbackView
from .facebook_auth import FacebookAuthView, FacebookCallbackView
from .linkedin_auth import LinkedInAuthView, LinkedInCallbackView

router = DefaultRouter()
router.register(r'accounts', SocialAccountViewSet, basename='social-account')
router.register(r'analytics', PostAnalyticsViewSet, basename='post-analytics')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('instagram/auth/', InstagramAuthView.as_view(), name='instagram_auth'),
    path('instagram/callback/', InstagramCallbackView.as_view(), name='instagram_callback'),
    path('x/auth/', XAuthView.as_view(), name='x_auth'),
    path('x/callback/', XCallbackView.as_view(), name='x_callback'),
    path('x/test-connection/', XConnectionTestView.as_view(), name='x_test_connection'),
    path('x/test-post/', XPostTestView.as_view(), name='x_test_post'),
    path('facebook/auth/', FacebookAuthView.as_view(), name='facebook_auth'),
    path('facebook/callback/', FacebookCallbackView.as_view(), name='facebook_callback'),
    path('facebook/test-connection/', FacebookConnectionTestView.as_view(), name='facebook_test_connection'),
    path('linkedin/auth/', LinkedInAuthView.as_view(), name='linkedin_auth'),
    path('linkedin/callback/', LinkedInCallbackView.as_view(), name='linkedin_callback'),
    path('linkedin/test-connection/', LinkedInConnectionTestView.as_view(), name='linkedin_test_connection'),
    path('linkedin/post/', LinkedInPostView.as_view(), name='linkedin_post'),
    path('linkedin/userinfo/', LinkedInUserInfoView.as_view(), name='linkedin_userinfo'),
    path('linkedin/post-image/', LinkedInImagePostView.as_view(), name='linkedin_post_image'),
    path('accounts/status/', SocialAccountsStatusView.as_view(), name='social_accounts_status'),
    path('x-linkedin/test-connection/', XAndLinkedInConnectionTestView.as_view(), name='x_linkedin_test_connection'),
    path('x/env-test/', x_env_test_view, name='x_env_test'),
    path('youtube/channel/<str:channel_id>/', youtube_channel_info, name='youtube_channel_info'),
    path('youtube/oauth/start/', youtube_oauth_start, name='youtube_oauth_start'),
    path('youtube/callback/', youtube_oauth_callback, name='youtube_oauth_callback'),
    path('youtube/upload/', youtube_upload_video, name='youtube_upload_video'),
    path('youtube/comments/', youtube_read_comments, name='youtube_read_comments'),
    path('youtube/feed/', youtube_feed, name='youtube_feed'),
] 
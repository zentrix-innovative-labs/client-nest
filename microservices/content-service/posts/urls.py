from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    SocialAccountViewSet,
    PostMediaViewSet,
    CommentListView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'social-accounts', SocialAccountViewSet, basename='socialaccount')
router.register(r'media', PostMediaViewSet, basename='postmedia')

# URL patterns
urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Custom endpoints
    path('posts/<uuid:post_id>/platforms/<uuid:platform_id>/comments/', 
         CommentListView.as_view(), 
         name='post-platform-comments'),
    
    # Post management endpoints
    path('posts/<uuid:pk>/publish/', 
         PostViewSet.as_view({'post': 'publish'}), 
         name='post-publish'),
    
    path('posts/<uuid:pk>/schedule/', 
         PostViewSet.as_view({'post': 'schedule'}), 
         name='post-schedule'),
    
    path('posts/<uuid:pk>/cancel-schedule/', 
         PostViewSet.as_view({'post': 'cancel_schedule'}), 
         name='post-cancel-schedule'),
    
    path('posts/<uuid:pk>/duplicate/', 
         PostViewSet.as_view({'post': 'duplicate'}), 
         name='post-duplicate'),
    
    path('posts/<uuid:pk>/analytics/', 
         PostViewSet.as_view({'get': 'analytics'}), 
         name='post-analytics'),
    
    # Social account management
    path('social-accounts/<uuid:pk>/test-connection/', 
         SocialAccountViewSet.as_view({'post': 'test_connection'}), 
         name='social-account-test'),
    
    path('social-accounts/<uuid:pk>/refresh-token/', 
         SocialAccountViewSet.as_view({'post': 'refresh_token'}), 
         name='social-account-refresh'),
]

# Add app name for namespacing
app_name = 'posts'
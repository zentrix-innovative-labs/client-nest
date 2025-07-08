from rest_framework import generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import (
    Post, PostMedia, SocialAccount, PostPlatform, Comment,
    PostStatus, SocialPlatform
)
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    PostListSerializer, PostMediaSerializer, SocialAccountSerializer,
    PostPlatformSerializer, CommentSerializer, PostAnalyticsSerializer
)
from .permissions import IsOwnerOrReadOnly
from .filters import PostFilter
from .tasks import publish_post_task, schedule_post_task
import logging

logger = logging.getLogger(__name__)

class PostViewSet(ModelViewSet):
    """
    ViewSet for managing posts
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'hashtags']
    ordering_fields = ['created_at', 'updated_at', 'published_at', 'scheduled_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter posts by current user"""
        return Post.objects.filter(user=self.request.user).prefetch_related(
            'media', 'platforms__social_account'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        elif self.action == 'list':
            return PostListSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set user when creating post"""
        post = serializer.save(user=self.request.user)
        
        # If post is scheduled, create Celery task
        if post.status == PostStatus.SCHEDULED and post.scheduled_at:
            schedule_post_task.apply_async(
                args=[str(post.id)],
                eta=post.scheduled_at
            )
            logger.info(f"Scheduled post {post.id} for {post.scheduled_at}")
        
        # If post is set to publish immediately
        elif post.status == PostStatus.PUBLISHED:
            publish_post_task.delay(str(post.id))
            logger.info(f"Queued post {post.id} for immediate publishing")
    
    @extend_schema(
        summary="Publish a post immediately",
        description="Publish a draft or scheduled post to all configured platforms"
    )
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a post immediately"""
        post = self.get_object()
        
        if post.status == PostStatus.PUBLISHED:
            return Response(
                {'error': 'Post is already published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if post.status == PostStatus.FAILED:
            return Response(
                {'error': 'Cannot publish failed post. Please edit and try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update post status and queue for publishing
        post.status = PostStatus.PUBLISHED
        post.save()
        
        publish_post_task.delay(str(post.id))
        
        return Response(
            {'message': 'Post queued for publishing'},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Schedule a post",
        description="Schedule a post for future publishing",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'scheduled_at': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'ISO 8601 datetime for scheduling'
                    }
                },
                'required': ['scheduled_at']
            }
        }
    )
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a post for future publishing"""
        post = self.get_object()
        scheduled_at = request.data.get('scheduled_at')
        
        if not scheduled_at:
            return Response(
                {'error': 'scheduled_at is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.utils.dateparse import parse_datetime
            scheduled_datetime = parse_datetime(scheduled_at)
            
            if not scheduled_datetime:
                return Response(
                    {'error': 'Invalid datetime format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if scheduled_datetime <= timezone.now():
                return Response(
                    {'error': 'Scheduled time must be in the future'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            post.scheduled_at = scheduled_datetime
            post.status = PostStatus.SCHEDULED
            post.save()
            
            # Create Celery task
            schedule_post_task.apply_async(
                args=[str(post.id)],
                eta=scheduled_datetime
            )
            
            return Response(
                {'message': f'Post scheduled for {scheduled_datetime}'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error scheduling post {post.id}: {str(e)}")
            return Response(
                {'error': 'Failed to schedule post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Cancel scheduled post",
        description="Cancel a scheduled post and revert to draft"
    )
    @action(detail=True, methods=['post'])
    def cancel_schedule(self, request, pk=None):
        """Cancel a scheduled post"""
        post = self.get_object()
        
        if post.status != PostStatus.SCHEDULED:
            return Response(
                {'error': 'Post is not scheduled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.status = PostStatus.DRAFT
        post.scheduled_at = None
        post.save()
        
        # TODO: Cancel Celery task if possible
        
        return Response(
            {'message': 'Post schedule cancelled'},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Duplicate a post",
        description="Create a copy of an existing post as a draft"
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a post"""
        original_post = self.get_object()
        
        # Create new post with same content
        new_post = Post.objects.create(
            user=original_post.user,
            title=f"{original_post.title} (Copy)" if original_post.title else "Untitled (Copy)",
            content=original_post.content,
            post_type=original_post.post_type,
            status=PostStatus.DRAFT,
            hashtags=original_post.hashtags.copy(),
            mentions=original_post.mentions.copy(),
            location=original_post.location.copy(),
            allow_comments=original_post.allow_comments,
            allow_sharing=original_post.allow_sharing,
            metadata=original_post.metadata.copy()
        )
        
        # Copy media
        for media in original_post.media.all():
            PostMedia.objects.create(
                post=new_post,
                file_url=media.file_url,
                file_type=media.file_type,
                file_size=media.file_size,
                width=media.width,
                height=media.height,
                duration=media.duration,
                thumbnail_url=media.thumbnail_url,
                alt_text=media.alt_text,
                order=media.order,
                metadata=media.metadata.copy()
            )
        
        serializer = PostSerializer(new_post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get post analytics",
        description="Get analytics data for user's posts",
        parameters=[
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of days to include (default: 30)'
            ),
            OpenApiParameter(
                name='platform',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by platform'
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get post analytics"""
        days = int(request.query_params.get('days', 30))
        platform = request.query_params.get('platform')
        
        # Filter posts by date range
        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=days)
        posts_queryset = self.get_queryset().filter(created_at__gte=start_date)
        
        if platform:
            posts_queryset = posts_queryset.filter(
                platforms__social_account__platform=platform
            )
        
        # Calculate analytics
        analytics_data = {
            'total_posts': posts_queryset.count(),
            'published_posts': posts_queryset.filter(status=PostStatus.PUBLISHED).count(),
            'scheduled_posts': posts_queryset.filter(status=PostStatus.SCHEDULED).count(),
            'draft_posts': posts_queryset.filter(status=PostStatus.DRAFT).count(),
            'failed_posts': posts_queryset.filter(status=PostStatus.FAILED).count(),
            'total_views': posts_queryset.aggregate(Sum('view_count'))['view_count__sum'] or 0,
            'total_likes': posts_queryset.aggregate(Sum('like_count'))['like_count__sum'] or 0,
            'total_comments': posts_queryset.aggregate(Sum('comment_count'))['comment_count__sum'] or 0,
            'total_shares': posts_queryset.aggregate(Sum('share_count'))['share_count__sum'] or 0,
            'average_engagement_rate': posts_queryset.aggregate(
                Avg('view_count')
            )['view_count__avg'] or 0,
            'top_performing_posts': posts_queryset.order_by('-view_count')[:5],
            'platform_breakdown': self._get_platform_breakdown(posts_queryset),
            'posting_frequency': self._get_posting_frequency(posts_queryset, days)
        }
        
        serializer = PostAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
    
    def _get_platform_breakdown(self, posts_queryset):
        """Get breakdown by platform"""
        breakdown = {}
        for platform_choice in SocialPlatform.choices:
            platform = platform_choice[0]
            count = posts_queryset.filter(
                platforms__social_account__platform=platform
            ).count()
            breakdown[platform] = count
        return breakdown
    
    def _get_posting_frequency(self, posts_queryset, days):
        """Get posting frequency data"""
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        frequency_data = posts_queryset.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return {
            'daily_average': posts_queryset.count() / days if days > 0 else 0,
            'daily_breakdown': list(frequency_data)
        }

class SocialAccountViewSet(ModelViewSet):
    """
    ViewSet for managing social media accounts
    """
    serializer_class = SocialAccountSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['platform', 'is_active']
    ordering_fields = ['created_at', 'platform']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter accounts by current user"""
        return SocialAccount.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user when creating account"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        summary="Test account connection",
        description="Test if the social account connection is working"
    )
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test social account connection"""
        account = self.get_object()
        
        # TODO: Implement platform-specific connection testing
        # This would involve making API calls to each platform
        
        return Response(
            {'message': 'Connection test not implemented yet'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    @extend_schema(
        summary="Refresh account token",
        description="Refresh the access token for the social account"
    )
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh account access token"""
        account = self.get_object()
        
        # TODO: Implement platform-specific token refresh
        # This would involve using refresh tokens to get new access tokens
        
        return Response(
            {'message': 'Token refresh not implemented yet'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )

class PostMediaViewSet(ModelViewSet):
    """
    ViewSet for managing post media
    """
    serializer_class = PostMediaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter media by post owner"""
        return PostMedia.objects.filter(post__user=self.request.user)

class CommentListView(generics.ListAPIView):
    """
    List comments for a specific post platform
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_reply', 'is_spam', 'is_hidden']
    ordering_fields = ['platform_created_at', 'like_count']
    ordering = ['-platform_created_at']
    
    def get_queryset(self):
        """Filter comments by post platform"""
        post_platform_id = self.kwargs.get('post_platform_id')
        return Comment.objects.filter(
            post_platform_id=post_platform_id,
            post_platform__post__user=self.request.user
        )
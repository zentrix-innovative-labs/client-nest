from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models_minimal import Post
from .serializers_minimal import PostSerializer, PostCreateSerializer, PostUpdateSerializer

class PostViewSet(viewsets.ModelViewSet):
    """Minimal ViewSet for managing posts"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter posts by current user"""
        return Post.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set user when creating post"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a post immediately"""
        post = self.get_object()
        
        if post.status == 'published':
            return Response(
                {'error': 'Post is already published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        
        return Response(
            {'message': 'Post published successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a post"""
        post = self.get_object()
        post.like_count = F('like_count') + 1
        post.save()
        post.refresh_from_db()  # Ensure updated value is fetched from the database
        
        return Response(
            {'message': 'Post liked', 'like_count': post.like_count},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        post = self.get_object()
        post.view_count = F('view_count') + 1
        post.save(update_fields=['view_count'])
        
        return Response(
            {'message': 'View counted', 'view_count': post.view_count},
            status=status.HTTP_200_OK
        ) 
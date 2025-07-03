from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Count
from .models import Post, Schedule, Comment, CommentLike
from .serializers import PostSerializer, ScheduleSerializer, CommentSerializer, CommentUpdateSerializer, CommentLikeSerializer
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from .utils import toggle_comment_like
from django.db import models

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user']
    search_fields = ['content']
    ordering_fields = ['created_at', 'published_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).annotate(comment_count=Count('comments'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        post = self.get_object()
        platform = request.data.get('platform')
        scheduled_time = request.data.get('scheduled_time')

        if not platform or not scheduled_time:
            return Response(
                {'error': 'Platform and scheduled_time are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        schedule = Schedule.objects.create(
            post=post,
            platform=platform,
            scheduled_time=scheduled_time
        )
        post.status = 'scheduled'
        post.save()

        return Response(ScheduleSerializer(schedule).data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        post = self.get_object()
        if post.status != 'scheduled':
            return Response(
                {'error': 'Only scheduled posts can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )

        post.status = 'published'
        post.published_at = timezone.now()
        post.save()

        return Response(PostSerializer(post).data)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'parent_comment']
    search_fields = ['content']
    ordering_fields = ['created_at', 'like_count']
    ordering = ['created_at']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # Show comments from posts the user can access (their own posts, public posts, or shared posts)
        qs = Comment.objects.filter(
            Q(post__user=self.request.user) | Q(post__status='published')
        ).select_related('author', 'post', 'parent_comment').prefetch_related('replies')
        user = self.request.user
        if user.is_authenticated:
            qs = qs.annotate(
                is_liked_by_user=models.Exists(
                    CommentLike.objects.filter(comment=models.OuterRef('pk'), user=user)
                )
            )
        return qs

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Ensure only the author can edit
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Only the comment author can edit this comment.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure only the author can delete
        if instance.author != self.request.user:
            raise PermissionDenied("Only the comment author can delete this comment.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        """Get current user's comments"""
        comments = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a comment"""
        comment = self.get_object()
        user = request.user
        action, like_count = toggle_comment_like(comment, user)
        return Response({
            'action': action,
            'like_count': like_count
        })

class CommentLikeViewSet(viewsets.ModelViewSet):
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommentLike.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # If unliked, return 204 No Content
        if getattr(serializer, '_unliked', False):
            return Response(status=status.HTTP_204_NO_CONTENT)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        # Get the comment before deleting the like
        comment = instance.comment
        with transaction.atomic():
            # Delete the like
            instance.delete()
            # Atomically decrement the comment's like count
            comment.like_count = F('like_count') - 1
            comment.save(update_fields=['like_count'])
            comment.refresh_from_db(fields=['like_count'])

class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Schedule.objects.filter(post__user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_published(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_published = True
        schedule.save()
        return Response(ScheduleSerializer(schedule).data)

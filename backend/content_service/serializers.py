from rest_framework import serializers
from .models import Post, Schedule, Comment, CommentLike
from users.serializers import UserSerializer 

from django.db.models import F
from django.db import transaction
from .utils import toggle_comment_like

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'post', 'platform', 'scheduled_time', 'is_published', 'created_at']
        read_only_fields = ['created_at']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'media_files', 'status', 'scheduled_time', 
                 'published_at', 'created_at', 'updated_at', 'comment_count']
        read_only_fields = ['created_at', 'updated_at', 'published_at']

    def get_comment_count(self, obj):
        return getattr(obj, 'comment_count', 0)

class IsLikedByUserMixin:
    def get_is_liked_by_user(self, obj):
        # Prefer the annotated flag if present
        value = getattr(obj, 'is_liked_by_user', None)
        if value is not None:
            return value
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

class CommentReplySerializer(IsLikedByUserMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent_comment', 'content', 'media_files',
                 'like_count', 'mentions', 'is_edited', 'edited_at',
                 'is_liked_by_user', 'created_at', 'updated_at']
        read_only_fields = ['author', 'like_count', 'is_edited', 'edited_at', 
                           'created_at', 'updated_at']

class CommentSerializer(IsLikedByUserMixin, serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    parent_comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = Comment
        ref_name = "ContentAppComment"
        fields = ['id', 'post', 'author', 'parent_comment', 'content', 'media_files',
                 'like_count', 'mentions', 'is_edited', 'edited_at', 'replies',
                 'is_liked_by_user', 'created_at', 'updated_at']
        read_only_fields = ['author', 'like_count', 'is_edited', 'edited_at', 
                           'created_at', 'updated_at']

    def get_replies(self, obj):
        # Only get direct replies (not nested replies to avoid infinite recursion)
        replies = obj.replies.all()
        return CommentReplySerializer(replies, many=True, context=self.context).data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'media_files']
        read_only_fields = ['author']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['comment', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        comment = validated_data['comment']
        user = validated_data['user']
        action, _ = toggle_comment_like(comment, user)
        # Return the CommentLike instance if liked, or a structured response if unliked
        if action == 'liked':
            return CommentLike.objects.get(comment=comment, user=user)
        else:
            # If unliked, return None or a structured response
            self._unliked = True  # Set a flag for the view to handle 204/response
            return None 

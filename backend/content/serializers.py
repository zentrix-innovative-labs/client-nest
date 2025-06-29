from rest_framework import serializers
from .models import Post, Schedule, Comment, CommentLike
from users.serializers import UserSerializer

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
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
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
        fields = ['id', 'post', 'author', 'parent_comment', 'content', 'media_files',
                 'like_count', 'mentions', 'is_edited', 'edited_at', 'replies',
                 'is_liked_by_user', 'created_at', 'updated_at']
        read_only_fields = ['author', 'like_count', 'is_edited', 'edited_at', 
                           'created_at', 'updated_at']

    def get_replies(self, obj):
        # Only get direct replies (not nested replies to avoid infinite recursion)
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'media_files']
        read_only_fields = ['author', 'post', 'parent_comment']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['comment', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        comment_like, created = CommentLike.objects.get_or_create(**validated_data)
        
        if created:
            # Update like count
            comment = validated_data['comment']
            comment.like_count = comment.likes.count()
            comment.save()
        
        return comment_like 
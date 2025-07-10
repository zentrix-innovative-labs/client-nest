from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import (
    Post, PostMedia, SocialAccount, PostPlatform, Comment,
    PostStatus, SocialPlatform, PostType
)
import re

User = get_user_model()

class SocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for social media accounts"""
    is_token_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = SocialAccount
        fields = [
            'id', 'platform', 'account_id', 'username', 'display_name',
            'profile_picture', 'is_active', 'permissions', 'is_token_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_token_expired']
    
    def validate_platform(self, value):
        """Validate platform choice"""
        if value not in [choice[0] for choice in SocialPlatform.choices]:
            raise serializers.ValidationError("Invalid platform choice.")
        return value

class PostMediaSerializer(serializers.ModelSerializer):
    """Serializer for post media"""
    
    class Meta:
        model = PostMedia
        fields = [
            'id', 'file_url', 'file_type', 'file_size', 'width', 'height',
            'duration', 'thumbnail_url', 'alt_text', 'order', 'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_file_type(self, value):
        """Validate file type"""
        allowed_types = ['image', 'video', 'gif']
        if value not in allowed_types:
            raise serializers.ValidationError(f"File type must be one of: {', '.join(allowed_types)}")
        return value
    
    def validate_file_size(self, value):
        """Validate file size (max 100MB)"""
        max_size = 100 * 1024 * 1024  # 100MB in bytes
        if value > max_size:
            raise serializers.ValidationError("File size cannot exceed 100MB.")
        return value

class PostPlatformSerializer(serializers.ModelSerializer):
    """Serializer for post platform relationships"""
    social_account = SocialAccountSerializer(read_only=True)
    social_account_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = PostPlatform
        fields = [
            'id', 'social_account', 'social_account_id', 'platform_post_id',
            'platform_url', 'status', 'published_at', 'error_message',
            'platform_analytics', 'last_analytics_update', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'platform_post_id', 'platform_url', 'platform_analytics',
            'last_analytics_update', 'created_at', 'updated_at'
        ]

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    
    class Meta:
        model = Comment
        fields = [
            'id', 'platform_comment_id', 'author_name', 'author_username',
            'author_profile_url', 'content', 'like_count', 'reply_count',
            'is_reply', 'parent_comment_id', 'sentiment_score', 'is_spam',
            'is_hidden', 'platform_created_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'platform_comment_id', 'like_count', 'reply_count',
            'sentiment_score', 'created_at', 'updated_at'
        ]

class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    media = PostMediaSerializer(many=True, required=False)
    platforms = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of social account IDs to publish to"
    )
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'post_type', 'status', 'scheduled_at',
            'hashtags', 'mentions', 'location', 'allow_comments', 'allow_sharing',
            'metadata', 'media', 'platforms'
        ]
        read_only_fields = ['id']
    
    def validate_content(self, value):
        """Validate post content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        
        if len(value) > 10000:
            raise serializers.ValidationError("Content cannot exceed 10,000 characters.")
        
        return value.strip()
    
    def validate_hashtags(self, value):
        """Validate hashtags"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Hashtags must be a list.")
        
        if len(value) > 30:
            raise serializers.ValidationError("Cannot have more than 30 hashtags.")
        
        # Validate hashtag format
        hashtag_pattern = re.compile(r'^[a-zA-Z0-9_]+$')
        for hashtag in value:
            if not isinstance(hashtag, str):
                raise serializers.ValidationError("All hashtags must be strings.")
            if not hashtag_pattern.match(hashtag):
                raise serializers.ValidationError(
                    f"Invalid hashtag '{hashtag}'. Use only letters, numbers, and underscores."
                )
            if len(hashtag) > 100:
                raise serializers.ValidationError(f"Hashtag '{hashtag}' is too long (max 100 characters).")
        
        return value
    
    def validate_scheduled_at(self, value):
        """Validate scheduled time"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        status = attrs.get('status')
        scheduled_at = attrs.get('scheduled_at')
        
        # If status is scheduled, scheduled_at is required
        if status == PostStatus.SCHEDULED and not scheduled_at:
            raise serializers.ValidationError({
                'scheduled_at': 'Scheduled time is required for scheduled posts.'
            })
        
        # If status is not scheduled, scheduled_at should be None
        if status != PostStatus.SCHEDULED and scheduled_at:
            raise serializers.ValidationError({
                'scheduled_at': 'Scheduled time should only be set for scheduled posts.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create post with media and platform relationships"""
        media_data = validated_data.pop('media', [])
        platforms_data = validated_data.pop('platforms', [])
        
        # Create the post
        post = Post.objects.create(**validated_data)
        
        # Create media objects
        for media_item in media_data:
            PostMedia.objects.create(post=post, **media_item)
        
        # Create platform relationships
        for social_account_id in platforms_data:
            try:
                social_account = SocialAccount.objects.get(
                    id=social_account_id,
                    user=post.user,
                    is_active=True
                )
                PostPlatform.objects.create(
                    post=post,
                    social_account=social_account,
                    status=post.status
                )
            except SocialAccount.DoesNotExist:
                # Log error but don't fail the entire creation
                pass
        
        return post

class PostSerializer(serializers.ModelSerializer):
    """Serializer for reading posts"""
    media = PostMediaSerializer(many=True, read_only=True)
    platforms = PostPlatformSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    is_scheduled = serializers.ReadOnlyField()
    is_published = serializers.ReadOnlyField()
    engagement_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'title', 'content', 'post_type', 'status',
            'scheduled_at', 'published_at', 'hashtags', 'mentions', 'location',
            'allow_comments', 'allow_sharing', 'view_count', 'like_count',
            'comment_count', 'share_count', 'metadata', 'error_message',
            'created_at', 'updated_at', 'media', 'platforms', 'is_scheduled',
            'is_published', 'engagement_rate'
        ]
        read_only_fields = [
            'id', 'user', 'published_at', 'view_count', 'like_count',
            'comment_count', 'share_count', 'error_message', 'created_at',
            'updated_at', 'is_scheduled', 'is_published', 'engagement_rate'
        ]

class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts"""
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'post_type', 'status', 'scheduled_at',
            'hashtags', 'mentions', 'location', 'allow_comments', 'allow_sharing',
            'metadata'
        ]
    
    def validate_content(self, value):
        """Validate post content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        
        if len(value) > 10000:
            raise serializers.ValidationError("Content cannot exceed 10,000 characters.")
        
        return value.strip()
    
    def validate(self, attrs):
        """Validate that published posts cannot be modified"""
        if self.instance and self.instance.status == PostStatus.PUBLISHED:
            # Only allow certain fields to be updated for published posts
            allowed_fields = {'metadata'}
            provided_fields = set(attrs.keys())
            
            if not provided_fields.issubset(allowed_fields):
                raise serializers.ValidationError(
                    "Published posts can only have metadata updated."
                )
        
        return attrs

class PostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for post lists"""
    media_count = serializers.SerializerMethodField()
    platform_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'post_type', 'status', 'scheduled_at',
            'published_at', 'view_count', 'like_count', 'comment_count',
            'share_count', 'created_at', 'updated_at', 'media_count',
            'platform_count'
        ]
        read_only_fields = '__all__'
    
    def get_media_count(self, obj):
        """Get number of media files"""
        return obj.media.count()
    
    def get_platform_count(self, obj):
        """Get number of platforms"""
        return obj.platforms.count()

class PostAnalyticsSerializer(serializers.Serializer):
    """Serializer for post analytics data"""
    total_posts = serializers.IntegerField()
    published_posts = serializers.IntegerField()
    scheduled_posts = serializers.IntegerField()
    draft_posts = serializers.IntegerField()
    failed_posts = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_shares = serializers.IntegerField()
    average_engagement_rate = serializers.FloatField()
    top_performing_posts = PostListSerializer(many=True)
    platform_breakdown = serializers.DictField()
    posting_frequency = serializers.DictField()
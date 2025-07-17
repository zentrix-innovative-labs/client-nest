from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.urls import reverse
import uuid
import json
from enum import Choices

User = get_user_model()

class PostStatus(models.TextChoices):
    """Post status choices"""
    DRAFT = 'draft', 'Draft'
    SCHEDULED = 'scheduled', 'Scheduled'
    PUBLISHED = 'published', 'Published'
    FAILED = 'failed', 'Failed'
    ARCHIVED = 'archived', 'Archived'

class SocialPlatform(models.TextChoices):
    """Supported social media platforms"""
    FACEBOOK = 'facebook', 'Facebook'
    INSTAGRAM = 'instagram', 'Instagram'
    TWITTER = 'twitter', 'Twitter'
    LINKEDIN = 'linkedin', 'LinkedIn'
    YOUTUBE = 'youtube', 'YouTube'
    TIKTOK = 'tiktok', 'TikTok'

class PostType(models.TextChoices):
    """Post type choices"""
    TEXT = 'text', 'Text Only'
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Video'
    CAROUSEL = 'carousel', 'Carousel'
    STORY = 'story', 'Story'
    REEL = 'reel', 'Reel'

class SocialAccount(models.Model):
    """Social media account model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=SocialPlatform.choices)
    account_id = models.CharField(max_length=100)  # Platform-specific account ID
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True)
    profile_picture = models.URLField(blank=True)
    access_token = models.TextField()  # Encrypted in production
    refresh_token = models.TextField(blank=True)  # For platforms that support it
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(default=dict)  # Platform-specific permissions
    metadata = models.JSONField(default=dict)  # Additional platform data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform', 'account_id']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['platform', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.platform.title()} - {self.username}"
    
    @property
    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        return timezone.now() >= self.token_expires_at

class Post(models.Model):
    """Main post model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(
        validators=[
            MinLengthValidator(1),
            MaxLengthValidator(10000)
        ]
    )
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.TEXT)
    status = models.CharField(max_length=20, choices=PostStatus.choices, default=PostStatus.DRAFT)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Social media specific
    hashtags = models.JSONField(default=list)  # List of hashtags
    mentions = models.JSONField(default=list)  # List of mentions
    location = models.JSONField(default=dict, blank=True)  # Location data
    
    # Engagement settings
    allow_comments = models.BooleanField(default=True)
    allow_sharing = models.BooleanField(default=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Additional post data
    error_message = models.TextField(blank=True)  # Error details if failed
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.status}"
    
    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'pk': self.pk})
    
    @property
    def is_scheduled(self):
        """Check if post is scheduled for future"""
        return (
            self.status == PostStatus.SCHEDULED and 
            self.scheduled_at and 
            self.scheduled_at > timezone.now()
        )
    
    @property
    def is_published(self):
        """Check if post is published"""
        return self.status == PostStatus.PUBLISHED
    
    @property
    def engagement_rate(self):
        """Calculate engagement rate"""
        if self.view_count == 0:
            return 0
        total_engagement = self.like_count + self.comment_count + self.share_count
        return (total_engagement / self.view_count) * 100

class PostMedia(models.Model):
    """Media files associated with posts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file_url = models.URLField()  # S3 or CDN URL
    file_type = models.CharField(max_length=20)  # image, video, gif
    file_size = models.PositiveIntegerField()  # Size in bytes
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # For videos in seconds
    thumbnail_url = models.URLField(blank=True)  # Thumbnail for videos
    alt_text = models.CharField(max_length=500, blank=True)  # Accessibility
    order = models.PositiveIntegerField(default=0)  # Order in carousel
    metadata = models.JSONField(default=dict)  # Additional media data
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['post', 'order']),
            models.Index(fields=['file_type']),
        ]
    
    def __str__(self):
        return f"{self.post.title} - {self.file_type}"

class PostPlatform(models.Model):
    """Many-to-many relationship between posts and social platforms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='platforms')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    platform_post_id = models.CharField(max_length=100, blank=True)  # Platform-specific post ID
    platform_url = models.URLField(blank=True)  # Direct link to post
    status = models.CharField(max_length=20, choices=PostStatus.choices, default=PostStatus.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Platform-specific analytics
    platform_analytics = models.JSONField(default=dict)
    last_analytics_update = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['post', 'social_account']
        indexes = [
            models.Index(fields=['post', 'status']),
            models.Index(fields=['social_account', 'status']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return f"{self.post.title} on {self.social_account.platform}"

class Comment(models.Model):
    """Comments on posts (from social platforms)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_platform = models.ForeignKey(PostPlatform, on_delete=models.CASCADE, related_name='comments')
    platform_comment_id = models.CharField(max_length=100)  # Platform-specific comment ID
    author_name = models.CharField(max_length=200)
    author_username = models.CharField(max_length=100, blank=True)
    author_profile_url = models.URLField(blank=True)
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    is_reply = models.BooleanField(default=False)
    parent_comment_id = models.CharField(max_length=100, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)  # AI sentiment analysis
    is_spam = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    platform_created_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['post_platform', 'platform_comment_id']
        ordering = ['-platform_created_at']
        indexes = [
            models.Index(fields=['post_platform', 'is_reply']),
            models.Index(fields=['platform_created_at']),
            models.Index(fields=['sentiment_score']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.post_platform.post.title}"
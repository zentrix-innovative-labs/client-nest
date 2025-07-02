from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    media_files = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed')
    ], default='draft')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.content[:50]}"

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    media_files = models.JSONField(default=list)
    like_count = models.IntegerField(default=0)
    mentions = models.JSONField(default=list)  # List of mentioned user IDs
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} on {self.post.id}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        # Mark as edited if content changed and not a new comment
        if self.pk:
            try:
                old_comment = Comment.objects.get(pk=self.pk)
                if self.content != old_comment.content:
                    self.is_edited = True
                    from django.utils import timezone
                    self.edited_at = timezone.now()
            except Comment.DoesNotExist:
                # This is a new comment, no need to check for changes
                pass
        super().save(*args, **kwargs)

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['comment', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.comment.id}"

class Schedule(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='schedules')
    platform = models.CharField(max_length=20)
    scheduled_time = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f"{self.post.id} - {self.platform} - {self.scheduled_time}"

# microservices/ai-service/content_generation/models.py
from django.db import models
from django.conf import settings
import decimal

class AIUsageLog(models.Model):
    """
    Logs each AI API call for analytics and cost management.
    This fulfills Onyait Elias's task for cost tracking.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_usage_logs'
    )
    request_type = models.CharField(max_length=100)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0, help_text="Cost in USD")
    response_time_ms = models.PositiveIntegerField(help_text="Response time in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_type} for {self.user.username if self.user else 'Anonymous'} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']

class GeneratedContent(models.Model):
    """
    Stores generated content for caching and reuse.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_content'
    )
    topic = models.CharField(max_length=500)
    platform = models.CharField(max_length=50)
    tone = models.CharField(max_length=50)
    content = models.TextField()
    hashtags = models.JSONField(default=list)
    call_to_action = models.TextField(blank=True)
    suggestions = models.JSONField(default=list)
    variations = models.JSONField(default=list)
    quality_score = models.IntegerField()
    safety_check = models.JSONField()
    readability_score = models.FloatField()
    engagement_prediction = models.CharField(max_length=20)
    optimal_posting_time_suggestion = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.platform} content for {self.user.username} - {self.topic[:50]}"

    class Meta:
        ordering = ['-created_at']

class ContentTemplate(models.Model):
    """
    Reusable content templates for different platforms and use cases.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    platform = models.CharField(max_length=50)
    tone = models.CharField(max_length=50)
    template_prompt = models.TextField()
    variables = models.JSONField(default=dict, help_text="Template variables and their descriptions")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='content_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.platform}"

    class Meta:
        ordering = ['-created_at'] 
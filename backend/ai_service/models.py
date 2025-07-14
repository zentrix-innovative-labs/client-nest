from django.db import models
from django.conf import settings

class AIModel(models.Model):
    """
    Model for AI models used in the system
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

class AITask(models.Model):
    """
    Model for AI tasks
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_tasks')
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model.name} task for {self.user.username} at {self.created_at}"

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

class UserTaskMapping(models.Model):
    """
    Stores a mapping between a Celery task ID and the user who initiated it.
    This is used to enforce ownership and security for task status polling.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.task_id}"

    class Meta:
        ordering = ['-created_at']

from django.db import models
from django.conf import settings

# Create your models here.

class Report(models.Model):
    REPORT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending')
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.report_type} - {self.user} - {self.status} @ {self.generated_at}"

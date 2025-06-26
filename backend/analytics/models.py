from django.db import models
from django.conf import settings

class AnalyticsData(models.Model):
    """
    Model for storing analytics data
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics_data')
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.metric_name} at {self.timestamp}"

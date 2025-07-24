from django.db import models
from django.conf import settings

# Create your models here.

class RawEvent(models.Model):
    event_type = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.platform} - {self.timestamp}"

class AggregatedMetric(models.Model):
    metric_type = models.CharField(max_length=100)
    value = models.FloatField()
    period = models.DateField()
    platform = models.CharField(max_length=50)
    extra = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.metric_type} - {self.platform} - {self.period}"

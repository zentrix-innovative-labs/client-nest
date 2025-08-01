from django.db import models

class AnalyticsEvent(models.Model):
    event_type = models.CharField(max_length=100)
    user_id = models.IntegerField()
    platform = models.CharField(max_length=50)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.platform} - {self.timestamp}"

class AggregatedMetrics(models.Model):
    date = models.DateField()
    metric_type = models.CharField(max_length=100)
    value = models.FloatField()
    platform = models.CharField(max_length=50)
    extra = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.metric_type} - {self.platform} - {self.date}"

class Report(models.Model):
    user_id = models.IntegerField()
    report_type = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f"{self.report_type} - {self.user_id} - {self.generated_at}" 
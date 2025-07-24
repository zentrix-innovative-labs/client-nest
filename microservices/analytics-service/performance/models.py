from django.db import models

# Create your models here.

class APIMetric(models.Model):
    endpoint = models.CharField(max_length=255)
    response_time_ms = models.FloatField()
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.endpoint} - {self.status_code} - {self.response_time_ms}ms @ {self.timestamp}"

class ErrorLog(models.Model):
    endpoint = models.CharField(max_length=255)
    error_type = models.CharField(max_length=100)
    message = models.TextField()
    status_code = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.endpoint} - {self.error_type} @ {self.timestamp}"

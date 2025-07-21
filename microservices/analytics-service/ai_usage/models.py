from django.db import models
from django.conf import settings

# Create your models here.

class AIUsageLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    operation = models.CharField(max_length=100)  # e.g., 'prediction', 'insight'
    model_name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=4)
    duration_ms = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.operation} - {self.model_name} @ {self.timestamp}"

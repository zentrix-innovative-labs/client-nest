from django.db import models
from django.utils import timezone
import uuid

class ServiceRegistry(models.Model):
    """
    Model to track registered microservices
    """
    SERVICE_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('unhealthy', 'Unhealthy'),
        ('maintenance', 'Maintenance'),
        ('unknown', 'Unknown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField()
    health_check_endpoint = models.CharField(max_length=200, default='/health/')
    version = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=SERVICE_STATUS_CHOICES, default='unknown')
    last_health_check = models.DateTimeField(null=True, blank=True)
    timeout = models.IntegerField(default=30, help_text='Request timeout in seconds')
    weight = models.IntegerField(default=1, help_text='Load balancing weight')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Service Registry'
        verbose_name_plural = 'Service Registries'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.status})"

class RouteConfiguration(models.Model):
    """
    Model to configure routing rules for different paths
    """
    ROUTE_TYPE_CHOICES = [
        ('prefix', 'Prefix Match'),
        ('exact', 'Exact Match'),
        ('regex', 'Regex Match'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path_pattern = models.CharField(max_length=500)
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPE_CHOICES, default='prefix')
    service = models.ForeignKey(ServiceRegistry, on_delete=models.CASCADE, related_name='routes')
    priority = models.IntegerField(default=0, help_text='Higher priority routes are matched first')
    is_active = models.BooleanField(default=True)
    requires_auth = models.BooleanField(default=True)
    rate_limit = models.CharField(max_length=50, blank=True, help_text='e.g., 100/hour')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Route Configuration'
        verbose_name_plural = 'Route Configurations'
        ordering = ['-priority', 'path_pattern']
    
    def __str__(self):
        return f"{self.path_pattern} -> {self.service.name}"

class RequestLog(models.Model):
    """
    Model to log requests passing through the gateway
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_id = models.CharField(max_length=100, db_index=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    service_name = models.CharField(max_length=100, blank=True)
    client_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text='Response time in seconds')
    request_size = models.IntegerField(null=True, blank=True, help_text='Request size in bytes')
    response_size = models.IntegerField(null=True, blank=True, help_text='Response size in bytes')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['service_name']),
            models.Index(fields=['status_code']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} ({self.status_code})"

class ServiceMetrics(models.Model):
    """
    Model to store service performance metrics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(ServiceRegistry, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField(default=timezone.now)
    request_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0.0)
    min_response_time = models.FloatField(default=0.0)
    max_response_time = models.FloatField(default=0.0)
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Service Metrics'
        verbose_name_plural = 'Service Metrics'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['service', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.service.name} metrics at {self.timestamp}"

class CircuitBreakerState(models.Model):
    """
    Model to track circuit breaker state for services
    """
    STATE_CHOICES = [
        ('closed', 'Closed'),
        ('open', 'Open'),
        ('half_open', 'Half Open'),
    ]
    
    service = models.OneToOneField(ServiceRegistry, on_delete=models.CASCADE, related_name='circuit_breaker')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='closed')
    failure_count = models.IntegerField(default=0)
    last_failure_time = models.DateTimeField(null=True, blank=True)
    next_attempt_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Circuit Breaker State'
        verbose_name_plural = 'Circuit Breaker States'
    
    def __str__(self):
        return f"{self.service.name} circuit breaker: {self.state}"

class RateLimitRule(models.Model):
    """
    Model to define rate limiting rules
    """
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('service', 'Per Service'),
        ('user', 'Per User'),
        ('ip', 'Per IP'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    path_pattern = models.CharField(max_length=500, blank=True)
    service = models.ForeignKey(ServiceRegistry, on_delete=models.CASCADE, null=True, blank=True)
    requests_per_minute = models.IntegerField(default=60)
    requests_per_hour = models.IntegerField(default=1000)
    requests_per_day = models.IntegerField(default=10000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rate Limit Rule'
        verbose_name_plural = 'Rate Limit Rules'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.scope})"

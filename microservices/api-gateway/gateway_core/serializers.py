from rest_framework import serializers
from .models import (
    ServiceRegistry, RouteConfiguration, RequestLog,
    ServiceMetrics, CircuitBreakerState, RateLimitRule
)

class ServiceRegistrySerializer(serializers.ModelSerializer):
    """
    Serializer for ServiceRegistry model
    """
    class Meta:
        model = ServiceRegistry
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_health_check')
    
    def validate_base_url(self, value):
        """
        Validate that base_url is properly formatted
        """
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Base URL must start with http:// or https://")
        return value

class RouteConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for RouteConfiguration model
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_url = serializers.CharField(source='service.base_url', read_only=True)
    
    class Meta:
        model = RouteConfiguration
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_path_pattern(self, value):
        """
        Validate path pattern format
        """
        if not value.startswith('/'):
            raise serializers.ValidationError("Path pattern must start with '/'")
        return value

class RequestLogSerializer(serializers.ModelSerializer):
    """
    Serializer for RequestLog model
    """
    class Meta:
        model = RequestLog
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class ServiceMetricsSerializer(serializers.ModelSerializer):
    """
    Serializer for ServiceMetrics model
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = ServiceMetrics
        fields = '__all__'
        read_only_fields = ('id',)

class CircuitBreakerStateSerializer(serializers.ModelSerializer):
    """
    Serializer for CircuitBreakerState model
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_url = serializers.CharField(source='service.base_url', read_only=True)
    
    class Meta:
        model = CircuitBreakerState
        fields = '__all__'
        read_only_fields = ('updated_at',)

class RateLimitRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for RateLimitRule model
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = RateLimitRule
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate(self, data):
        """
        Validate rate limit values
        """
        if data.get('requests_per_minute', 0) <= 0:
            raise serializers.ValidationError("Requests per minute must be greater than 0")
        if data.get('requests_per_hour', 0) <= 0:
            raise serializers.ValidationError("Requests per hour must be greater than 0")
        if data.get('requests_per_day', 0) <= 0:
            raise serializers.ValidationError("Requests per day must be greater than 0")
        return data

class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for health check responses
    """
    status = serializers.CharField()
    response_time = serializers.FloatField(required=False)
    last_check = serializers.DateTimeField(required=False)
    error = serializers.CharField(required=False)
    status_code = serializers.IntegerField(required=False)

class DashboardSerializer(serializers.Serializer):
    """
    Serializer for dashboard data
    """
    services = serializers.DictField()
    requests = serializers.DictField()
    services_detail = ServiceRegistrySerializer(many=True)

class AnalyticsSerializer(serializers.Serializer):
    """
    Serializer for analytics data
    """
    by_service = serializers.ListField()
    by_status = serializers.ListField()
    error_rate = serializers.FloatField()
    total_requests = serializers.IntegerField()
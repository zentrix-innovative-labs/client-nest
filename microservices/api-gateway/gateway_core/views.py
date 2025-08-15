from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
import requests
import logging

from .models import (
    ServiceRegistry, RouteConfiguration, RequestLog, 
    ServiceMetrics, CircuitBreakerState, RateLimitRule
)
from .serializers import (
    ServiceRegistrySerializer, RouteConfigurationSerializer,
    RequestLogSerializer, ServiceMetricsSerializer,
    CircuitBreakerStateSerializer, RateLimitRuleSerializer
)

logger = logging.getLogger(__name__)

class ServiceRegistryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service registry
    """
    queryset = ServiceRegistry.objects.all()
    serializer_class = ServiceRegistrySerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def health_check(self, request, pk=None):
        """
        Perform health check on a specific service
        """
        service = self.get_object()
        try:
            health_url = f"{service.base_url.rstrip('/')}{service.health_check_endpoint}"
            response = requests.get(health_url, timeout=service.timeout)
            
            if response.status_code == 200:
                service.status = 'healthy'
                service.last_health_check = timezone.now()
                service.save()
                
                # Reset circuit breaker if healthy
                circuit_breaker, created = CircuitBreakerState.objects.get_or_create(
                    service=service,
                    defaults={'state': 'closed', 'failure_count': 0}
                )
                if circuit_breaker.state != 'closed':
                    circuit_breaker.state = 'closed'
                    circuit_breaker.failure_count = 0
                    circuit_breaker.save()
                
                return Response({
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'last_check': service.last_health_check
                })
            else:
                service.status = 'unhealthy'
                service.last_health_check = timezone.now()
                service.save()
                return Response({
                    'status': 'unhealthy',
                    'status_code': response.status_code,
                    'last_check': service.last_health_check
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except requests.RequestException as e:
            service.status = 'unhealthy'
            service.last_health_check = timezone.now()
            service.save()
            
            # Update circuit breaker
            circuit_breaker, created = CircuitBreakerState.objects.get_or_create(
                service=service,
                defaults={'state': 'closed', 'failure_count': 0}
            )
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = timezone.now()
            
            if circuit_breaker.failure_count >= 5:  # Threshold
                circuit_breaker.state = 'open'
                circuit_breaker.next_attempt_time = timezone.now() + timedelta(minutes=5)
            
            circuit_breaker.save()
            
            logger.error(f"Health check failed for {service.name}: {str(e)}")
            return Response({
                'status': 'unhealthy',
                'error': str(e),
                'last_check': service.last_health_check
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @action(detail=False, methods=['post'])
    def health_check_all(self, request):
        """
        Perform health check on all active services
        """
        services = ServiceRegistry.objects.filter(is_active=True)
        results = []
        
        for service in services:
            try:
                health_url = f"{service.base_url.rstrip('/')}{service.health_check_endpoint}"
                response = requests.get(health_url, timeout=service.timeout)
                
                if response.status_code == 200:
                    service.status = 'healthy'
                    results.append({
                        'service': service.name,
                        'status': 'healthy',
                        'response_time': response.elapsed.total_seconds()
                    })
                else:
                    service.status = 'unhealthy'
                    results.append({
                        'service': service.name,
                        'status': 'unhealthy',
                        'status_code': response.status_code
                    })
                    
                service.last_health_check = timezone.now()
                service.save()
                
            except requests.RequestException as e:
                service.status = 'unhealthy'
                service.last_health_check = timezone.now()
                service.save()
                
                results.append({
                    'service': service.name,
                    'status': 'unhealthy',
                    'error': str(e)
                })
        
        return Response({'results': results})
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get dashboard data for all services
        """
        services = ServiceRegistry.objects.all()
        total_services = services.count()
        healthy_services = services.filter(status='healthy').count()
        unhealthy_services = services.filter(status='unhealthy').count()
        
        # Get recent request stats
        last_hour = timezone.now() - timedelta(hours=1)
        recent_requests = RequestLog.objects.filter(created_at__gte=last_hour)
        
        request_stats = {
            'total_requests': recent_requests.count(),
            'error_requests': recent_requests.filter(status_code__gte=400).count(),
            'avg_response_time': recent_requests.aggregate(Avg('response_time'))['response_time__avg'] or 0
        }
        
        return Response({
            'services': {
                'total': total_services,
                'healthy': healthy_services,
                'unhealthy': unhealthy_services
            },
            'requests': request_stats,
            'services_detail': ServiceRegistrySerializer(services, many=True).data
        })

class RouteConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing route configurations
    """
    queryset = RouteConfiguration.objects.all()
    serializer_class = RouteConfigurationSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.query_params.get('service', None)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset

class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing request logs
    """
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by service
        service = self.request.query_params.get('service', None)
        if service:
            queryset = queryset.filter(service_name=service)
        
        # Filter by status code
        status_code = self.request.query_params.get('status_code', None)
        if status_code:
            queryset = queryset.filter(status_code=status_code)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get analytics data for requests
        """
        queryset = self.get_queryset()
        
        # Request count by service
        by_service = queryset.values('service_name').annotate(
            count=Count('id'),
            avg_response_time=Avg('response_time')
        ).order_by('-count')
        
        # Status code distribution
        by_status = queryset.values('status_code').annotate(
            count=Count('id')
        ).order_by('status_code')
        
        # Error rate
        total_requests = queryset.count()
        error_requests = queryset.filter(status_code__gte=400).count()
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        return Response({
            'by_service': list(by_service),
            'by_status': list(by_status),
            'error_rate': error_rate,
            'total_requests': total_requests
        })

class ServiceMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing service metrics
    """
    queryset = ServiceMetrics.objects.all()
    serializer_class = ServiceMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.query_params.get('service', None)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset

class CircuitBreakerStateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing circuit breaker states
    """
    queryset = CircuitBreakerState.objects.all()
    serializer_class = CircuitBreakerStateSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """
        Reset circuit breaker to closed state
        """
        circuit_breaker = self.get_object()
        circuit_breaker.state = 'closed'
        circuit_breaker.failure_count = 0
        circuit_breaker.last_failure_time = None
        circuit_breaker.next_attempt_time = None
        circuit_breaker.save()
        
        return Response({
            'message': f'Circuit breaker for {circuit_breaker.service.name} has been reset',
            'state': circuit_breaker.state
        })

class RateLimitRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rate limit rules
    """
    queryset = RateLimitRule.objects.all()
    serializer_class = RateLimitRuleSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.query_params.get('service', None)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset

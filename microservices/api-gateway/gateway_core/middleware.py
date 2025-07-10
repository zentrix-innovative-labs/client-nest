import logging
import time
import json
import requests
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger(__name__)

class ServiceRoutingMiddleware(MiddlewareMixin):
    """
    Middleware to route requests to appropriate microservices
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.service_routes = {
            '/api/v1/auth/': 'USER_SERVICE',
            '/api/v1/users/': 'USER_SERVICE',
            '/api/v1/content/': 'CONTENT_SERVICE',
            '/api/v1/posts/': 'CONTENT_SERVICE',
            '/api/v1/comments/': 'CONTENT_SERVICE',
            '/api/v1/social/': 'SOCIAL_SERVICE',
            '/api/v1/ai/': 'AI_SERVICE',
            '/api/v1/notifications/': 'NOTIFICATION_SERVICE',
        }
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming request and route to appropriate service
        """
        path = request.path
        
        # Skip routing for admin, health checks, and documentation
        if any(path.startswith(skip) for skip in ['/admin/', '/health/', '/swagger/', '/redoc/']):
            return None
        
        # Find matching service for the request path
        service_name = self._get_service_for_path(path)
        if not service_name:
            return None
        
        # Get service configuration
        service_config = settings.MICROSERVICES.get(service_name)
        if not service_config:
            logger.error(f"Service configuration not found for {service_name}")
            return JsonResponse(
                {'error': 'Service configuration error'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Check service health
        if not self._is_service_healthy(service_name, service_config):
            return JsonResponse(
                {'error': f'{service_name} is currently unavailable'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Forward request to microservice
        try:
            response = self._forward_request(request, service_config)
            return response
        except Exception as e:
            logger.error(f"Error forwarding request to {service_name}: {str(e)}")
            return JsonResponse(
                {'error': 'Internal service error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_service_for_path(self, path):
        """
        Determine which service should handle the request based on path
        """
        for route_prefix, service_name in self.service_routes.items():
            if path.startswith(route_prefix):
                return service_name
        return None
    
    def _is_service_healthy(self, service_name, service_config):
        """
        Check if the service is healthy using cached health status
        """
        cache_key = f"health_{service_name}"
        health_status = cache.get(cache_key)
        
        if health_status is None:
            # Perform health check
            try:
                health_url = f"{service_config['BASE_URL']}{service_config['HEALTH_CHECK']}"
                response = requests.get(health_url, timeout=5)
                health_status = response.status_code == 200
                # Cache health status for 30 seconds
                cache.set(cache_key, health_status, 30)
            except Exception as e:
                logger.warning(f"Health check failed for {service_name}: {str(e)}")
                health_status = False
                cache.set(cache_key, health_status, 10)  # Cache failure for shorter time
        
        return health_status
    
    def _forward_request(self, request, service_config):
        """
        Forward the request to the appropriate microservice
        """
        # Construct target URL
        target_url = f"{service_config['BASE_URL']}{request.path}"
        if request.GET:
            query_string = request.GET.urlencode()
            target_url += f"?{query_string}"
        
        # Prepare headers
        headers = {
            'Content-Type': request.content_type,
            'User-Agent': 'ClientNest-Gateway/1.0',
        }
        
        # Forward authorization header if present
        if 'HTTP_AUTHORIZATION' in request.META:
            headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
        
        # Forward other relevant headers
        for header_name in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_USER_AGENT']:
            if header_name in request.META:
                clean_name = header_name.replace('HTTP_', '').replace('_', '-')
                headers[clean_name] = request.META[header_name]
        
        # Prepare request data
        data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    data = request.body
            else:
                data = request.body
        
        # Make request to microservice
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            json=data if isinstance(data, dict) else None,
            data=data if not isinstance(data, dict) else None,
            timeout=service_config.get('TIMEOUT', 30),
            allow_redirects=False
        )
        
        # Create Django response from microservice response
        django_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )
        
        # Forward relevant response headers
        for header_name, header_value in response.headers.items():
            if header_name.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                django_response[header_name] = header_value
        
        return django_response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests passing through the gateway
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request details
        logger.info(f"Gateway Request: {request.method} {request.path} from {self._get_client_ip(request)}")
    
    def process_response(self, request, response):
        # Calculate request duration
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # Log response details
        logger.info(
            f"Gateway Response: {request.method} {request.path} -> "
            f"{response.status_code} ({duration:.3f}s)"
        )
        
        return response
    
    def _get_client_ip(self, request):
        """
        Get the client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CircuitBreakerMiddleware(MiddlewareMixin):
    """
    Circuit breaker pattern implementation for service resilience
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.circuit_breaker_settings = settings.GATEWAY_SETTINGS.get('CIRCUIT_BREAKER', {})
        super().__init__(get_response)
    
    def process_request(self, request):
        if not self.circuit_breaker_settings.get('ENABLED', False):
            return None
        
        # Check if circuit breaker is open for any service
        service_name = self._get_service_for_path(request.path)
        if service_name and self._is_circuit_open(service_name):
            return JsonResponse(
                {'error': f'{service_name} is temporarily unavailable'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return None
    
    def _get_service_for_path(self, path):
        """
        Determine which service should handle the request based on path
        """
        service_routes = {
            '/api/v1/auth/': 'USER_SERVICE',
            '/api/v1/users/': 'USER_SERVICE',
            '/api/v1/content/': 'CONTENT_SERVICE',
            '/api/v1/posts/': 'CONTENT_SERVICE',
            '/api/v1/comments/': 'CONTENT_SERVICE',
            '/api/v1/social/': 'SOCIAL_SERVICE',
            '/api/v1/ai/': 'AI_SERVICE',
            '/api/v1/notifications/': 'NOTIFICATION_SERVICE',
        }
        
        for route_prefix, service_name in service_routes.items():
            if path.startswith(route_prefix):
                return service_name
        return None
    
    def _is_circuit_open(self, service_name):
        """
        Check if circuit breaker is open for the service
        """
        cache_key = f"circuit_breaker_{service_name}"
        failure_count = cache.get(f"{cache_key}_failures", 0)
        
        failure_threshold = self.circuit_breaker_settings.get('FAILURE_THRESHOLD', 5)
        return failure_count >= failure_threshold
# Service Communication Guide

## 🎯 **Ensuring Proper Inter-Service Communication**

This guide provides comprehensive strategies to ensure your microservices communicate properly and reliably.

## 📊 **Current Communication Architecture**

### **Service Ports & URLs**
```
API Gateway:     http://localhost:8000
User Service:    http://localhost:8001
Content Service: http://localhost:8002
Social Service:  http://localhost:8003
Analytics Service: http://localhost:8004
AI Service:      http://localhost:8005
Notification Service: http://localhost:8006
Queue Service:   http://localhost:8007
Security Service: http://localhost:8008
File Service:    http://localhost:8009
Webhook Service: http://localhost:8010
```

## 🔍 **1. Health Check Implementation**

### **Basic Health Check**
```python
# In each service's views.py
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Comprehensive health check endpoint"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Redis connection (if used)
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        
        return Response({
            'status': 'healthy',
            'service': 'service-name',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'cache': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
```

### **Advanced Health Check with Dependencies**
```python
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def detailed_health_check(request):
    """Detailed health check with dependency verification"""
    health_status = {
        'status': 'healthy',
        'service': 'content-service',
        'timestamp': timezone.now().isoformat(),
        'dependencies': {},
        'checks': []
    }
    
    # Database check
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['dependencies']['database'] = 'connected'
        health_status['checks'].append('database_ok')
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['dependencies']['database'] = f'error: {str(e)}'
        health_status['checks'].append('database_failed')
    
    # Redis check
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_status['dependencies']['redis'] = 'connected'
        health_status['checks'].append('redis_ok')
    except Exception as e:
        health_status['dependencies']['redis'] = f'error: {str(e)}'
        health_status['checks'].append('redis_failed')
    
    # External service checks
    try:
        # Check user service
        user_service_response = requests.get(
            'http://localhost:8001/api/health/',
            timeout=5
        )
        if user_service_response.status_code == 200:
            health_status['dependencies']['user_service'] = 'connected'
            health_status['checks'].append('user_service_ok')
        else:
            health_status['dependencies']['user_service'] = 'unavailable'
            health_status['checks'].append('user_service_failed')
    except Exception as e:
        health_status['dependencies']['user_service'] = f'error: {str(e)}'
        health_status['checks'].append('user_service_failed')
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return Response(health_status, status=status_code)
```

## 🔐 **2. Service-to-Service Authentication**

### **JWT Service Tokens**
```python
# utils/service_auth.py
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import requests

class ServiceAuthenticator:
    def __init__(self, service_name, secret_key=None):
        self.service_name = service_name
        self.secret_key = secret_key or settings.SECRET_KEY
    
    def get_service_token(self):
        """Generate JWT token for service-to-service communication"""
        payload = {
            'service': self.service_name,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'scopes': self.get_service_scopes()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def make_authenticated_request(self, target_service, endpoint, data=None, method='GET'):
        """Make authenticated request to another service"""
        headers = {
            'Authorization': f'Bearer {self.get_service_token()}',
            'X-Service-Name': self.service_name,
            'X-Correlation-ID': self.get_correlation_id(),
            'Content-Type': 'application/json'
        }
        
        url = f"{target_service}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Service communication error: {str(e)}")
    
    def get_service_scopes(self):
        """Define service-specific permissions"""
        service_scopes = {
            'user-service': ['user:read', 'user:write', 'auth:validate'],
            'content-service': ['content:read', 'content:write', 'media:process'],
            'analytics-service': ['analytics:read', 'metrics:write', 'reports:generate'],
            'ai-service': ['ai:generate', 'ai:analyze', 'ai:optimize'],
            'social-service': ['social:read', 'social:write', 'platform:connect']
        }
        return service_scopes.get(self.service_name, [])
    
    def get_correlation_id(self):
        """Generate correlation ID for request tracing"""
        import uuid
        return str(uuid.uuid4())
```

### **Service Authentication Middleware**
```python
# middleware/service_auth.py
import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

class ServiceAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for health checks and public endpoints
        if request.path in ['/api/health/', '/api/docs/', '/admin/']:
            return self.get_response(request)
        
        # Check for service token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request.service_name = payload.get('service')
                request.service_scopes = payload.get('scopes', [])
                return self.get_response(request)
            except jwt.InvalidTokenError:
                return Response(
                    {'error': 'Invalid service token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # Continue with regular authentication
        return self.get_response(request)
```

## 📡 **3. API Gateway Communication**

### **Service Discovery & Routing**
```python
# api_gateway/routing.py
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

class ServiceRouter:
    def __init__(self):
        self.services = {
            'user-service': {
                'url': 'http://localhost:8001',
                'health_endpoint': '/api/health/',
                'timeout': 30
            },
            'content-service': {
                'url': 'http://localhost:8002',
                'health_endpoint': '/api/health/',
                'timeout': 30
            },
            'social-service': {
                'url': 'http://localhost:8003',
                'health_endpoint': '/api/health/',
                'timeout': 30
            }
        }
    
    def route_request(self, request, service_name):
        """Route request to appropriate service"""
        if service_name not in self.services:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service_config = self.services[service_name]
        
        # Check service health
        if not self.is_service_healthy(service_config):
            return Response(
                {'error': f'{service_name} is unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Forward request
        return self.forward_request(request, service_config)
    
    def is_service_healthy(self, service_config):
        """Check if service is healthy"""
        try:
            response = requests.get(
                f"{service_config['url']}{service_config['health_endpoint']}",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def forward_request(self, request, service_config):
        """Forward request to target service"""
        target_url = f"{service_config['url']}{request.path}"
        
        headers = {
            'Content-Type': request.content_type or 'application/json',
            'Authorization': request.META.get('HTTP_AUTHORIZATION', ''),
            'X-Forwarded-For': self.get_client_ip(request),
            'X-Gateway-Service': 'api-gateway'
        }
        
        try:
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=request.data if request.data else None,
                params=request.GET,
                timeout=service_config['timeout']
            )
            
            return Response(
                response.json() if response.content else {},
                status=response.status_code
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': f'Service communication error: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY
            )
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

## 🔄 **4. Circuit Breaker Pattern**

### **Circuit Breaker Implementation**
```python
# utils/circuit_breaker.py
import time
from enum import Enum
from django.core.cache import cache

class CircuitState(Enum):
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'

class CircuitBreaker:
    def __init__(self, service_name, failure_threshold=5, recovery_timeout=60):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.cache_key = f"circuit_breaker:{service_name}"
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.is_open():
            raise Exception(f"Circuit breaker for {self.service_name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def is_open(self):
        """Check if circuit breaker is open"""
        state = cache.get(f"{self.cache_key}:state")
        if state == CircuitState.OPEN.value:
            # Check if recovery timeout has passed
            last_failure = cache.get(f"{self.cache_key}:last_failure")
            if last_failure and time.time() - last_failure > self.recovery_timeout:
                self.set_half_open()
                return False
            return True
        return False
    
    def on_success(self):
        """Handle successful call"""
        cache.set(f"{self.cache_key}:state", CircuitState.CLOSED.value)
        cache.delete(f"{self.cache_key}:failure_count")
    
    def on_failure(self):
        """Handle failed call"""
        failure_count = cache.get(f"{self.cache_key}:failure_count", 0) + 1
        cache.set(f"{self.cache_key}:failure_count", failure_count)
        cache.set(f"{self.cache_key}:last_failure", time.time())
        
        if failure_count >= self.failure_threshold:
            cache.set(f"{self.cache_key}:state", CircuitState.OPEN.value)
    
    def set_half_open(self):
        """Set circuit breaker to half-open state"""
        cache.set(f"{self.cache_key}:state", CircuitState.HALF_OPEN.value)
```

## 📊 **5. Monitoring & Observability**

### **Request Logging Middleware**
```python
# middleware/request_logging.py
import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('service_communication')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log incoming request
        log_data = {
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'client_ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'service': 'content-service'
        }
        
        if request.content_type == 'application/json':
            try:
                log_data['request_body'] = json.loads(request.body.decode())
            except:
                pass
        
        logger.info(f"INCOMING_REQUEST: {json.dumps(log_data)}")
    
    def process_response(self, request, response):
        # Calculate response time
        response_time = time.time() - getattr(request, 'start_time', time.time())
        
        # Log response
        log_data = {
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'response_time': response_time,
            'service': 'content-service'
        }
        
        logger.info(f"OUTGOING_RESPONSE: {json.dumps(log_data)}")
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

### **Service Metrics Collection**
```python
# utils/metrics.py
from django.core.cache import cache
import time

class ServiceMetrics:
    def __init__(self, service_name):
        self.service_name = service_name
    
    def record_request(self, endpoint, method, status_code, response_time):
        """Record request metrics"""
        key = f"metrics:{self.service_name}:{endpoint}:{method}"
        
        # Increment request count
        cache.incr(f"{key}:count", 1)
        
        # Update average response time
        current_avg = cache.get(f"{key}:avg_time", 0)
        current_count = cache.get(f"{key}:count", 1)
        new_avg = ((current_avg * (current_count - 1)) + response_time) / current_count
        cache.set(f"{key}:avg_time", new_avg)
        
        # Track status codes
        cache.incr(f"{key}:status:{status_code}", 1)
        
        # Update last request time
        cache.set(f"{key}:last_request", time.time())
    
    def get_metrics(self, endpoint=None):
        """Get service metrics"""
        metrics = {
            'service': self.service_name,
            'timestamp': time.time(),
            'endpoints': {}
        }
        
        if endpoint:
            key = f"metrics:{self.service_name}:{endpoint}"
            metrics['endpoints'][endpoint] = {
                'count': cache.get(f"{key}:count", 0),
                'avg_time': cache.get(f"{key}:avg_time", 0),
                'last_request': cache.get(f"{key}:last_request", 0)
            }
        else:
            # Get all endpoints
            pattern = f"metrics:{self.service_name}:*:count"
            # Implementation depends on your cache backend
        
        return metrics
```

## 🧪 **6. Testing Service Communication**

### **Integration Test Example**
```python
# tests/test_service_communication.py
import pytest
import requests
from django.test import TestCase
from unittest.mock import patch

class ServiceCommunicationTest(TestCase):
    def setUp(self):
        self.user_service_url = 'http://localhost:8001'
        self.content_service_url = 'http://localhost:8002'
    
    def test_user_service_health(self):
        """Test user service health check"""
        response = requests.get(f"{self.user_service_url}/api/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'user-service')
    
    def test_service_to_service_communication(self):
        """Test content service calling user service"""
        # Mock the user service response
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'id': 1,
                'email': 'test@example.com',
                'username': 'testuser'
            }
            
            # Make request from content service to user service
            response = requests.get(f"{self.user_service_url}/api/users/1/")
            self.assertEqual(response.status_code, 200)
    
    def test_circuit_breaker_functionality(self):
        """Test circuit breaker pattern"""
        from utils.circuit_breaker import CircuitBreaker
        
        breaker = CircuitBreaker('test-service')
        
        # Test successful call
        def successful_func():
            return "success"
        
        result = breaker.call(successful_func)
        self.assertEqual(result, "success")
        
        # Test failed call
        def failed_func():
            raise Exception("Service unavailable")
        
        with self.assertRaises(Exception):
            breaker.call(failed_func)
```

## 🚀 **7. Implementation Checklist**

### **For Each Service**
- [ ] **Health Check Endpoint**: `/api/health/`
- [ ] **Service Authentication**: JWT tokens for inter-service calls
- [ ] **Circuit Breaker**: Implement for external service calls
- [ ] **Request Logging**: Log all incoming/outgoing requests
- [ ] **Metrics Collection**: Track response times and error rates
- [ ] **Error Handling**: Proper exception handling and retry logic
- [ ] **Timeout Configuration**: Set appropriate timeouts for service calls
- [ ] **CORS Configuration**: Allow cross-origin requests from other services

### **For API Gateway**
- [ ] **Service Discovery**: Dynamic service registration
- [ ] **Load Balancing**: Distribute requests across service instances
- [ ] **Rate Limiting**: Prevent service overload
- [ ] **Request Routing**: Route requests to appropriate services
- [ ] **Authentication**: Validate JWT tokens
- [ ] **Monitoring**: Track gateway performance

### **For Development Environment**
- [ ] **Docker Compose**: All services running locally
- [ ] **Environment Variables**: Service URLs and configurations
- [ ] **Logging**: Centralized logging for all services
- [ ] **Testing**: Integration tests for service communication
- [ ] **Documentation**: API documentation for each service

## 📈 **8. Monitoring Dashboard**

### **Key Metrics to Monitor**
- **Response Times**: Average response time per service
- **Error Rates**: Percentage of failed requests
- **Throughput**: Requests per second
- **Circuit Breaker Status**: Open/closed state of circuit breakers
- **Service Health**: Health check status of all services
- **Dependencies**: Status of external service dependencies

### **Alerting Rules**
- Service response time > 2 seconds
- Error rate > 5%
- Circuit breaker open for > 5 minutes
- Service health check failing
- High memory/CPU usage

## 🎯 **Success Criteria**

Your services are communicating properly when:

1. **All health checks pass** - Every service responds to `/api/health/`
2. **Zero communication errors** - No 502/503/504 errors in logs
3. **Fast response times** - All inter-service calls < 200ms
4. **Proper authentication** - All service-to-service calls use JWT tokens
5. **Circuit breakers closed** - No circuit breakers in OPEN state
6. **Complete request tracing** - All requests have correlation IDs
7. **Comprehensive logging** - All service communication is logged
8. **Error handling** - Failed requests are properly handled and retried

This comprehensive approach ensures reliable, observable, and maintainable inter-service communication in your microservices architecture. 
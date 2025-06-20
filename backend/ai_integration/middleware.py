from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.core.cache import cache
from typing import Callable, Any
import time
import json
import logging
from .config import MONITORING_CONFIG, USAGE_LIMITS
from .exceptions import AIQuotaExceededError, AIRateLimitError

logger = logging.getLogger('ai.middleware')

class AIRequestMiddleware:
    """Middleware for processing AI-related requests"""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Only process AI-related endpoints
        if not request.path.startswith('/api/ai/'):
            return self.get_response(request)

        # Start request timing
        start_time = time.time()

        try:
            # Check authentication
            if not request.user.is_authenticated:
                return HttpResponse(
                    json.dumps({'error': 'Authentication required'}),
                    status=401,
                    content_type='application/json'
                )

            # Check user tier and limits
            if not self._check_user_limits(request):
                raise AIQuotaExceededError('Usage quota exceeded')

            # Process the request
            response = self.get_response(request)

            # Record metrics only for successful requests
            if response.status_code < 400:
                self._record_metrics(request, response, start_time)

            return response

        except AIQuotaExceededError as e:
            return HttpResponse(
                json.dumps({'error': str(e)}),
                status=402,
                content_type='application/json'
            )
        except AIRateLimitError as e:
            return HttpResponse(
                json.dumps({'error': str(e)}),
                status=429,
                content_type='application/json'
            )
        except Exception as e:
            logger.error(f'AI request processing error: {str(e)}')
            self._record_error_metric(request, e)
            return HttpResponse(
                json.dumps({'error': 'Internal server error'}),
                status=500,
                content_type='application/json'
            )
        finally:
            # Always record request duration
            duration = time.time() - start_time
            self._record_duration_metric(request, duration)

    def _check_user_limits(self, request: HttpRequest) -> bool:
        """Check if user has exceeded their usage limits"""
        user = request.user
        tier = getattr(user, 'subscription_tier', 'free')
        limits = USAGE_LIMITS.get(tier, USAGE_LIMITS['free'])

        # Skip checks for enterprise tier
        if tier == 'enterprise':
            return True

        # Check daily limit
        daily_key = f'ai:usage:daily:{user.id}'
        daily_usage = cache.get(daily_key, 0)
        if limits['daily_requests'] != -1 and daily_usage >= limits['daily_requests']:
            return False

        # Check monthly limit
        monthly_key = f'ai:usage:monthly:{user.id}'
        monthly_usage = cache.get(monthly_key, 0)
        if limits['monthly_requests'] != -1 and monthly_usage >= limits['monthly_requests']:
            return False

        # Check concurrent requests
        concurrent_key = f'ai:concurrent:{user.id}'
        concurrent_requests = cache.get(concurrent_key, 0)
        if concurrent_requests >= limits['concurrent_requests']:
            return False

        return True

    def _record_metrics(self, request: HttpRequest, response: HttpResponse,
                       start_time: float) -> None:
        """Record request metrics"""
        if not MONITORING_CONFIG['metrics']['request_duration']:
            return

        duration = time.time() - start_time
        endpoint = request.path.split('/')[-1]

        # Record endpoint usage
        if MONITORING_CONFIG['metrics']['usage_by_endpoint']:
            endpoint_key = f'ai:metrics:endpoint:{endpoint}'
            cache.incr(endpoint_key, 1)

        # Record user usage
        if MONITORING_CONFIG['metrics']['usage_by_user']:
            user_key = f'ai:metrics:user:{request.user.id}'
            cache.incr(user_key, 1)

        # Check for latency alerts
        if duration > MONITORING_CONFIG['alerts']['latency_threshold']:
            logger.warning(
                f'High latency detected for {endpoint}: {duration:.2f}s'
            )

    def _record_error_metric(self, request: HttpRequest, error: Exception) -> None:
        """Record error metrics"""
        if not MONITORING_CONFIG['metrics']['error_rate']:
            return

        endpoint = request.path.split('/')[-1]
        error_key = f'ai:metrics:errors:{endpoint}'
        cache.incr(error_key, 1)

        # Check error rate threshold
        total_key = f'ai:metrics:endpoint:{endpoint}'
        total_requests = cache.get(total_key, 0)
        if total_requests > 0:
            error_rate = cache.get(error_key, 0) / total_requests
            if error_rate > MONITORING_CONFIG['alerts']['error_threshold']:
                logger.error(
                    f'High error rate detected for {endpoint}: {error_rate:.2%}'
                )

    def _record_duration_metric(self, request: HttpRequest, duration: float) -> None:
        """Record request duration metrics"""
        if not MONITORING_CONFIG['metrics']['request_duration']:
            return

        endpoint = request.path.split('/')[-1]
        duration_key = f'ai:metrics:duration:{endpoint}'
        
        # Store as running average
        current_avg = cache.get(duration_key, 0)
        request_count = cache.get(f'ai:metrics:endpoint:{endpoint}', 0)
        
        if request_count > 0:
            new_avg = ((current_avg * (request_count - 1)) + duration) / request_count
            cache.set(duration_key, new_avg)

    def _is_ai_request(self, request):
        """Return True if the request is for an AI endpoint."""
        return request.path.startswith('/api/ai/')

# Add stubs for test patching
statsd = None
def check_usage_limits(*args, **kwargs):
    return True
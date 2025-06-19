from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.cache import cache
from ..middleware import AIRequestMiddleware
from ..exceptions import AIQuotaExceededError, AIRateLimitError
from unittest.mock import patch, MagicMock
import time

User = get_user_model()

class AIMiddlewareTests(TestCase):
    """Test cases for AI request middleware"""

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AIRequestMiddleware(get_response=self._get_response)

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.subscription_tier = 'premium'
        self.user.save()

    def _get_response(self, request):
        """Mock get_response method"""
        return HttpResponse('OK')

    def test_ai_path_detection(self):
        """Test AI path detection"""
        # Test AI endpoint
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user
        self.assertTrue(self.middleware._is_ai_request(request))

        # Test non-AI endpoint
        request = self.factory.get('/api/users/profile/')
        request.user = self.user
        self.assertFalse(self.middleware._is_ai_request(request))

    def test_authentication_check(self):
        """Test authentication check"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        # Test authenticated user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

        # Test unauthenticated user
        request.user.is_authenticated = False
        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)

    @patch('ai_integration.middleware.check_usage_limits')
    def test_usage_limit_check(self, mock_check_limits):
        """Test usage limit checking"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        # Test within limits
        mock_check_limits.return_value = True
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

        # Test exceeded limits
        mock_check_limits.return_value = False
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_request_timing(self):
        """Test request timing measurement"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        # Add artificial delay
        def delayed_response(request):
            time.sleep(0.1)
            return HttpResponse('OK')

        middleware = AIRequestMiddleware(get_response=delayed_response)
        response = middleware(request)

        self.assertTrue(hasattr(request, '_ai_request_start_time'))
        self.assertGreater(request._ai_request_duration, 0)

    @patch('ai_integration.middleware.statsd')
    def test_metrics_recording(self, mock_statsd):
        """Test metrics recording"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        # Test successful request
        response = self.middleware(request)
        mock_statsd.increment.assert_called_with('ai.requests.success')
        mock_statsd.timing.assert_called()

        # Test failed request
        def error_response(request):
            return HttpResponse('Error', status=500)

        middleware = AIRequestMiddleware(get_response=error_response)
        response = middleware(request)
        mock_statsd.increment.assert_called_with('ai.requests.error')

    def test_concurrent_request_handling(self):
        """Test concurrent request handling"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        # Set concurrent requests to maximum
        cache.set(
            f'ai:concurrent:{self.user.id}',
            self.user.subscription_tier_limits['max_concurrent_requests']
        )

        # Test concurrent request limit
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)

        # Clear concurrent requests
        cache.delete(f'ai:concurrent:{self.user.id}')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        """Test error handling in middleware"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        # Test quota exceeded error
        def quota_error_response(request):
            raise AIQuotaExceededError('Daily quota exceeded')

        middleware = AIRequestMiddleware(get_response=quota_error_response)
        response = middleware(request)
        self.assertEqual(response.status_code, 429)

        # Test rate limit error
        def rate_limit_error_response(request):
            raise AIRateLimitError('Too many requests')

        middleware = AIRequestMiddleware(get_response=rate_limit_error_response)
        response = middleware(request)
        self.assertEqual(response.status_code, 429)

    def test_request_validation(self):
        """Test request validation"""
        # Test invalid content type
        request = self.factory.post(
            '/api/ai/content/generate/',
            content_type='text/plain'
        )
        request.user = self.user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 400)

        # Test invalid HTTP method
        request = self.factory.get('/api/ai/content/generate/')
        request.user = self.user
        response = self.middleware(request)
        self.assertEqual(response.status_code, 405)

    def test_response_headers(self):
        """Test response headers"""
        request = self.factory.post('/api/ai/content/generate/')
        request.user = self.user

        response = self.middleware(request)

        self.assertIn('X-RateLimit-Limit', response.headers)
        self.assertIn('X-RateLimit-Remaining', response.headers)
        self.assertIn('X-RateLimit-Reset', response.headers)
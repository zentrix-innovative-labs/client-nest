import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from asgiref.sync import async_to_sync

@pytest.mark.asyncio
class AIServiceTests(TestCase):
    """Test cases for AIService"""

    def setUp(self):
        from django.contrib.auth import get_user_model
        from ..models import AIModel
        from ..services import AIService
        User = get_user_model()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create test model
        self.model = AIModel.objects.create(
            name='deepseek-chat',
            description='Test Model',
            version='1.0'
        )
        # Initialize service
        self.service = AIService()

    def test_content_generation(self):
        from ..services import AIService
        from unittest.mock import patch, MagicMock
        with patch('ai_integration.services.DeepSeekClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {'content': 'Generated content'}
                }]
            }
            mock_client.return_value.post.return_value = mock_response

            result = self.service.sync_process_content_generation(
                user_id=self.user.id,
                content_type='post',
                prompt='Test prompt',
                platform='twitter'
            )

            self.assertIn('choices', result)
            self.assertEqual(
                result['choices'][0]['message']['content'],
                'Generated content'
            )

    def test_rate_limit_handling(self):
        from ..exceptions import AIRateLimitError
        # Set rate limiter to exceeded state
        self.service.rate_limiter.max_requests = 0

        with self.assertRaises(AIRateLimitError):
            self.service.sync_process_content_generation(
                user_id=self.user.id,
                content_type='post',
                prompt='Test prompt'
            )

    def test_circuit_breaker_handling(self):
        from ..exceptions import AIServiceUnavailableError
        # Trigger circuit breaker
        for _ in range(self.service.circuit_breaker.failure_threshold):
            self.service.circuit_breaker.record_failure()

        with self.assertRaises(AIServiceUnavailableError):
            self.service.sync_process_content_generation(
                user_id=self.user.id,
                content_type='post',
                prompt='Test prompt'
            )

    def test_sentiment_analysis(self):
        from unittest.mock import patch, MagicMock
        with patch('ai_integration.services.DeepSeekClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'sentiment': 'positive',
                'confidence': 0.95,
                'emotions': ['joy', 'excitement']
            }
            mock_client.return_value.post.return_value = mock_response

            result = self.service.sync_process_sentiment_analysis(
                user_id=self.user.id,
                text='Great product!',
                context='review'
            )

            self.assertEqual(result['sentiment'], 'positive')
            self.assertGreater(result['confidence'], 0.9)
            self.assertIn('joy', result['emotions'])

class UtilsTests(TestCase):
    """Test cases for utility functions"""

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_cache_key_generation(self):
        from ..utils import generate_cache_key
        data = {'type': 'test', 'content': 'test content'}
        key1 = generate_cache_key('test', data)
        key2 = generate_cache_key('test', data)
        self.assertEqual(key1, key2)
        self.assertTrue(key1.startswith('ai:test:'))

    def test_tier_limits(self):
        from ..utils import get_tier_limits
        free_limits = get_tier_limits('free')
        premium_limits = get_tier_limits('premium')
        self.assertLess(free_limits['daily_requests'],
                       premium_limits['daily_requests'])
        self.assertLess(free_limits['max_tokens'],
                       premium_limits['max_tokens'])

    def test_usage_limits(self):
        from django.core.cache import cache
        from ..utils import get_tier_limits, check_usage_limits
        # Ensure cache is clear for this user
        cache.delete(f'ai:usage:daily:{self.user.id}')
        cache.delete(f'ai:usage:monthly:{self.user.id}')
        # Test with no usage
        self.assertTrue(check_usage_limits(self.user.id, 'free'))
        # Test with exceeded usage
        cache.set(f'ai:usage:daily:{self.user.id}',
                 get_tier_limits('free')['daily_requests'] + 1)
        self.assertFalse(check_usage_limits(self.user.id, 'free'))
        # Test enterprise tier (unlimited)
        self.assertTrue(check_usage_limits(self.user.id, 'enterprise'))

    def test_token_cost_calculation(self):
        from ..utils import calculate_token_cost
        short_text = 'Hello world'
        long_text = 'x' * 1000
        short_cost = calculate_token_cost(short_text)
        long_cost = calculate_token_cost(long_text)
        self.assertLess(short_cost, long_cost)
        self.assertEqual(short_cost, len(short_text) // 4)
        self.assertEqual(long_cost, len(long_text) // 4)
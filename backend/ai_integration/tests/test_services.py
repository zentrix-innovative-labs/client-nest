import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from ..models import AIModel, AITask
from ..services import AIService
from ..exceptions import (
    AIRateLimitError,
    AIServiceUnavailableError,
    AIQuotaExceededError
)
from ..utils import (
    generate_cache_key,
    get_tier_limits,
    check_usage_limits,
    calculate_token_cost
)

User = get_user_model()

@pytest.mark.asyncio
class AIServiceTests(TestCase):
    """Test cases for AIService"""

    async def asyncSetUp(self):
        # Create test user
        self.user = await User.objects.acreate(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test model
        self.model = await AIModel.objects.acreate(
            name='deepseek-chat',
            description='Test Model',
            version='1.0'
        )

        # Initialize service
        self.service = AIService()

    async def test_content_generation(self):
        """Test content generation service"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {'content': 'Generated content'}
                }]
            }
            mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await self.service.process_content_generation(
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

    async def test_rate_limit_handling(self):
        """Test rate limit handling"""
        # Set rate limiter to exceeded state
        self.service.rate_limiter.max_requests = 0

        with self.assertRaises(AIRateLimitError):
            await self.service.process_content_generation(
                user_id=self.user.id,
                content_type='post',
                prompt='Test prompt'
            )

    async def test_circuit_breaker_handling(self):
        """Test circuit breaker handling"""
        # Trigger circuit breaker
        for _ in range(self.service.circuit_breaker.failure_threshold):
            self.service.circuit_breaker.record_failure()

        with self.assertRaises(AIServiceUnavailableError):
            await self.service.process_content_generation(
                user_id=self.user.id,
                content_type='post',
                prompt='Test prompt'
            )

    async def test_sentiment_analysis(self):
        """Test sentiment analysis service"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'sentiment': 'positive',
                'confidence': 0.95,
                'emotions': ['joy', 'excitement']
            }
            mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

            result = await self.service.process_sentiment_analysis(
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
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_cache_key_generation(self):
        """Test cache key generation"""
        data = {'type': 'test', 'content': 'test content'}
        key1 = generate_cache_key('test', data)
        key2 = generate_cache_key('test', data)

        self.assertEqual(key1, key2)
        self.assertTrue(key1.startswith('ai:test:'))

    def test_tier_limits(self):
        """Test tier-based limits"""
        free_limits = get_tier_limits('free')
        premium_limits = get_tier_limits('premium')

        self.assertLess(free_limits['daily_requests'],
                       premium_limits['daily_requests'])
        self.assertLess(free_limits['max_tokens'],
                       premium_limits['max_tokens'])

    def test_usage_limits(self):
        """Test usage limit checking"""
        # Test with no usage
        self.assertTrue(check_usage_limits(self.user.id, 'free'))

        # Test with exceeded usage
        cache.set(f'ai:usage:daily:{self.user.id}',
                 get_tier_limits('free')['daily_requests'] + 1)
        self.assertFalse(check_usage_limits(self.user.id, 'free'))

        # Test enterprise tier (unlimited)
        self.assertTrue(check_usage_limits(self.user.id, 'enterprise'))

    def test_token_cost_calculation(self):
        """Test token cost calculation"""
        short_text = 'Hello world'
        long_text = 'x' * 1000

        short_cost = calculate_token_cost(short_text)
        long_cost = calculate_token_cost(long_text)

        self.assertLess(short_cost, long_cost)
        self.assertEqual(short_cost, len(short_text) // 4)
        self.assertEqual(long_cost, len(long_text) // 4)
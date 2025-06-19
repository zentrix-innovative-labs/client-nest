from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from ..models import AIModel, AITask
from ..signals import (
    update_concurrent_requests,
    update_task_metrics,
    clear_model_cache,
    clear_task_cache
)
from ..config import (
    DEEPSEEK_API_CONFIG,
    RATE_LIMIT_CONFIG,
    CIRCUIT_BREAKER_CONFIG,
    TIER_LIMITS,
    CACHE_CONFIG,
    QUEUE_CONFIG,
    CONTENT_POLICY_CONFIG,
    MONITORING_CONFIG,
    COST_OPTIMIZATION_CONFIG
)
from unittest.mock import patch

User = get_user_model()

class ConfigTests(TestCase):
    """Test cases for AI integration configuration"""

    def test_deepseek_api_config(self):
        """Test DeepSeek API configuration"""
        self.assertIn('base_url', DEEPSEEK_API_CONFIG)
        self.assertIn('timeout', DEEPSEEK_API_CONFIG)
        self.assertIn('retry_count', DEEPSEEK_API_CONFIG)
        self.assertGreater(DEEPSEEK_API_CONFIG['timeout'], 0)
        self.assertGreater(DEEPSEEK_API_CONFIG['retry_count'], 0)

    def test_rate_limit_config(self):
        """Test rate limiting configuration"""
        self.assertIn('window_size', RATE_LIMIT_CONFIG)
        self.assertIn('max_requests', RATE_LIMIT_CONFIG)
        self.assertGreater(RATE_LIMIT_CONFIG['window_size'], 0)
        self.assertGreater(RATE_LIMIT_CONFIG['max_requests'], 0)

    def test_circuit_breaker_config(self):
        """Test circuit breaker configuration"""
        self.assertIn('failure_threshold', CIRCUIT_BREAKER_CONFIG)
        self.assertIn('recovery_timeout', CIRCUIT_BREAKER_CONFIG)
        self.assertGreater(CIRCUIT_BREAKER_CONFIG['failure_threshold'], 0)
        self.assertGreater(CIRCUIT_BREAKER_CONFIG['recovery_timeout'], 0)

    def test_tier_limits(self):
        """Test tier-based limits configuration"""
        for tier in ['free', 'premium', 'enterprise']:
            self.assertIn(tier, TIER_LIMITS)
            self.assertIn('daily_requests', TIER_LIMITS[tier])
            self.assertIn('max_tokens', TIER_LIMITS[tier])
            self.assertIn('max_concurrent_requests', TIER_LIMITS[tier])

    def test_cache_config(self):
        """Test cache configuration"""
        self.assertIn('default_ttl', CACHE_CONFIG)
        self.assertIn('max_size', CACHE_CONFIG)
        self.assertGreater(CACHE_CONFIG['default_ttl'], 0)
        self.assertGreater(CACHE_CONFIG['max_size'], 0)

    def test_queue_config(self):
        """Test queue configuration"""
        self.assertIn('max_retries', QUEUE_CONFIG)
        self.assertIn('retry_delay', QUEUE_CONFIG)
        self.assertIn('task_timeout', QUEUE_CONFIG)
        self.assertGreater(QUEUE_CONFIG['max_retries'], 0)
        self.assertGreater(QUEUE_CONFIG['retry_delay'], 0)
        self.assertGreater(QUEUE_CONFIG['task_timeout'], 0)

    def test_content_policy_config(self):
        """Test content policy configuration"""
        self.assertIn('max_prompt_length', CONTENT_POLICY_CONFIG)
        self.assertIn('max_text_length', CONTENT_POLICY_CONFIG)
        self.assertIn('allowed_languages', CONTENT_POLICY_CONFIG)
        self.assertGreater(len(CONTENT_POLICY_CONFIG['allowed_languages']), 0)

    def test_monitoring_config(self):
        """Test monitoring configuration"""
        self.assertIn('metrics_enabled', MONITORING_CONFIG)
        self.assertIn('log_level', MONITORING_CONFIG)
        self.assertIn('alert_thresholds', MONITORING_CONFIG)

    def test_cost_optimization_config(self):
        """Test cost optimization configuration"""
        self.assertIn('cache_enabled', COST_OPTIMIZATION_CONFIG)
        self.assertIn('batch_size', COST_OPTIMIZATION_CONFIG)
        self.assertIn('token_buffer', COST_OPTIMIZATION_CONFIG)

class SignalTests(TestCase):
    """Test cases for AI integration signals"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test model
        self.model = AIModel.objects.create(
            name='Test Model',
            description='Test Description',
            version='1.0'
        )

    def test_concurrent_requests_signal(self):
        """Test concurrent requests signal"""
        # Create task
        task = AITask.objects.create(
            model=self.model,
            user=self.user,
            status='processing'
        )

        # Check concurrent requests increment
        concurrent_key = f'ai:concurrent:{self.user.id}'
        self.assertEqual(cache.get(concurrent_key), 1)

        # Complete task
        task.status = 'completed'
        task.save()

        # Check concurrent requests decrement
        self.assertEqual(cache.get(concurrent_key), 0)

    @patch('ai_integration.signals.statsd')
    def test_task_metrics_signal(self, mock_statsd):
        """Test task metrics signal"""
        # Create and complete task
        task = AITask.objects.create(
            model=self.model,
            user=self.user,
            status='completed'
        )

        # Check metrics recording
        mock_statsd.increment.assert_called_with(
            'ai.tasks.completed',
            tags=[f'model:{self.model.name}']
        )

        # Create and fail task
        task = AITask.objects.create(
            model=self.model,
            user=self.user,
            status='failed'
        )

        # Check metrics recording
        mock_statsd.increment.assert_called_with(
            'ai.tasks.failed',
            tags=[f'model:{self.model.name}']
        )

    def test_model_cache_signal(self):
        """Test model cache signal"""
        # Set cache
        cache_key = f'ai:model:{self.model.id}'
        cache.set(cache_key, 'test_data')

        # Update model
        self.model.description = 'Updated Description'
        self.model.save()

        # Check cache cleared
        self.assertIsNone(cache.get(cache_key))

    def test_task_cache_signal(self):
        """Test task cache signal"""
        # Create task
        task = AITask.objects.create(
            model=self.model,
            user=self.user,
            status='completed'
        )

        # Set cache
        cache_key = f'ai:task:{task.id}'
        cache.set(cache_key, 'test_data')

        # Delete task
        task.delete()

        # Check cache cleared
        self.assertIsNone(cache.get(cache_key))

    def test_signal_registration(self):
        """Test signal registration"""
        # Check post_save signals
        registered_save_receivers = [r[1]() for r in post_save.receivers]
        self.assertIn(update_concurrent_requests, registered_save_receivers)
        self.assertIn(update_task_metrics, registered_save_receivers)
        self.assertIn(clear_model_cache, registered_save_receivers)

        # Check post_delete signals
        registered_delete_receivers = [r[1]() for r in post_delete.receivers]
        self.assertIn(clear_task_cache, registered_delete_receivers)
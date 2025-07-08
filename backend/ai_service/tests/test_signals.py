from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import MagicMock

from backend.ai_service.signals import _calculate_cost, log_ai_usage_receiver
from backend.ai_service.models import AIUsageLog

User = get_user_model()

class TestAISignals(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    @override_settings(DEEPSEEK_PRICING={"prompt": 0.001, "completion": 0.002})
    def test_calculate_cost(self):
        """
        Tests the _calculate_cost function with sample token counts.
        """
        # Test case 1: Standard calculation
        cost = _calculate_cost(prompt_tokens=1000, completion_tokens=2000)
        expected_cost = Decimal('0.005')
        self.assertEqual(cost, expected_cost)

        # Test case 2: Zero tokens
        cost = _calculate_cost(prompt_tokens=0, completion_tokens=0)
        self.assertEqual(cost, Decimal('0.0'))

        # Test case 3: Small token count
        cost = _calculate_cost(prompt_tokens=500, completion_tokens=0)
        self.assertEqual(cost, Decimal('0.0005'))

        # Test case 4: Only completion tokens
        cost = _calculate_cost(prompt_tokens=0, completion_tokens=100)
        self.assertEqual(cost, Decimal('0.0002'))

    def test_log_ai_usage_receiver(self):
        """
        Tests that the log_ai_usage_receiver correctly creates an AIUsageLog entry.
        """
        self.assertEqual(AIUsageLog.objects.count(), 0)

        # Mock the sender and signal arguments
        sender = MagicMock()
        log_ai_usage_receiver(
            sender=sender,
            user=self.user,
            request_type='content_generation',
            usage_data={
                'prompt_tokens': 150,
                'completion_tokens': 350,
                'total_tokens': 500
            },
            response_time_ms=1234
        )

        self.assertEqual(AIUsageLog.objects.count(), 1)
        log_entry = AIUsageLog.objects.first()
        self.assertEqual(log_entry.user, self.user)
        self.assertEqual(log_entry.request_type, 'content_generation')
        self.assertEqual(log_entry.prompt_tokens, 150)
        self.assertEqual(log_entry.completion_tokens, 350)
        self.assertEqual(log_entry.total_tokens, 500)
        self.assertEqual(log_entry.response_time_ms, 1234)
        
        # Verify the cost was calculated and stored
        expected_cost = _calculate_cost(150, 350)
        self.assertAlmostEqual(log_entry.cost, expected_cost, places=6) 

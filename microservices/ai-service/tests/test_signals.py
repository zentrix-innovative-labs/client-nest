# microservices/ai-service/tests/test_signals.py
"""
Unit tests for content_generation signals module
Tests the _calculate_cost function with various scenarios
"""

import unittest
import decimal
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.conf import settings
import os

# Import the function to test
from content_generation.signals import _calculate_cost


class TestCalculateCost(TestCase):
    """Test cases for the _calculate_cost function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_pricing = {
            'prompt': '0.001',      # $0.001 per 1K prompt tokens
            'completion': '0.002'    # $0.002 per 1K completion tokens
        }
        self.mock_pricing_patch = patch('content_generation.signals.settings.DEEPSEEK_PRICING')
        self.mock_pricing_mock = self.mock_pricing_patch.start()
        self.mock_pricing_mock.__getitem__.side_effect = self.mock_pricing.__getitem__

    def tearDown(self):
        self.mock_pricing_patch.stop()
    
    def test_calculate_cost_normal_usage(self):
        """Test normal token usage scenarios"""
        cost = _calculate_cost(prompt_tokens=1000, completion_tokens=2000)
        expected = decimal.Decimal('0.001') + decimal.Decimal('0.004')  # 0.001 + 0.004
        self.assertEqual(cost, expected)
        
        # Test case 2: Different token counts
        cost = _calculate_cost(prompt_tokens=500, completion_tokens=1500)
        expected = decimal.Decimal('0.0005') + decimal.Decimal('0.003')  # 0.0005 + 0.003
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_zero_tokens(self):
        """Test edge case with zero tokens"""
        
        # Test zero tokens
        cost = _calculate_cost(prompt_tokens=0, completion_tokens=0)
        expected = decimal.Decimal('0')
        self.assertEqual(cost, expected)
        
        # Test zero prompt tokens only
        cost = _calculate_cost(prompt_tokens=0, completion_tokens=1000)
        expected = decimal.Decimal('0.002')
        self.assertEqual(cost, expected)
        
        # Test zero completion tokens only
        cost = _calculate_cost(prompt_tokens=1000, completion_tokens=0)
        expected = decimal.Decimal('0.001')
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_small_token_counts(self):
        """Test with very small token counts"""
        
        # Test single tokens
        cost = _calculate_cost(prompt_tokens=1, completion_tokens=1)
        expected = decimal.Decimal('0.000001') + decimal.Decimal('0.000002')
        self.assertEqual(cost, expected)
        
        # Test small token counts
        cost = _calculate_cost(prompt_tokens=100, completion_tokens=50)
        expected = decimal.Decimal('0.0001') + decimal.Decimal('0.0001')
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_large_token_counts(self):
        """Test with large token counts"""
        
        # Test large token counts
        cost = _calculate_cost(prompt_tokens=10000, completion_tokens=5000)
        expected = decimal.Decimal('0.01') + decimal.Decimal('0.01')
        self.assertEqual(cost, expected)
        
        # Test very large token counts
        cost = _calculate_cost(prompt_tokens=100000, completion_tokens=200000)
        expected = decimal.Decimal('0.1') + decimal.Decimal('0.4')
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_decimal_precision(self):
        """Test decimal precision handling"""
        
        # Test that calculations maintain precision
        cost = _calculate_cost(prompt_tokens=333, completion_tokens=667)
        # 333/1000 * 0.001 + 667/1000 * 0.002 = 0.000333 + 0.001334 = 0.001667
        expected = decimal.Decimal('0.001667')
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_different_pricing(self):
        """Test with different pricing models"""
        # Test with different pricing
        different_pricing = {
            'prompt': '0.0005',     # $0.0005 per 1K prompt tokens
            'completion': '0.0015'   # $0.0015 per 1K completion tokens
        }
        self.mock_pricing_mock.__getitem__.side_effect = different_pricing.__getitem__
        
        cost = _calculate_cost(prompt_tokens=1000, completion_tokens=1000)
        expected = decimal.Decimal('0.0005') + decimal.Decimal('0.0015')
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_input_validation(self):
        """Test input validation"""
        # Test with negative tokens (should raise ValueError)
        with self.assertRaises(ValueError):
            _calculate_cost(prompt_tokens=-100, completion_tokens=100)
        
        with self.assertRaises(ValueError):
            _calculate_cost(prompt_tokens=100, completion_tokens=-100)
        
        # Test with non-integer inputs (should raise TypeError)
        with self.assertRaises(TypeError):
            _calculate_cost(prompt_tokens="100", completion_tokens=100)
        
        with self.assertRaises(TypeError):
            _calculate_cost(prompt_tokens=100, completion_tokens="100")
    
    def test_calculate_cost_rounding_behavior(self):
        """Test rounding behavior with decimal precision"""
        
        # Test that rounding follows decimal precision settings
        cost = _calculate_cost(prompt_tokens=1234, completion_tokens=5678)
        # This should be rounded according to the DECIMAL_PRECISION setting
        self.assertIsInstance(cost, decimal.Decimal)
        self.assertGreater(cost, 0)
    
    @override_settings(DEEPSEEK_API_KEY='dummy-key')
    def test_calculate_cost_thread_safety(self):
        """Test that the function is thread-safe with decimal context"""
        import threading
        import queue
        results = queue.Queue()
        def calculate_cost_thread():
            try:
                cost = _calculate_cost(prompt_tokens=1000, completion_tokens=2000)
                results.put(('success', cost))
            except Exception as e:
                results.put(('error', str(e)))
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=calculate_cost_thread)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for _ in range(5):
            status, result = results.get()
            assert status == 'success', f"Thread failed with error: {result}"
            assert isinstance(result, decimal.Decimal)


if __name__ == '__main__':
    unittest.main() 
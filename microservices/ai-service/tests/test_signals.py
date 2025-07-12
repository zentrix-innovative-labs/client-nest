# microservices/ai-service/tests/test_signals.py
"""
Unit tests for content_generation signals module
Tests the _calculate_cost function with various scenarios
"""

import unittest
import decimal
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings

# Import the function to test
from content_generation.signals import _calculate_cost


class TestCalculateCost(TestCase):
    """Test cases for the _calculate_cost function"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the pricing settings for consistent testing
        self.mock_pricing = {
            'prompt': '0.001',      # $0.001 per 1K prompt tokens
            'completion': '0.002'    # $0.002 per 1K completion tokens
        }
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_normal_usage(self, mock_pricing):
        """Test normal token usage scenarios"""
        mock_pricing.__getitem__.side_effect = self.mock_pricing.__getitem__
        
        # Test case 1: Normal usage
        cost = _calculate_cost(prompt_tokens=1000, completion_tokens=2000)
        expected = decimal.Decimal('0.001') + decimal.Decimal('0.004')  # 0.001 + 0.004
        self.assertEqual(cost, expected)
        
        # Test case 2: Different token counts
        cost = _calculate_cost(prompt_tokens=500, completion_tokens=1500)
        expected = decimal.Decimal('0.0005') + decimal.Decimal('0.003')  # 0.0005 + 0.003
        self.assertEqual(cost, expected)
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_zero_tokens(self, mock_pricing):
        """Test edge case with zero tokens"""
        mock_pricing.__getitem__.side_effect = self.mock_pricing.__getitem__
        
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
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_small_token_counts(self, mock_pricing):
        """Test with very small token counts"""
        mock_pricing.__getitem__.side_effect = self.mock_pricing.__getitem__
        
        # Test single tokens
        cost = _calculate_cost(prompt_tokens=1, completion_tokens=1)
        expected = decimal.Decimal('0.000001') + decimal.Decimal('0.000002')
        self.assertEqual(cost, expected)
        
        # Test small token counts
        cost = _calculate_cost(prompt_tokens=100, completion_tokens=50)
        expected = decimal.Decimal('0.0001') + decimal.Decimal('0.0001')
        self.assertEqual(cost, expected)
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_large_token_counts(self, mock_pricing):
        """Test with large token counts"""
        mock_pricing.__getitem__.side_effect = self.mock_pricing.__getitem__
        
        # Test large token counts
        cost = _calculate_cost(prompt_tokens=10000, completion_tokens=5000)
        expected = decimal.Decimal('0.01') + decimal.Decimal('0.01')
        self.assertEqual(cost, expected)
        
        # Test very large token counts
        cost = _calculate_cost(prompt_tokens=100000, completion_tokens=200000)
        expected = decimal.Decimal('0.1') + decimal.Decimal('0.4')
        self.assertEqual(cost, expected)
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_decimal_precision(self, mock_pricing):
        """Test decimal precision handling"""
        mock_pricing.__getitem__.side_effect = self.mock_pricing.__getitem__
        
        # Test that calculations maintain precision
        cost = _calculate_cost(prompt_tokens=333, completion_tokens=667)
        # 333/1000 * 0.001 + 667/1000 * 0.002 = 0.000333 + 0.001334 = 0.001667
        expected = decimal.Decimal('0.001667')
        self.assertEqual(cost, expected)
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_different_pricing(self, mock_pricing):
        """Test with different pricing models"""
        # Test with different pricing
        different_pricing = {
            'prompt': '0.0005',     # $0.0005 per 1K prompt tokens
            'completion': '0.0015'   # $0.0015 per 1K completion tokens
        }
        mock_pricing.__getitem__.side_effect = different_pricing.__getitem__
        
        cost = _calculate_cost(prompt_tokens=1000, completion_tokens=1000)
        expected = decimal.Decimal('0.0005') + decimal.Decimal('0.0015')
        self.assertEqual(cost, expected)
    
    def test_calculate_cost_input_validation(self):
        """Test input validation"""
        # Test with negative tokens (should handle gracefully)
        with self.assertRaises(TypeError):
            _calculate_cost(prompt_tokens=-100, completion_tokens=100)
        
        # Test with non-integer inputs
        with self.assertRaises(TypeError):
            _calculate_cost(prompt_tokens="100", completion_tokens=100)
        
        with self.assertRaises(TypeError):
            _calculate_cost(prompt_tokens=100, completion_tokens="100")
    
    @patch('content_generation.signals.settings.DEEPSEEK_PRICING')
    def test_calculate_cost_rounding_behavior(self, mock_pricing):
        """Test rounding behavior with decimal precision"""
        mock_pricing.__getitem__.side_effect = self.mock_pricing.__getitem__
        
        # Test that rounding follows decimal precision settings
        cost = _calculate_cost(prompt_tokens=1234, completion_tokens=5678)
        # This should be rounded according to the DECIMAL_PRECISION setting
        self.assertIsInstance(cost, decimal.Decimal)
        self.assertGreater(cost, 0)
    
    def test_calculate_cost_thread_safety(self):
        """Test that the function is thread-safe with decimal context"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def calculate_cost_thread():
            """Thread function to calculate cost"""
            try:
                cost = _calculate_cost(prompt_tokens=1000, completion_tokens=2000)
                results.put(('success', cost))
            except Exception as e:
                results.put(('error', str(e)))
        
        # Run multiple threads simultaneously
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=calculate_cost_thread)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all threads completed successfully
        for _ in range(5):
            status, result = results.get()
            self.assertEqual(status, 'success')
            self.assertIsInstance(result, decimal.Decimal)


if __name__ == '__main__':
    unittest.main() 
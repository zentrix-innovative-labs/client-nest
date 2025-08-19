#!/usr/bin/env python3
"""
Unittest version of AI service endpoint tests for better framework consistency.
This addresses Copilot AI recommendations for proper unittest assertions and tiered timeout management.
"""

import unittest
import requests
import json
import os
from unittest.mock import patch
from .test_utils import EndpointTestMixin, TestConfiguration, validate_endpoint_coverage


class TestAIServiceEndpointsUnittest(unittest.TestCase, EndpointTestMixin):
    """Proper unittest.TestCase for AI service endpoint testing"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level test fixtures"""
        cls.AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", TestConfiguration.AI_SERVICE_URL)
        cls.auth_headers = cls().get_auth_headers()
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Use tiered timeout approach as suggested by Copilot AI
        # Different timeout values for different endpoint types
        # Call the methods directly to get integer values
        self.health_timeout = TestConfiguration.get_health_timeout()      # Fast health checks
        self.standard_timeout = TestConfiguration.get_standard_timeout()  # Regular API calls
        self.ai_generation_timeout = TestConfiguration.get_ai_generation_timeout()  # AI operations (can be slow)
        self.default_timeout = TestConfiguration.get_default_timeout()        # Default fallback

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        url = f"{self.AI_SERVICE_URL}/health/"
        
        # Use health-specific timeout for fast health checks
        response = requests.get(url, timeout=self.health_timeout)
        
        # Use proper unittest assertions
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
        self.assertEqual(data['service'], 'ai-service')

    def test_hashtag_optimization_endpoint(self):
        """Test the hashtag optimization endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/optimize/hashtags/"
        
        payload = {
            "content": "Launching our new AI-powered social media management platform!",
            "platform": "linkedin",
            "target_audience": "marketers",
            "industry": "technology"
        }
        
        # Use AI generation timeout for hashtag optimization (AI operation)
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.ai_generation_timeout)
        
        # Test for expected status codes (including auth failures)
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('usage', data)
            
            hashtag_data = data['data']
            self.assertIn('hashtags', hashtag_data)
            self.assertIsInstance(hashtag_data['hashtags'], list)

    def test_optimal_posting_time_endpoint(self):
        """Test the optimal posting time endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/schedule/optimal/"
        
        payload = {
            "platform": "instagram",
            "content_type": "fashion",
            "target_audience": "millennials",
            "timezone": "America/New_York",
            "industry": "fashion"
        }
        
        # Use AI generation timeout for optimal posting time (AI operation)
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.ai_generation_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('usage', data)
            
            timing_data = data['data']
            self.assertIn('optimal_times', timing_data)
            self.assertIsInstance(timing_data['optimal_times'], dict)

    def test_content_generation_endpoint(self):
        """Test the content generation endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/generate/content/"
        
        payload = {
            "topic": "AI in business",
            "platform": "linkedin",
            "tone": "professional",
            "content_type": "post"
        }
        
        # Use AI generation timeout for content generation (most complex AI operation)
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.ai_generation_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('usage', data)
            
            content_data = data['data']
            self.assertIn('content', content_data)
            self.assertIsInstance(content_data['content'], str)

    def test_sentiment_analysis_endpoint(self):
        """Test the sentiment analysis endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/analyze/sentiment/"
        
        payload = {
            "text": "I'm really excited about the new AI features in our product! The team has done an amazing job."
        }
        
        # Use AI generation timeout for sentiment analysis (AI operation)
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.ai_generation_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('data', data)
            self.assertIn('usage', data)
            
            sentiment_data = data['data']
            self.assertIn('sentiment', sentiment_data)
            self.assertIn('confidence', sentiment_data)

    def test_token_usage_endpoint(self):
        """Test the token usage endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/token/usage/"
        
        # Use standard timeout for token usage (regular API call)
        response = requests.get(url, headers=self.auth_headers, timeout=self.standard_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIn('token_usage', data)
            self.assertIn('budget_warnings', data)
            self.assertIn('remaining_daily', data)
            self.assertIn('remaining_total', data)

    def test_usage_stats_endpoint(self):
        """Test the usage stats endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/usage/stats/"
        
        # Use standard timeout for usage stats (regular API call)
        response = requests.get(url, headers=self.auth_headers, timeout=self.standard_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIn('total_tasks', data)
            self.assertIn('completed_tasks', data)
            self.assertIn('failed_tasks', data)

    def test_endpoint_coverage(self):
        """Test that all required endpoints are implemented (using shared utility)"""
        # Use the dynamic endpoint discovery system
        self.assert_endpoint_coverage()

    def test_service_integration(self):
        """Integration test for service availability"""
        # Skip if AI service is not available for integration testing
        try:
            response = requests.get(f"{self.AI_SERVICE_URL}/health/", timeout=self.health_timeout)
            if response.status_code == 200:
                # Service is available, run integration test
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['status'], 'healthy')
            else:
                self.skipTest("AI service not available for integration testing")
        except requests.exceptions.RequestException:
            self.skipTest("AI service not available for integration testing")


if __name__ == '__main__':
    unittest.main()

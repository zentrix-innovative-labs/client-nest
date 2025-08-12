#!/usr/bin/env python3
"""
Unittest version of AI service endpoint tests for better framework consistency.
This addresses Copilot AI recommendations for proper unittest assertions.
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
        self.timeout = TestConfiguration.API_TIMEOUT  # Reduced from 60 to 10 seconds
        self.short_timeout = TestConfiguration.HEALTH_TIMEOUT  # Reduced to 5 seconds

    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        url = f"{self.AI_SERVICE_URL}/health/"
        
        response = requests.get(url, timeout=self.short_timeout)
        
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
        
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.timeout)
        
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
        
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.timeout)
        
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
        
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Content generation can return different structures
            if 'error' in data:
                self.assertIn('raw_content', data)
            elif 'content' in data:
                self.assertIsInstance(data['content'], str)
                if 'hashtags' in data:
                    self.assertIsInstance(data['hashtags'], list)
            else:
                self.fail("Response missing required content field")

    def test_sentiment_analysis_endpoint(self):
        """Test the sentiment analysis endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/analyze/sentiment/"
        
        payload = {
            "text": "I'm really excited about the new AI features in our product! The team has done an amazing job."
        }
        
        response = requests.post(url, json=payload, headers=self.auth_headers, timeout=self.timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            if 'error' in data:
                self.assertIn('raw_content', data)
            elif 'sentiment' in data:
                self.assertIsInstance(data['sentiment'], str)
                if 'confidence' in data:
                    self.assertIsInstance(data['confidence'], (int, float))
            else:
                self.fail("Response missing required sentiment field")

    def test_usage_stats_endpoint(self):
        """Test the usage stats endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/usage/stats/"
        
        response = requests.get(url, headers=self.auth_headers, timeout=self.short_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIsInstance(data, dict)
            self.assertIn('total_tasks', data)

    def test_token_usage_endpoint(self):
        """Test the token usage endpoint"""
        url = f"{self.AI_SERVICE_URL}/api/ai/token/usage/"
        
        response = requests.get(url, headers=self.auth_headers, timeout=self.short_timeout)
        
        # Test for expected status codes
        self.assertIn(response.status_code, [200, 201, 401, 403])
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.assertIsInstance(data, dict)
            self.assertIn('token_usage', data)

    def test_endpoint_coverage(self):
        """Test that all required endpoints are implemented (using shared utility)"""
        try:
            self.assert_endpoint_coverage()
        except AssertionError as e:
            self.fail(str(e))

    @unittest.skipIf(os.getenv('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true', 
                     "Integration tests skipped")
    def test_service_integration(self):
        """Integration test for service availability"""
        try:
            response = requests.get(f"{self.AI_SERVICE_URL}/health/", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.skipTest("AI service not available for integration testing")


if __name__ == '__main__':
    unittest.main()

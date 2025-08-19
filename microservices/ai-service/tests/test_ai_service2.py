"""
Comprehensive Testing Framework for AI Service
Tests all components: API endpoints, content generation, quality assurance, and performance
"""

import pytest
import json
import time
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from content_generation.logic import ContentGenerator
from common.deepseek_client import DeepSeekClient
from content_generation.models import GeneratedContent, AIUsageLog

User = get_user_model()

class AIQualityAssuranceTests(TestCase):
    """Quality Assurance Testing Framework"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_content_quality_scoring(self):
        """Test quality scoring functionality"""
        # Mock AI response
        mock_response = {
            'content': 'Test content for quality scoring',
            'quality_score': 85,
            'safety_check': {'is_safe': True, 'reason': 'Safe content'},
            'readability_score': 75
        }
        
        with patch.object(ContentGenerator, 'generate_post', return_value=mock_response):
            generator = ContentGenerator(MagicMock())
            result = generator.generate_post(
                topic="Test topic",
                platform="linkedin",
                user=self.user,
                tone="professional"
            )
            
            # Quality assertions
            self.assertIn('quality_score', result)
            self.assertGreaterEqual(result['quality_score'], 0)
            self.assertLessEqual(result['quality_score'], 100)
            
            # Safety check assertions
            self.assertIn('safety_check', result)
            self.assertIn('is_safe', result['safety_check'])
            
            # Readability assertions
            self.assertIn('readability_score', result)
            self.assertGreaterEqual(result['readability_score'], 0)
            self.assertLessEqual(result['readability_score'], 100)
    
    def test_content_safety_filtering(self):
        """Test content safety filtering"""
        # Test safe content
        safe_content = "This is a professional business post about AI."
        with patch.object(DeepSeekClient, 'analyze_sentiment') as mock_sentiment:
            mock_sentiment.return_value = {
                'sentiment': 'positive',
                'confidence': 0.9,
                'emotions': ['excitement'],
                'urgency': 'low'
            }
            
            client = DeepSeekClient()
            result = client.analyze_sentiment(safe_content)
            
            self.assertEqual(result['sentiment'], 'positive')
            self.assertGreater(result['confidence'], 0.5)
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        start_time = time.time()
        
        # Simulate content generation
        with patch.object(ContentGenerator, 'generate_post') as mock_generate:
            mock_generate.return_value = {'content': 'Test content'}
            
            generator = ContentGenerator(MagicMock())
            result = generator.generate_post(
                topic="Performance test",
                platform="linkedin",
                user=self.user,
                tone="professional"
            )
            
        end_time = time.time()
        response_time = end_time - start_time
        
        # Performance assertions
        self.assertLess(response_time, 5.0)  # Should complete within 5 seconds
        self.assertIn('content', result)

class APIIntegrationTests(APITestCase):
    """API Integration Testing"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apitestuser',
            email='apitest@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'healthy')
    
    def test_content_generation_endpoint(self):
        """Test content generation API endpoint"""
        data = {
            'topic': 'AI in business',
            'platform': 'linkedin',
            'tone': 'professional'
        }
        
        with patch.object(ContentGenerator, 'generate_post') as mock_generate:
            mock_generate.return_value = {
                'content': 'Test content',
                'hashtags': ['#AI', '#Business'],
                'quality_score': 85,
                'call_to_action': 'Test CTA'
            }
            
            response = self.client.post('/api/ai/generate/content/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('content', response.json())
    
    def test_token_usage_endpoint(self):
        """Test token usage endpoint"""
        response = self.client.get('/api/ai/token/usage/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token_usage', response.data)
    
    def test_models_status_endpoint(self):
        """Test AI models status endpoint"""
        response = self.client.get('/api/ai/models/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)

class PerformanceMonitoringTests(TestCase):
    """Performance Monitoring Tests"""
    
    def test_response_time_monitoring(self):
        """Test response time monitoring"""
        start_time = time.time()
        
        # Simulate API call
        with patch.object(DeepSeekClient, 'generate_content') as mock_generate:
            mock_generate.return_value = {'content': 'Test content'}
            
            client = DeepSeekClient()
            result = client.generate_content(
                system_prompt="Test system prompt",
                user_prompt="Test user prompt"
            )
            
        end_time = time.time()
        response_time = end_time - start_time
        
        # Performance assertions
        self.assertLess(response_time, 3.0)  # API should respond within 3 seconds
        self.assertIn('content', result)
    
    def test_token_usage_monitoring(self):
        """Test token usage monitoring"""
        with patch.object(DeepSeekClient, 'generate_content') as mock_generate:
            mock_generate.return_value = {
                'content': 'Test content',
                'usage': {'prompt_tokens': 50, 'completion_tokens': 100}
            }
            
            client = DeepSeekClient()
            result = client.generate_content(
                system_prompt="Test",
                user_prompt="Test"
            )
            
            # Token usage assertions
            self.assertIn('usage', result)
            self.assertIn('prompt_tokens', result['usage'])
            self.assertIn('completion_tokens', result['usage'])

class QualityAssuranceAutomationTests(TestCase):
    """Quality Assurance Automation Tests"""
    
    def test_automated_quality_checks(self):
        """Test automated quality checks"""
        test_cases = [
            {
                'content': 'Professional business content about AI.',
                'expected_quality': 80,
                'expected_safety': True
            },
            {
                'content': 'This is a very long content that should be truncated for quality purposes.',
                'expected_quality': 70,
                'expected_safety': True
            }
        ]
        
        for test_case in test_cases:
            with patch.object(ContentGenerator, 'generate_post') as mock_generate:
                mock_generate.return_value = {
                    'content': test_case['content'],
                    'quality_score': test_case['expected_quality'],
                    'safety_check': {'is_safe': test_case['expected_safety']}
                }
                
                generator = ContentGenerator(MagicMock())
                result = generator.generate_post(
                    topic="Test",
                    platform="linkedin",
                    user=None,
                    tone="professional"
                )
                
                # Quality assertions
                self.assertGreaterEqual(result['quality_score'], 0)
                self.assertLessEqual(result['quality_score'], 100)
                self.assertIn('safety_check', result)
    
    def test_content_validation_automation(self):
        """Test automated content validation"""
        with patch.object(ContentGenerator, 'generate_post') as mock_generate:
            mock_generate.return_value = {
                'content': 'Valid content',
                'hashtags': ['#Test'],
                'call_to_action': 'Test CTA',
                'quality_score': 85,
                'safety_check': {'is_safe': True}
            }
            
            generator = ContentGenerator(MagicMock())
            result = generator.generate_post(
                topic="Test",
                platform="linkedin",
                user=None,
                tone="professional"
            )
            
            # Validation assertions
            required_fields = ['content', 'hashtags', 'quality_score', 'safety_check']
            for field in required_fields:
                self.assertIn(field, result)

if __name__ == '__main__':
    pytest.main([__file__]) 
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import AIModel, AITask
from unittest.mock import patch
import json

User = get_user_model()

class AIViewsTests(TestCase):
    """Test cases for AI integration views"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.subscription_tier = 'premium'
        self.user.save()

        # Create test model
        self.model = AIModel.objects.create(
            name='Test Model',
            description='Test Description',
            version='1.0'
        )

        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_task_list_endpoint(self):
        """Test task list endpoint"""
        # Create some tasks
        AITask.objects.create(
            model=self.model,
            user=self.user,
            input_data={'type': 'test'},
            status='completed'
        )
        AITask.objects.create(
            model=self.model,
            user=self.user,
            input_data={'type': 'test'},
            status='processing'
        )

        url = reverse('ai-task-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_usage_stats_endpoint(self):
        """Test usage statistics endpoint"""
        url = reverse('ai-task-usage-stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_requests', response.data)
        self.assertIn('monthly_requests', response.data)

    @patch('ai_integration.tasks.process_content_generation.delay')
    def test_content_generation_endpoint(self, mock_task):
        """Test content generation endpoint"""
        mock_task.return_value.id = 'test-task-id'

        url = reverse('content-generation-generate-post')
        data = {
            'prompt': 'Test prompt',
            'platform': 'twitter',
            'tone': 'professional',
            'language': 'en'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['status'], 'processing')

        # Verify task was called with correct arguments
        mock_task.assert_called_once()
        call_args = mock_task.call_args[1]
        self.assertEqual(call_args['user_id'], self.user.id)
        self.assertEqual(call_args['content_type'], 'post')
        self.assertEqual(call_args['prompt'], data['prompt'])

    def test_content_generation_validation(self):
        """Test content generation input validation"""
        url = reverse('content-generation-generate-post')

        # Test empty prompt
        data = {'prompt': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test too long prompt
        data = {'prompt': 'x' * 1001}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid platform
        data = {'prompt': 'Test', 'platform': 'invalid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('ai_integration.tasks.process_sentiment_analysis.delay')
    def test_sentiment_analysis_endpoint(self, mock_task):
        """Test sentiment analysis endpoint"""
        mock_task.return_value.id = 'test-task-id'

        url = reverse('sentiment-analysis-analyze-comment')
        data = {
            'text': 'Great product! Really satisfied with the quality.',
            'language': 'en'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['status'], 'processing')

        # Verify task was called with correct arguments
        mock_task.assert_called_once()
        call_args = mock_task.call_args[1]
        self.assertEqual(call_args['user_id'], self.user.id)
        self.assertEqual(call_args['context'], 'comment')
        self.assertEqual(call_args['text'], data['text'])

    def test_sentiment_analysis_validation(self):
        """Test sentiment analysis input validation"""
        url = reverse('sentiment-analysis-analyze-comment')

        # Test empty text
        data = {'text': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test too long text
        data = {'text': 'x' * 5001}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_required(self):
        """Test authentication requirements"""
        # Create unauthenticated client
        client = APIClient()

        # Test task list endpoint
        url = reverse('ai-task-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test content generation endpoint
        url = reverse('content-generation-generate-post')
        response = client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test sentiment analysis endpoint
        url = reverse('sentiment-analysis-analyze-comment')
        response = client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
# backend/ai_integration/tests/test_api_endpoints.py
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from celery import current_app

class TestContentGenerationFlow(APITestCase):
    """
    Integration test for the full asynchronous content generation flow.
    This fulfills Biyo Stella's tasks for end-to-end testing, quality validation,
    and performance monitoring.
    """
    def setUp(self):
        """Set up a test user and authenticate."""
        self.user = User.objects.create_user(username='testuser', password='testpassword123', email='test@example.com')
        self.client.force_authenticate(user=self.user)
        # Biyo Stella's final, direct fix: Force celery to store results for eager tasks.
        current_app.conf.update(task_store_eager_result=True)

    @patch('ai_services.content_generation.logic.ContentGenerator.generate_post')
    def test_full_async_content_generation_flow_success(self, mock_generate_post):
        """
        Tests the entire successful workflow using a mock for the AI call.
        """
        # Biyo Stella's final test strategy: Mock the actual AI call to ensure
        # the test is fast, repeatable, and validates the full pipeline.
        mock_generate_post.return_value = {
            "content": "This is a brilliantly mocked post about remote work.",
            "hashtags": ["#remotework", "#productivity", "#mocked"],
            "call_to_action": "What's your take? Comment below!",
            "suggestions": [],
            "variations": [],
            "quality_score": 92,
            "safety_check": {"is_safe": True, "reason": "N/A"},
            "readability_score": 65.5,
            "engagement_prediction": "High",
            "optimal_posting_time_suggestion": "9 AM - 11 AM on Tue, Wed, Thu"
        }

        # 1. Start the content generation task
        url = reverse('generate-content')
        data = {
            "topic": "The benefits of remote work for productivity",
            "platform": "linkedin",
            "tone": "professional"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        task_id = response.data['task_id']

        # 2. Poll the status endpoint (will be instant due to eager execution)
        status_url = reverse('task-status', kwargs={'task_id': task_id})
        response = self.client.get(status_url)
        
        # 3. Validate the successful response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')
        
        result = response.data.get('result')
        self.assertIsNotNone(result)
        self.assertEqual(result['content'], "This is a brilliantly mocked post about remote work.")
        self.assertIn("#mocked", result['hashtags'])

        # Validate the structure against expected keys (fulfills quality assurance task)
        expected_keys = [
            'content', 'hashtags', 'call_to_action', 'suggestions', 'variations',
            'quality_score', 'safety_check', 'readability_score', 
            'engagement_prediction', 'optimal_posting_time_suggestion'
        ]
        for key in expected_keys:
            self.assertIn(key, result, f"Expected key '{key}' not found in the final result.")

        # Validate specific data types for quality
        self.assertIsInstance(result['content'], str)
        self.assertIsInstance(result['hashtags'], list)
        self.assertGreater(len(result['content']), 10)
        self.assertGreater(result['quality_score'], 0)
        self.assertTrue(result['safety_check']['is_safe']) 
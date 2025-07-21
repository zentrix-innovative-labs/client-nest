# backend/ai_integration/tests/test_api_endpoints.py
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user_service.models import User
from celery import current_app
from backend.ai_service.models import AIUsageLog

class TestContentGenerationFlow(APITestCase):
    """
    Integration test for the full asynchronous content generation flow,
    covering end-to-end testing, quality validation, and performance monitoring.
    """
    def setUp(self):
        """Set up test users and authenticate."""
        self.user = User.objects.create_user(username='testuser', password='testpassword123', email='test@example.com')
        self.other_user = User.objects.create_user(username='otheruser', password='password456', email='other@example.com')
        self.client.force_authenticate(user=self.user)
        # Force celery to execute tasks eagerly and store results for testing purposes.
        current_app.conf.update(task_store_eager_result=True, task_always_eager=True)

    @patch('ai_service.content_generation.logic.ContentGenerator.generate_post')
    def test_full_async_content_generation_flow_success(self, mock_generate_post):
        """
        Tests the entire successful workflow from task creation to successful result retrieval.
        """
        # Mock the actual AI call to ensure the test is fast, repeatable,
        # and validates the full pipeline.
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
        # Assert that an AIUsageLog entry was created for the user
        self.assertTrue(AIUsageLog.objects.filter(user=self.user).exists())

    def test_content_generation_invalid_input(self):
        """
        Tests the API's response to invalid input data (missing 'topic').
        """
        url = reverse('generate-content')
        data = {
            "platform": "linkedin",
            "tone": "professional"
            # 'topic' is intentionally missing
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('topic', response.data)
        self.assertEqual(str(response.data['topic'][0]), 'This field is required.')

    @patch('ai_service.content_generation.logic.ContentGenerator.generate_post')
    def test_content_generation_task_failure(self, mock_generate_post):
        """
        Tests the API's response when the underlying Celery task fails.
        """
        # Configure the mock to raise an exception
        mock_generate_post.side_effect = Exception("AI service is down")

        # 1. Start the content generation task
        url = reverse('generate-content')
        data = {
            "topic": "A topic that will cause a failure",
            "platform": "twitter",
            "tone": "casual"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        task_id = response.data['task_id']

        # 2. Poll the status endpoint
        status_url = reverse('task-status', kwargs={'task_id': task_id})
        response = self.client.get(status_url)
        
        # 3. Validate the failure response
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)

    @patch('ai_service.content_generation.logic.ContentGenerator.generate_post')
    def test_task_status_unauthorized_access(self, mock_generate_post):
        """
        Ensures a user cannot access the task status of a task created by another user.
        """
        # This side effect isn't strictly necessary for this test but is good practice
        mock_generate_post.return_value = {"content": "some content"}

        # 1. User 1 starts a task
        url = reverse('generate-content')
        data = {"topic": "A topic", "platform": "twitter"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        task_id = response.data['task_id']

        # 2. User 2 (other_user) tries to poll the status
        self.client.force_authenticate(user=self.other_user)
        status_url = reverse('task-status', kwargs={'task_id': task_id})
        response = self.client.get(status_url)

        # 3. Validate that access is denied
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_content_generation_invalid_ai_response(self):
        """
        Simulate an invalid AI response structure to trigger the 502 gateway branch.
        """
        # Patch the Celery task to return a malformed response
        invalid_response = {"unexpected": "structure"}
        with patch("backend.ai_service.tasks.generate_content_task.apply_async") as mock_task:
            mock_task.return_value.id = "fake-task-id"
            # Simulate the task result in the polling endpoint
            with patch("backend.ai_service.views.AsyncResult") as mock_async_result:
                mock_async_result.return_value.status = "SUCCESS"
                mock_async_result.return_value.result = invalid_response
                # Create a UserTaskMapping for the fake task
                from backend.ai_service.models import UserTaskMapping
                UserTaskMapping.objects.create(user=self.user, task_id="fake-task-id")
                response = self.client.get(f"/api/ai/task-status/fake-task-id/")
                self.assertEqual(response.status_code, 502)
                self.assertIn("error", response.data["result"])
